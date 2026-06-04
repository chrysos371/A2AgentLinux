<template>
  <aside class="sidebar">
    <h3>A2 运维 Agent</h3>
    <p class="desc">
      基于 DeepSeek + MCP<br/>
      安全护栏 · 最小权限 · 审计溯源
    </p>

    <el-divider style="border-color:#0f3460;margin:8px 0" />

    <label class="label">DeepSeek API Key</label>
    <el-input
      v-model="keyInput"
      type="password"
      placeholder="sk-..."
      size="small"
      show-password
    />
    <el-button type="primary" size="small" @click="$emit('set-key', keyInput)">
      设置 Key
    </el-button>

    <el-divider style="border-color:#0f3460;margin:8px 0" />

    <div class="stat">
      <div>MCP 工具: <strong>{{ toolCount }}</strong> 个</div>
      <div>AI 状态: <strong>{{ aiReady ? '已连接' : '未设置' }}</strong></div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  apiKey: String,
  toolCount: Number,
  aiReady: Boolean,
})

defineEmits(['set-key'])

const keyInput = ref('')
</script>

<style scoped>
.sidebar {
  width: 260px; min-width: 260px; background: #16213e;
  padding: 20px; display: flex; flex-direction: column; gap: 10px;
  border-right: 1px solid #0f3460;
}
h3 { font-size: 18px; color: #e94560; }
.desc { font-size: 12px; color: #888; line-height: 1.6; }
.label { font-size: 12px; color: #aaa; }
.stat { font-size: 12px; color: #aaa; line-height: 1.8; }
.stat strong { color: #eee; }
</style>
