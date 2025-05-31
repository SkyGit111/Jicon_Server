<template>
  <div class="detection-records">
    <el-card>
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-bold">检测记录</div>
      </div>

      <el-table :data="records" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="date" label="检测时间" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="message_id" label="消息 ID" />
        <el-table-column prop="terminal_id" label="终端 ID" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewRecord(row.id)">详情</el-button>
            <el-popconfirm title="确认删除该记录？" @confirm="deleteRecord(row.id)">
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
          @current-change="fetchRecords"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="检测详情" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="检测时间">{{ detail.date }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.type }}</el-descriptions-item>
        <el-descriptions-item label="消息 ID">{{ detail.message_id }}</el-descriptions-item>
        <el-descriptions-item label="终端 ID">{{ detail.terminal_id }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const detailVisible = ref(false)
const detail = reactive({
  id: null,
  date: '',
  type: '',
  message_id: null,
  terminal_id: null
})

const fetchRecords = async () => {
  try {
    const res = await request.get(`/detections/?page=${page.value}&size=${pageSize}`)
    records.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (err) {
    ElMessage.error('加载失败')
  }
}

const viewRecord = async (id) => {
  try {
    const res = await request.get(`/detections/${id}`)
    Object.assign(detail, res.data)
    detailVisible.value = true
  } catch (err) {
    ElMessage.error('获取详情失败')
  }
}

const deleteRecord = async (id) => {
  try {
    await request.delete(`/detections/${id}`)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchRecords)
</script>

<style scoped>
.detection-records {
  padding: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
