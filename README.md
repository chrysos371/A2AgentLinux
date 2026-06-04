# A2-AgentLinux

面向麒麟操作系统的安全智能运维 Agent — 第15届"中国软件杯"A2赛题

## 项目结构

```
A2-AgentLinux/
├── backend/
│   ├── app.py                        # FastAPI 主入口 (WebSocket + 安全护栏)
│   ├── mcp_server/                   # MCP Server (基于 ops-mcp-server)
│   │   ├── server.py                 # SSE 模式 MCP Server
│   │   ├── core/                     # SSH 管理器 + 巡检引擎
│   │   ├── tools/                    # 18个运维工具
│   │   ├── config/                   # 日志配置
│   │   ├── models/                   # 数据模型
│   │   └── utils/                    # 装饰器工具
│   ├── guardrail/                    # 安全护栏 (NEW)
│   │   ├── intent_filter.py          # 意图风险过滤
│   │   ├── command_validator.py      # 命令安全校验
│   │   └── injection_detector.py     # Prompt Injection 检测
│   ├── audit/                        # 审计日志 (NEW)
│   │   └── logger.py                 # 思维链审计
│   └── requirements.txt
├── frontend/                         # Vue 3 + Element Plus
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── components/
│   │       ├── ChatPanel.vue         # 对话面板
│   │       ├── Sidebar.vue           # 侧边栏 (API Key)
│   │       └── StatusBar.vue         # 状态栏
│   ├── package.json
│   └── vite.config.js
├── deploy/
│   ├── Dockerfile
│   └── docker-compose.yml
└── docs/
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt

# 启动 MCP Server (SSE 模式)
python -m mcp_server.server --port 8000 &

# 启动 Web 后端
uvicorn app:app --host 0.0.0.0 --port 8080
```

### 前端

```bash
cd frontend
npm install
npm run dev        # 开发
npm run build      # 生产构建
```

### 部署到龙芯/麒麟

```bash
# 1. 在本地完成开发后推送到 GitHub
git add . && git commit -m "update" && git push

# 2. 在龙芯虚拟机上拉取
git clone https://github.com/xyls999/A2-AgentLinux.git
cd A2-AgentLinux/backend
pip install -r requirements.txt
python -m mcp_server.server --port 8000 &
uvicorn app:app --host 0.0.0.0 --port 8080
```

## 技术栈

- **后端**: Python 3.10+ / FastAPI / MCP SDK
- **AI**: DeepSeek API (Function Calling)
- **前端**: Vue 3 + Element Plus + Vite
- **安全**: 三层护栏 (注入检测 → 意图过滤 → 命令校验)
- **审计**: JSONL 思维链日志

## 安全护栏架构

```
用户输入 → [1. Prompt Injection 检测] → [2. 意图风险过滤]
         → LLM 推理 → [3. 命令参数校验] → 执行 → 审计日志
```
