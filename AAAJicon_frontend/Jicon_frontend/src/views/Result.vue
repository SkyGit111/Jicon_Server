<template>
  <div class="result-management">
    <el-card>
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-bold">检测结果管理</div>
      </div>

      <el-table :data="results" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="message_id" label="消息 ID" />
        <el-table-column prop="detection_id" label="检测记录 ID" />
        <el-table-column prop="label" label="标签" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-popconfirm title="确认删除该结果？" @confirm="deleteResult(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchResults"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const fetchResults = async () => {
  try {
    const res = await request.get(`/results/?page=${page.value}&size=${pageSize}`)
    results.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取检测结果失败')
  }
}

const deleteResult = async (id) => {
  try {
    await request.delete(`/results/${id}`)
    ElMessage.success('删除成功')
    fetchResults()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchResults)
</script>

<style scoped>
.result-management {
  padding: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
