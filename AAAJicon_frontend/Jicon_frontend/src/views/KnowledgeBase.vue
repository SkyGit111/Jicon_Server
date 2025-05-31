<!-- src/views/KnowledgeBase.vue -->
<template>
  <div>
    <el-card>
      <div class="header">
        <h2>知识库版本管理</h2>
        <el-button type="primary" @click="openCreateDialog">新建版本</el-button>
      </div>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="version" label="版本号" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        background
        layout="prev, pager, next"
        :page-size="pagination.size"
        :current-page="pagination.page"
        :total="pagination.total"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 新建/编辑 Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑版本' : '新建版本'">
      <el-form :model="form" label-width="100px">
        <el-form-item label="版本号">
          <el-input v-model="form.version" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="form.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import request from '../utils/request'

const tableData = ref([])
const loading = ref(false)

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

const dialogVisible = ref(false)
const isEditing = ref(false)
const currentEditId = ref(null)

const form = reactive({
  version: '',
  description: '',
})

// 查询分页数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/knowledge_versions/', {
      params: {
        page: pagination.page,
        size: pagination.size,
      },
    })
    tableData.value = res.data.items || res.data || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

// 打开创建弹窗
const openCreateDialog = () => {
  isEditing.value = false
  currentEditId.value = null
  form.version = ''
  form.description = ''
  dialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (row) => {
  isEditing.value = true
  currentEditId.value = row.id
  form.version = row.version
  form.description = row.description
  dialogVisible.value = true
}

// 提交新建或编辑
const handleSubmit = async () => {
  if (isEditing.value) {
    await request.put(`/knowledge_versions/${currentEditId.value}`, {
      version: form.version,
      description: form.description,
    })
  } else {
    await request.post('/knowledge_versions/', {
      version: form.version,
      description: form.description,
    })
  }
  dialogVisible.value = false
  fetchData()
}

// 删除记录
const handleDelete = async (id) => {
  await request.delete(`/knowledge_versions/${id}`)
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
