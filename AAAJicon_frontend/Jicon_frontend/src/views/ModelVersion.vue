<template>
  <div class="model-version-container">
    <el-card class="mb-4">
      <div class="flex justify-between items-center">
        <div>
          当前在线模型版本：
          <el-tag type="success" v-if="currentModel">
            #{{ currentModel.id }} - {{ currentModel.description }}
          </el-tag>
          <span v-else>暂无</span>
        </div>
        <el-button type="primary" @click="openDialog()">新增模型版本</el-button>
      </div>
    </el-card>

    <el-table :data="tableData" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="description" label="模型描述" />
      <el-table-column prop="finish_date" label="完成时间" />
      <el-table-column prop="is_active" label="是否在线" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteModel(row.id)">删除</el-button>
          <el-button
            size="small"
            type="warning"
            :disabled="row.is_active"
            @click="setOnline(row.id)"
          >
            设为在线
          </el-button>
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

    <el-dialog :title="form.id ? '编辑模型版本' : '新增模型版本'" v-model="dialogVisible" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="描述">
          <el-input v-model="form.description" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const tableData = ref([])
const total = ref(0)
const pageSize = 10
const currentPage = ref(1)
const dialogVisible = ref(false)
const currentModel = ref(null)

const form = ref({
  id: null,
  description: ''
})

const fetchData = async () => {
  const res = await request.get('/model_versions/', {
    params: { page: currentPage.value, size: pageSize }
  })
  tableData.value = res.data.items
  total.value = res.data.total
}

const fetchCurrentModel = async () => {
  const res = await request.get('/model_versions/current')
  currentModel.value = res.data
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchData()
}

const openDialog = (row = null) => {
  if (row) {
    form.value = { ...row }
  } else {
    form.value = { id: null, description: '' }
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (form.value.id) {
    await request.put(`/model_versions/${form.value.id}`, {
      description: form.value.description
    })
    ElMessage.success('更新成功')
  } else {
    await request.post('/model_versions/', {
      description: form.value.description
    })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchData()
  fetchCurrentModel()
}

const deleteModel = async (id) => {
  await ElMessageBox.confirm('确认删除该模型版本？', '提示', { type: 'warning' })
  await request.delete(`/model_versions/${id}`)
  ElMessage.success('删除成功')
  fetchData()
  fetchCurrentModel()
}

const setOnline = async (id) => {
  await request.post(`/model_versions/${id}/online`)
  ElMessage.success('已设置为在线版本')
  fetchData()
  fetchCurrentModel()
}

onMounted(() => {
  fetchData()
  fetchCurrentModel()
})
</script>

<style scoped>
.model-version-container {
  padding: 20px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
