<template>
  <div class="chat-panel">
    <div class="messages" ref="msgBox">
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <span v-if="m.role === 'tool'" style="color:#e94560">&#x1F527; {{ m.text }}</span>
        <span v-else-if="m.role === 'error'" style="color:#f44336">{{ m.text }}</span>
        <template v-else>
          <div v-html="renderMd(m.text)"></div>
          <el-collapse v-if="m.data" style="margin-top:8px">
            <el-collapse-item title="查看原始数据" name="1">
              <pre>{{ m.data }}</pre>
            </el-collapse-item>
          </el-collapse>
        </template>
      </div>
    </div>
    <div class="input-box">
      <el-input
        v-model="input"
        placeholder="输入运维指令..."
        @keydown.enter="send"
        size="large"
      />
      <el-button type="primary" size="large" @click="send" :disabled="!ws || ws.readyState !== WebSocket.OPEN">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'

const props = defineProps({ ws: Object })

const messages = ref([])
const input = ref('')
const msgBox = ref(null)

function append(role, text, data) {
  messages.value.push({ role, text, data })
  nextTick(() => {
    msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

function renderMd(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre>$2</pre>')
    .replace(/\n/g, '<br/>')
}

function send() {
  const text = input.value.trim()
  if (!text) return
  append('user', text)
  input.value = ''
  props.ws.send(text)
}

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}

onMounted(() => {
  if (props.ws) {
    props.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      switch (msg.type) {
        case 'status':
          break
        case 'thinking':
          break
        case 'tool_call':
          append('tool', msg.text)
          break
        case 'answer':
          append('assistant', msg.text, msg.data ? esc(msg.data) : null)
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
.chat-panel { flex: 1; display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
.msg { max-width: 85%; padding: 10px 14px; border-radius: 10px; line-height: 1.6; word-break: break-word; }
.msg.user { align-self: flex-end; background: #e94560; }
.msg.assistant { align-self: flex-start; background: #16213e; border: 1px solid #0f3460; }
.msg.tool, .msg.error { align-self: center; font-size: 12px; }
.msg pre { background: #0a0a1a; padding: 10px; border-radius: 6px; margin-top: 6px; font-size: 11px; max-height: 200px; overflow-y: auto; }
.input-box { display: flex; padding: 16px; background: #16213e; gap: 10px; border-top: 1px solid #0f3460; }
</style>
