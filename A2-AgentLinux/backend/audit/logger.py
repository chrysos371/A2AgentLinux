"""思维链审计日志 — 记录完整推理链路，支持异常回溯"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path(__file__).parent.parent.parent / "audit_logs"
LOG_DIR.mkdir(exist_ok=True)


def _log_file() -> Path:
    return LOG_DIR / f"audit-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"


def log_event(event_type: str, **kwargs):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **kwargs,
    }
    with open(_log_file(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_user_input(text: str, injection_result: dict):
    log_event("user_input", text=text[:500], injection_check=injection_result)


def log_intent_check(text: str, result: dict):
    log_event("intent_check", text=text[:200], intent_result=result)


def log_tool_call(tool_name: str, args: dict, validation: dict | None = None):
    log_event("tool_call", tool=tool_name, args=args, validation=validation)


def log_tool_result(tool_name: str, success: bool, output_preview: str = ""):
    log_event("tool_result", tool=tool_name, success=success, preview=output_preview[:500])


def log_llm_response(response: str, tool_calls: list | None = None):
    log_event("llm_response", preview=response[:300], has_tool_calls=bool(tool_calls))


def log_error(error: str, context: dict | None = None):
    log_event("error", error=error, context=context or {})
