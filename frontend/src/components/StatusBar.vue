<template>
  <header class="status-bar">
    <div class="brand">
      <span class="logo">A2</span>
      <span class="title">安全智能运维 Agent</span>
      <span class="badge">麒麟 OS</span>
    </div>

    <div class="indicators">
      <div class="indicator">
        <span class="pulse" :class="mcpOn ? 'on' : 'off'"></span>
        <span class="label">MCP</span>
        <span class="value">{{ mcpOn ? `${toolCount} tools` : '断开' }}</span>
      </div>
      <div class="divider"></div>
      <div class="indicator">
        <span class="pulse" :class="aiReady ? 'on' : 'off'"></span>
        <span class="label">DeepSeek</span>
        <span class="value">{{ aiReady ? '已连接' : '未设置' }}</span>
      </div>
      <div class="divider"></div>
      <div class="indicator">
        <span class="shield-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </span>
        <span class="label">护栏</span>
        <span class="value active">运行中</span>
      </div>
    </div>

    <div class="time">{{ now }}</div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({ mcpOn: Boolean, aiReady: Boolean, toolCount: Number })

const now = ref('')
let timer = null
onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  }, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 20px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  flex-shrink: 0;
  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 8px;
  font-weight: 800;
  font-size: 14px;
  color: #fff;
  letter-spacing: -0.5px;
}

.title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(0,212,255,0.12);
  color: var(--accent);
  border: 1px solid rgba(0,212,255,0.2);
  font-weight: 500;
}

.indicators {
  display: flex;
  align-items: center;
  gap: 16px;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.divider {
  width: 1px;
  height: 20px;
  background: var(--border);
}

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: relative;
}

.pulse.on {
  background: var(--success);
  box-shadow: 0 0 8px rgba(0,230,118,0.5);
  animation: pulse-glow 2s ease-in-out infinite;
}

.pulse.off {
  background: var(--text-muted);
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 4px rgba(0,230,118,0.4); }
  50% { box-shadow: 0 0 12px rgba(0,230,118,0.7); }
}

.shield-icon {
  color: var(--accent);
  display: flex;
  align-items: center;
}

.label {
  color: var(--text-secondary);
  font-weight: 500;
}

.value {
  color: var(--text-primary);
  font-weight: 600;
}

.value.active {
  color: var(--success);
}

.time {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-muted);
  min-width: 80px;
  text-align: right;
}
</style>
