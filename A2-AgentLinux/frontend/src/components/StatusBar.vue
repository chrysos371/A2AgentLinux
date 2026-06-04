<template>
  <div class="status-bar">
    <span><span class="dot" :class="mcpOn ? 'on' : 'off'"></span> MCP: {{ mcpOn ? '就绪' : '断开' }}</span>
    <span><span class="dot" :class="aiReady ? 'on' : 'off'"></span> DeepSeek: {{ aiReady ? '已连接' : '未设置' }}</span>
  </div>
</template>

<script setup>
defineProps({ mcpOn: Boolean, aiReady: Boolean })
</script>

<style scoped>
.status-bar {
  padding: 8px 20px; font-size: 12px; color: #888;
  border-bottom: 1px solid #0f3460; display: flex; gap: 16px;
}
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.dot.on { background: #4caf50; }
.dot.off { background: #f44336; }
</style>
