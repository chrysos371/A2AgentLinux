<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="shield-large">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div>
        <h3>Agent 控制台</h3>
        <p>安全护栏 · 最小权限 · 审计溯源</p>
      </div>
    </div>

    <div class="card api-card">
      <div class="card-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
        DeepSeek API Key
      </div>
      <el-input
        v-model="keyInput"
        type="password"
        placeholder="sk-..."
        size="default"
        show-password
        class="key-input"
      />
      <el-button type="primary" size="default" @click="$emit('set-key', keyInput)" class="set-btn">
        连接 AI
      </el-button>
    </div>

    <div class="card stats-card">
      <div class="card-label">系统状态</div>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ mcpOn ? toolCount : '--' }}</span>
          <span class="stat-label">MCP 工具</span>
        </div>
        <div class="stat-item">
          <span class="stat-value" :class="aiReady ? 'green' : 'dim'">{{ aiReady ? 'ON' : 'OFF' }}</span>
          <span class="stat-label">DeepSeek</span>
        </div>
        <div class="stat-item">
          <span class="stat-value green">3 层</span>
          <span class="stat-label">安全护栏</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">审计</span>
          <span class="stat-label">日志追踪</span>
        </div>
      </div>
    </div>

    <div class="card tips-card">
      <div class="card-label">快捷指令</div>
      <div class="tips">
        <span class="tip" @click="$emit('quick', '查看服务器内存')">查看内存</span>
        <span class="tip" @click="$emit('quick', '检查服务器安全状态')">安全检查</span>
        <span class="tip" @click="$emit('quick', '查看网络连接')">网络连接</span>
        <span class="tip" @click="$emit('quick', '检查防火墙状态')">防火墙</span>
        <span class="tip" @click="$emit('quick', '服务器一键巡检')">一键巡检</span>
        <span class="tip" @click="$emit('quick', '查看 Docker 容器')">Docker</span>
      </div>
    </div>

    <div class="sidebar-footer">
      <span class="version">v0.2.0 · MCP-Native</span>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ apiKey: String, toolCount: Number, aiReady: Boolean, mcpOn: Boolean })
defineEmits(['set-key', 'quick'])

const keyInput = ref('')
</script>

<style scoped>
.sidebar {
  width: 272px;
  min-width: 272px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  gap: 14px;
  position: relative;
  z-index: 2;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 4px;
}

.shield-large {
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(0,212,255,0.08);
  border-radius: var(--radius);
  border: 1px solid rgba(0,212,255,0.15);
  flex-shrink: 0;
}

.sidebar-header h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}

.sidebar-header p {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 1px;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
}

.card-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-label svg { color: var(--accent); }

.api-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.key-input :deep(.el-input__wrapper) {
  background: var(--bg-deep) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
  border-radius: var(--radius-sm) !important;
}

.key-input :deep(.el-input__inner) {
  color: var(--text-primary) !important;
  font-family: var(--font-mono);
  font-size: 12px;
}

.set-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  border: none !important;
  font-weight: 600;
  font-size: 13px;
  border-radius: var(--radius-sm) !important;
  height: 36px;
}

.set-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  transition: var(--transition);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 6px;
  background: var(--bg-deep);
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.green { color: var(--success); }
.stat-value.dim { color: var(--text-muted); }

.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 2px;
}

.tips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tip {
  font-size: 11px;
  padding: 5px 10px;
  background: var(--bg-deep);
  border: 1px solid var(--border);
  border-radius: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}

.tip:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(0,212,255,0.06);
}

.sidebar-footer {
  margin-top: auto;
  text-align: center;
  padding-top: 8px;
}

.version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
}
</style>
