<template>
  <div class="app">
    <Sidebar
      :api-key="apiKey"
      :tool-count="toolCount"
      :ai-ready="aiReady"
      @set-key="setApiKey"
    />
    <div class="main">
      <StatusBar :mcp-on="mcpOn" :ai-ready="aiReady" />
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
  } catch (e) {}
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.app { display: flex; height: 100vh; background: #1a1a2e; color: #eee; font-family: 'Microsoft YaHei', sans-serif; }
.main { flex: 1; display: flex; flex-direction: column; }
</style>
