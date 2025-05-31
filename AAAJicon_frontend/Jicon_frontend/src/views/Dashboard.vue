<template>
  <div class="dashboard">
    <el-card class="mb-4">
      <div class="text-lg font-bold mb-2">系统总览仪表盘</div>
      <div class="grid grid-cols-2 gap-4">
        <ChartCard title="终端状态统计" :option="terminalStateOption" />
        <ChartCard title="用户组数量" :option="groupCountOption" />
        <ChartCard title="检测记录数量" :option="detectionCountOption" />
        <ChartCard title="检测标签分布" :option="labelDistributionOption" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import ChartCard from '../components/ChartCard.vue'  // 封装好的 ECharts 组件

const terminalStateOption = ref({})
const groupCountOption = ref({})
const detectionCountOption = ref({})
const labelDistributionOption = ref({})

const fetchAllData = async () => {
  // 1. 终端状态统计
  const terminalRes = await request.get('/terminals/?page=1&size=100')
  const totalTerminals = terminalRes.data.total
  const active = terminalRes.data.items.filter(t => t.state).length
  const inactive = totalTerminals - active
  terminalStateOption.value = {
    title: { text: `终端总数：${totalTerminals}`, left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: [
          { value: active, name: '启用' },
          { value: inactive, name: '禁用' }
        ],
        label: { formatter: '{b}: {c} ({d}%)' }
      }
    ]
  }

  // 2. 用户组数量
  const groupRes = await request.get('/user_groups/?page=1&size=100')
  groupCountOption.value = {
    title: { text: `用户组数量：${groupRes.data.total}`, left: 'center' },
    tooltip: {},
    xAxis: { type: 'category', data: groupRes.data.items.map(g => `组${g.name}`) },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: groupRes.data.items.map(g =>g.members ? g.members.split(',').filter(m => m.trim() !== '').length : 0),
        label: { show: true, position: 'top' }
      }
    ]
  }

  // 3. 检测记录数量
  const detectionRes = await request.get('/detections/?page=1&size=100')
  detectionCountOption.value = {
    title: { text: `检测记录总数：${detectionRes.data.total}`, left: 'center' },
    tooltip: {},
    xAxis: { type: 'category', data: detectionRes.data.items.map(d => `记录${d.id}`) },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: detectionRes.data.items.map(() => 1),
        label: { show: false }
      }
    ]
  }

  // 4. 标签分布
  const resultRes = await request.get('/messages/?page=1&size=100')
  const labelMap = {}
  resultRes.data.items.forEach(r => {
    labelMap[r.label] = (labelMap[r.label] || 0) + 1
  })
  labelDistributionOption.value = {
    title: { text: '标签分布', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: Object.entries(labelMap).map(([label, count]) => ({ name: label, value: count })),
        label: { formatter: '{b}: {c} ({d}%)' }
      }
    ]
  }
}

onMounted(fetchAllData)
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.mb-4 {
  margin-bottom: 1rem;
}
.grid {
  display: grid;
  gap: 20px;
}
.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}
</style>
