<template>
  <el-card>
    <div ref="chartRef" style="height: 300px;"></div>
  </el-card>
</template>

<script setup>
import * as echarts from 'echarts'
import {ref, watch, onMounted} from 'vue'

const props = defineProps({
  title: String,
  option: Object
})

const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  if (props.option) {
    chartInstance.setOption(props.option)
  }
})

watch(() => props.option, (newOption) => {
  if (chartInstance && newOption) {
    chartInstance.setOption(newOption)
  }
})
</script>
