<template>
  <div class="terminal-management">
    <el-card>
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-bold">终端管理</div>
        <el-button type="primary" @click="openDialog(false)">新增终端</el-button>
      </div>

      <el-table :data="terminals" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="signin_date" label="注册时间" />
        <el-table-column prop="state" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.state ? 'success' : 'info'">
              {{ row.state ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="group_id" label="所属用户组" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(true, row)">编辑</el-button>
            <el-popconfirm title="确认删除该设备？" @confirm="deleteTerminal(row.id)">
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
          @current-change="fetchTerminals"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑终端' : '新增终端'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="注册时间">
          <el-date-picker
            v-model="form.signin_date"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.state" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="所属用户组">
          <el-input-number v-model="form.group_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTerminal">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const terminals = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = reactive({
  id: null,  // 只用于编辑时引用，不提交
  signin_date: '',
  state: true,
  group_id: null,
})

const fetchTerminals = async () => {
  const res = await request.get(`/terminals/?page=${page.value}&size=${pageSize}`)
  terminals.value = res.data.items || []
  total.value = res.data.total || 0
}

const openDialog = (edit = false, row = null) => {
  isEdit.value = edit
  if (edit && row) {
    Object.assign(form, { ...row })
  } else {
    form.id = null
    form.signin_date = ''
    form.state = true
    form.group_id = null
  }
  dialogVisible.value = true
}

const saveTerminal = async () => {
  if (!form.signin_date || form.group_id == null) {
    ElMessage.warning('请填写所有必填字段')
    return
  }

  const { id, ...payload } = form // 剥离 id 字段
  try {
    if (isEdit.value) {
      await request.put(`/terminals/${form.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/terminals/', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTerminals()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '操作失败')
  }
}

const deleteTerminal = async (id) => {
  try {
    await request.delete(`/terminals/${id}`)
    ElMessage.success('删除成功')
    fetchTerminals()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchTerminals)
</script>

<style scoped>
.terminal-management {
  padding: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
