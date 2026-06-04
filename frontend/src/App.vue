<template>
  <div class="app-shell">
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>

    <Sidebar
      :api-key="apiKey"
      :tool-count="toolCount"
      :ai-ready="aiReady"
      :mcp-on="mcpOn"
      @set-key="setApiKey"
    />

    <div class="main-area">
      <StatusBar :mcp-on="mcpOn" :ai-ready="aiReady" :tool-count="toolCount" />
      <ChatPanel ref="chatPanel" :ws="ws" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import StatusBar from './components/StatusBar.vue'
import ChatPanel from './components/ChatPanel.vue'

const apiKey = ref('')
const toolCount = ref(0)
const aiReady = ref(false)
const mcpOn = ref(false)
let ws = null

function connect() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${location.host}/chat`)
  ws.onopen = () => { mcpOn.value = true }
  ws.onclose = () => { mcpOn.value = false; setTimeout(connect, 3000) }
  ws.onerror = () => { mcpOn.value = false }
}

function setApiKey(key) {
  apiKey.value = key
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(`__apikey:${key}`)
    aiReady.value = true
  }
}

onMounted(async () => {
  connect()
  try {
    const r = await fetch('/api/tools')
    const tools = await r.json()
    toolCount.value = tools.length
  } catch (e) { /* MCP not connected yet */ }
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg-deep: #060b1a;
  --bg-primary: #0a1030;
  --bg-card: #111640;
  --bg-card-hover: #161d52;
  --border: #1e2a5a;
  --accent: #00d4ff;
  --accent2: #7c5cfc;
  --success: #00e676;
  --danger: #ff3d5a;
  --warning: #ffab40;
  --text-primary: #e8eaf0;
  --text-secondary: #8892aa;
  --text-muted: #5a6380;
  --radius-sm: 8px;
  --radius: 12px;
  --radius-lg: 16px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --font-sans: 'Inter', 'Microsoft YaHei', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

body {
  font-family: var(--font-sans);
  background: var(--bg-deep);
  color: var(--text-primary);
  overflow: hidden;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.app-shell {
  display: flex;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

.bg-glow {
  position: fixed;
  top: -200px;
  right: -200px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  min-width: 0;
}
</style>
