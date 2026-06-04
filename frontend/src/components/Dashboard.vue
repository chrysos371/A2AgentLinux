<template>
  <div class="dashboard">
    <!-- 系统概览卡片 -->
    <div class="overview-cards">
      <div class="info-card" v-for="card in sysCards" :key="card.label">
        <span class="card-icon" v-html="card.icon"></span>
        <div class="card-info">
          <span class="card-value">{{ card.value }}</span>
          <span class="card-label">{{ card.label }}</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-box">
        <div class="chart-title">CPU 使用率</div>
        <VChart :option="cpuOption" autoresize />
      </div>
      <div class="chart-box">
        <div class="chart-title">内存使用</div>
        <VChart :option="memOption" autoresize />
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-box wide">
        <div class="chart-title">磁盘使用</div>
        <VChart :option="diskOption" autoresize />
      </div>
      <div class="chart-box">
        <div class="chart-title">进程 TOP 5 (CPU)</div>
        <VChart :option="procOption" autoresize />
      </div>
    </div>

    <!-- 网络端口 -->
    <div class="chart-box">
      <div class="chart-title">网络连接状态</div>
      <div class="network-grid">
        <div class="net-item" v-for="n in networkData" :key="n.name">
          <span class="net-name">{{ n.name }}</span>
          <span class="net-value" :class="n.status">{{ n.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { GaugeChart, PieChart, BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([GaugeChart, PieChart, BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const sysCards = ref([
  { label: '主机名', value: 'LoongArch-Server', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>' },
  { label: '运行时间', value: '7d 12h', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
  { label: '操作系统', value: 'Kylin V11', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>' },
  { label: '内核版本', value: '5.10-loong64', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>' },
])

const cpuOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 210, endAngle: -30,
    center: ['50%', '60%'],
    radius: '90%',
    min: 0, max: 100,
    splitNumber: 10,
    axisLine: {
      show: true,
      lineStyle: {
        width: 18,
        color: [[0.3, '#00e676'], [0.7, '#ffab40'], [1, '#ff3d5a']]
      }
    },
    pointer: { length: '65%', width: 6, itemStyle: { color: 'auto' } },
    detail: {
      fontSize: 28, fontWeight: 'bold', color: '#e8eaf0',
      formatter: '{value}%', offsetCenter: [0, '70%']
    },
    data: [{ value: 47, name: 'CPU' }],
    axisLabel: { color: '#5a6380', fontSize: 11 },
    title: { color: '#8892aa', fontSize: 13, offsetCenter: [0, '95%'] }
  }]
}))

const memOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 5, textStyle: { color: '#8892aa', fontSize: 11 } },
  series: [{
    type: 'pie',
    radius: ['55%', '80%'],
    center: ['50%', '48%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 6, borderColor: '#0a1030', borderWidth: 3 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#e8eaf0' } },
    data: [
      { value: 62, name: '已使用', itemStyle: { color: '#7c5cfc' } },
      { value: 38, name: '可用', itemStyle: { color: '#1e2a5a' } },
    ]
  }]
}))

const diskOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 10, right: 30, top: 10, bottom: 20 },
  xAxis: {
    type: 'value', max: 100,
    axisLabel: { color: '#5a6380', formatter: '{value}%' },
    splitLine: { lineStyle: { color: '#1e2a5a' } }
  },
  yAxis: {
    type: 'category',
    data: ['/', '/home', '/var', '/boot'],
    axisLabel: { color: '#8892aa', fontSize: 12 },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  series: [{
    type: 'bar',
    barWidth: 16,
    itemStyle: { borderRadius: [0, 6, 6, 0] },
    data: [
      { value: 45, itemStyle: { color: '#00d4ff' } },
      { value: 72, itemStyle: { color: '#ffab40' } },
      { value: 35, itemStyle: { color: '#00d4ff' } },
      { value: 18, itemStyle: { color: '#00e676' } },
    ],
    label: { show: true, position: 'right', color: '#8892aa', formatter: '{c}%', fontSize: 11 }
  }]
}))

const procOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 10, right: 10, top: 10, bottom: 20 },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#5a6380' },
    splitLine: { lineStyle: { color: '#1e2a5a' } }
  },
  yAxis: {
    type: 'category',
    data: ['python3', 'mysqld', 'nginx', 'sshd', 'systemd'],
    axisLabel: { color: '#8892aa', fontSize: 11 },
    axisLine: { show: false }, axisTick: { show: false }
  },
  series: [{
    type: 'bar', barWidth: 12,
    itemStyle: { borderRadius: [0, 4, 4, 0], color: '#7c5cfc' },
    data: [12.5, 8.3, 5.1, 1.2, 0.8],
    label: { show: true, position: 'right', color: '#8892aa', formatter: '{c}%', fontSize: 10 }
  }]
}))

const networkData = ref([
  { name: 'SSH (22)', value: '4 连接', status: 'ok' },
  { name: 'HTTP (80)', value: '监听中', status: 'ok' },
  { name: 'MCP (8000)', value: '监听中', status: 'ok' },
  { name: 'Agent (8080)', value: '2 连接', status: 'ok' },
  { name: 'MySQL (3306)', value: '未开放', status: 'off' },
  { name: 'Redis (6379)', value: '未开放', status: 'off' },
])
</script>

<style scoped>
.dashboard {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: var(--transition);
}

.info-card:hover {
  border-color: rgba(0,212,255,0.3);
  background: var(--bg-card-hover);
}

.card-icon {
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(0,212,255,0.06);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.card-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.charts-row {
  display: flex;
  gap: 14px;
}

.chart-box {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  min-height: 260px;
}

.chart-box.wide {
  flex: 2;
}

.chart-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 8px;
}

.chart-box :deep(.echarts) {
  height: 220px !important;
}

.network-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 8px;
}

.net-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--bg-deep);
  border-radius: var(--radius-sm);
}

.net-name {
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.net-value {
  font-size: 12px;
  font-weight: 600;
}

.net-value.ok { color: var(--success); }
.net-value.off { color: var(--text-muted); }
</style>
