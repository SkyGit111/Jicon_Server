<template xmlns="http://www.w3.org/1999/html">
  <div class="message-records">
    <el-card class="mb-4">
      <div class="flex justify-between items-center">
        <span class="font-bold text-lg">消息记录管理</span>
        <br>
        <el-button type="primary" @click="openDialog()">新增消息</el-button>
      </div>
    </el-card>

    <el-table :data="tableData" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="label" label="标签" width="120" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteMessage(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="mt-4"
      layout="total, prev, pager, next"
      :total="total"
      :page-size="pageSize"
      @current-change="handlePageChange"
    />

   <el-card class="flex-grow chart-card">
    <div class="font-bold mb-2">标签分布统计</div>
    <div ref="chartRef" class="chart-container"></div>
  </el-card>


    <el-dialog :title="form.id ? '编辑消息' : '新增消息'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.label" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const tableData = ref([])
const total = ref(0)
const pageSize = 10
const currentPage = ref(1)
const dialogVisible = ref(false)
const form = ref({ id: null, content: '', label: '' })
const chartRef = ref()

const fetchData = async () => {
  const res = await request.get('/messages/', {
    params: { page: currentPage.value, size: pageSize }
  })
  tableData.value = res.data.items
  total.value = res.data.total
}

const fetchStats = async () => {
  const res = await request.get('/messages/statistics')
  renderChart(res.data.statistics)
}

const renderChart = (data) => {
  nextTick(() => {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      xAxis: { type: 'category', data: data.map(d => d.label) },
      yAxis: { type: 'value' },
      series: [{ data: data.map(d => d.count), type: 'bar' }]
    })
    window.addEventListener('resize', () => chart.resize())
  })
}


const handlePageChange = (page) => {
  currentPage.value = page
  fetchData()
}

const openDialog = (row = null) => {
  if (row) {
    form.value = { ...row }
  } else {
    form.value = { id: null, content: '', label: '' }
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (form.value.id) {
    await request.put(`/messages/${form.value.id}`, {
      content: form.value.content,
      label: form.value.label
    })
    ElMessage.success('更新成功')
  } else {
    await request.post('/messages/', {
      content: form.value.content,
      label: form.value.label
    })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchData()
  fetchStats()
}

const deleteMessage = async (id) => {
  await ElMessageBox.confirm('确认删除该消息？', '提示', { type: 'warning' })
  await request.delete(`/messages/${id}`)
  ElMessage.success('删除成功')
  fetchData()
  fetchStats()
}

onMounted(() => {
  fetchData()
  fetchStats()
})
</script>

<style scoped>
.message-records {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.chart-container {
  flex: 1;
  min-height: 300px;
}
</style>
