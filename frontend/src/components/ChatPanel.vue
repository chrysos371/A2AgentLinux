<template>
  <div class="chat-panel" @click="focusInput">
    <!-- Empty state -->
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 9v6M9 12h6"/>
        </svg>
      </div>
      <h2>A2 安全智能运维 Agent</h2>
      <p>输入运维指令，AI 将调用 MCP 工具执行操作<br/>所有操作经过三层安全护栏校验</p>
      <div class="empty-tips">
        <span v-for="t in samplePrompts" :key="t" @click="sendText(t)">{{ t }}</span>
      </div>
    </div>

    <!-- Messages -->
    <div class="messages" ref="msgBox" v-else>
      <div v-for="(m, i) in messages" :key="i" :class="['msg-row', m.role]">
        <!-- Tool call -->
        <template v-if="m.role === 'tool'">
          <div class="msg-tool">
            <span class="tool-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </span>
            <span class="tool-text">{{ m.text }}</span>
          </div>
        </template>

        <!-- Error -->
        <template v-else-if="m.role === 'error'">
          <div class="msg-error">
            <span class="err-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            </span>
            {{ m.text }}
          </div>
        </template>

        <!-- User message -->
        <template v-else-if="m.role === 'user'">
          <div class="msg-bubble user">
            <div class="msg-content" v-html="renderMarkdown(m.text)"></div>
          </div>
        </template>

        <!-- Assistant message -->
        <template v-else-if="m.role === 'assistant'">
          <div class="msg-bubble assistant">
            <div class="avatar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="msg-body">
              <div class="msg-content" v-html="renderMarkdown(m.text)"></div>
              <el-collapse v-if="m.data" class="data-collapse">
                <el-collapse-item title="查看原始数据" name="1">
                  <pre class="raw-data">{{ m.data }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Input -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          ref="inputEl"
          v-model="input"
          placeholder="输入运维指令，例如：查看服务器内存使用情况..."
          @keydown.enter="send"
          autofocus
        />
        <button
          class="send-btn"
          @click="send"
          :disabled="!wsReady"
          title="发送"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
      <span class="input-hint">Enter 发送 · 所有操作经过安全护栏校验</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'

const props = defineProps({ ws: Object })

const messages = ref([])
const input = ref('')
const msgBox = ref(null)
const inputEl = ref(null)

const wsReady = computed(() => props.ws && props.ws.readyState === WebSocket.OPEN)

const samplePrompts = [
  '查看服务器内存',
  '检查服务器安全状态',
  '查看网络连接情况',
  '服务器一键巡检',
]

function append(role, text, data) {
  messages.value.push({ role, text, data })
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/\n/g, '<br/>')
}

function send() {
  const text = input.value.trim()
  if (!text || !wsReady.value) return
  append('user', text)
  input.value = ''
  props.ws.send(text)
}

function sendText(t) {
  if (!wsReady.value) return
  append('user', t)
  props.ws.send(t)
}

function focusInput() {
  inputEl.value?.focus()
}

defineExpose({ sendText })

onMounted(() => {
  if (props.ws) {
    props.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      switch (msg.type) {
        case 'status': break
        case 'thinking': break
        case 'tool_call':
          append('tool', msg.text)
          break
        case 'answer':
          append('assistant', msg.text, msg.data || null)
          break
        case 'error':
          append('error', msg.text)
          break
        case 'warning':
          append('tool', '⚠ ' + msg.text)
          break
      }
    }
  }
})
</script>

<style scoped>
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  position: relative;
}

/* Empty state */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  text-align: center;
}

.empty-icon {
  color: var(--accent);
  opacity: 0.4;
  margin-bottom: 8px;
}

.empty-state h2 {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}

.empty-tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

.empty-tips span {
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.empty-tips span:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(0,212,255,0.06);
}

/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.msg-row {
  display: flex;
  max-width: 100%;
}

.msg-row.user {
  justify-content: flex-end;
}

.msg-row.assistant {
  justify-content: flex-start;
}

.msg-row.tool, .msg-row.error {
  justify-content: center;
}

.msg-bubble {
  max-width: 78%;
  display: flex;
  gap: 10px;
}

.msg-bubble.user .msg-content {
  background: linear-gradient(135deg, #1a3a5c, #1e3660);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: var(--radius) 4px var(--radius) var(--radius);
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}

.msg-bubble.assistant {
  max-width: 85%;
}

.avatar {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 8px;
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
}

.msg-body {
  flex: 1;
  min-width: 0;
}

.msg-bubble.assistant .msg-content {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px var(--radius) var(--radius) var(--radius);
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-primary);
}

.msg-content :deep(strong) {
  color: var(--accent);
  font-weight: 600;
}

.msg-content :deep(code) {
  font-family: var(--font-mono);
  font-size: 12px;
  background: rgba(0,212,255,0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--accent);
}

.msg-content :deep(pre) {
  background: var(--bg-deep);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  color: var(--text-secondary);
}

.msg-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

/* Tool message */
.msg-tool {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(124,92,252,0.08);
  border: 1px solid rgba(124,92,252,0.15);
  border-radius: 16px;
  font-size: 11px;
  color: var(--accent2);
}

.tool-icon { display: flex; align-items: center; opacity: 0.7; }

/* Error message */
.msg-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255,61,90,0.08);
  border: 1px solid rgba(255,61,90,0.15);
  border-radius: 16px;
  font-size: 11px;
  color: var(--danger);
}

.err-icon { display: flex; align-items: center; }

/* Data collapse */
.data-collapse {
  margin-top: 8px;
}

.data-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 11px;
  color: var(--text-muted);
  height: 32px;
  line-height: 32px;
}

.data-collapse :deep(.el-collapse-item__wrap) {
  background: transparent;
  border: none;
}

.raw-data {
  background: var(--bg-deep);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.5;
  max-height: 160px;
  overflow: auto;
  color: var(--text-muted);
  white-space: pre-wrap;
}

/* Input area */
.input-area {
  padding: 16px 24px 20px;
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
  transition: var(--transition);
}

.input-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(0,212,255,0.08);
}

.input-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  padding: 10px 14px;
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--text-primary);
}

.input-wrapper input::placeholder {
  color: var(--text-muted);
}

.send-btn {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.input-hint {
  display: block;
  text-align: center;
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 6px;
}
</style>
