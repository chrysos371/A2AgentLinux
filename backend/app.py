import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from openai import OpenAI

from guardrail.intent_filter import filter_intent
from guardrail.command_validator import validate_command
from guardrail.injection_detector import detect_injection
from audit.logger import (
    log_user_input, log_intent_check, log_tool_call,
    log_tool_result, log_llm_response, log_error,
)

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/sse")
TOOLS_CACHE_FILE = Path(__file__).parent / "tools_cache.json"

mcp_session: ClientSession | None = None
mcp_tools: list[dict] = []
deepseek_client: OpenAI | None = None


async def connect_mcp():
    global mcp_session, mcp_tools
    try:
        read, write = await sse_client(MCP_URL).__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()

        result = await session.list_tools()
        mcp_tools = []
        for tool in result.tools:
            mcp_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": (
                        json.loads(tool.inputSchema) if hasattr(tool, "inputSchema") and tool.inputSchema
                        else {"type": "object", "properties": {}}
                    ),
                },
            })
        with open(TOOLS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(mcp_tools, f, ensure_ascii=False, indent=2)

        mcp_session = session
        print(f"[OK] MCP connected, {len(mcp_tools)} tools loaded")
    except Exception as e:
        print(f"[WARN] MCP connection failed: {e}")
        if TOOLS_CACHE_FILE.exists():
            with open(TOOLS_CACHE_FILE, encoding="utf-8") as f:
                mcp_tools = json.load(f)
            print(f"[OK] Loaded {len(mcp_tools)} tools from cache")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mcp()
    yield


app = FastAPI(lifespan=lifespan)

frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")


@app.get("/api/tools")
async def get_tools():
    return mcp_tools


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>Frontend not built. Run: cd frontend && npm run build</h1>"


@app.websocket("/chat")
async def chat(ws: WebSocket):
    global deepseek_client
    await ws.accept()

    while True:
        try:
            user_msg = await ws.receive_text()

            if user_msg.startswith("__apikey:"):
                key = user_msg.split(":", 1)[1].strip()
                deepseek_client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
                await ws.send_json({"type": "status", "text": "DeepSeek API Key 已设置"})
                continue

            if not deepseek_client:
                await ws.send_json({
                    "type": "ask_key",
                    "text": "请先设置 DeepSeek API Key"
                })
                continue

            # === 安全护栏第1层: Prompt Injection 检测 ===
            injection_result = detect_injection(user_msg)
            log_user_input(user_msg, injection_result)
            if injection_result["blocked"]:
                await ws.send_json({
                    "type": "error",
                    "text": f"检测到注入攻击 (score={injection_result['score']}): "
                           + "; ".join(injection_result["matches"])
                })
                continue

            # === 安全护栏第2层: 意图风险过滤 ===
            intent_result = filter_intent(user_msg)
            log_intent_check(user_msg, intent_result)
            if not intent_result["allowed"]:
                await ws.send_json({
                    "type": "error",
                    "text": f"操作被安全策略拒绝: {intent_result['reason']}"
                })
                continue
            if intent_result["require_confirmation"]:
                await ws.send_json({
                    "type": "warning",
                    "text": f"该操作需要二次确认: {intent_result['reason']}",
                    "need_confirm": True,
                })

            await ws.send_json({"type": "thinking", "text": "分析中..."})

            messages = [
                {"role": "system", "content": "你是一个运维助手。用户会提问运维相关问题，你可以调用工具来获取信息。用中文回答。回答要简洁。"},
                {"role": "user", "content": user_msg},
            ]

            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=mcp_tools if mcp_tools else None,
                stream=False,
            )

            choice = response.choices[0]
            msg = choice.message

            if msg.tool_calls and mcp_session:
                tool_call = msg.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # === 安全护栏第3层: 命令参数校验 ===
                validation = validate_command(json.dumps(tool_args, ensure_ascii=False))
                log_tool_call(tool_name, tool_args, {
                    "allowed": validation.allowed,
                    "reason": validation.reason,
                })

                if not validation.allowed:
                    await ws.send_json({
                        "type": "error",
                        "text": f"命令校验不通过: {validation.reason}"
                    })
                    continue

                await ws.send_json({
                    "type": "tool_call",
                    "text": f"调用工具: {tool_name}({json.dumps(tool_args, ensure_ascii=False)})"
                })

                try:
                    result = await mcp_session.call_tool(tool_name, tool_args)
                    tool_output = ""
                    for c in result.content:
                        if hasattr(c, "text"):
                            tool_output += c.text
                    parsed = tool_output[:3000]
                    log_tool_result(tool_name, True, parsed)
                except Exception as e:
                    parsed = f"工具调用失败: {e}"
                    log_tool_result(tool_name, False, str(e))

                messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": parsed})

                await ws.send_json({"type": "thinking", "text": "整理结果中..."})

                response2 = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=False,
                )
                final = response2.choices[0].message.content or ""
                log_llm_response(final)
                await ws.send_json({"type": "answer", "text": final, "data": parsed})

            else:
                log_llm_response(msg.content or "")
                await ws.send_json({"type": "answer", "text": msg.content or "", "data": None})

        except WebSocketDisconnect:
            break
        except Exception as e:
            log_error(str(e))
            await ws.send_json({"type": "error", "text": str(e)})
