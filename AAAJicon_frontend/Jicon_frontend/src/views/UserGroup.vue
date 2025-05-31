<template>
  <div class="user-group">
    <el-card>
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-bold">用户组管理</div>
        <el-button type="primary" @click="openDialog()">新增用户组</el-button>
      </div>

      <el-table :data="groups" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="组名" />
        <el-table-column label="成员列表">
          <template #default="{ row }">
            <span>{{ row.terminal_ids?.join(', ') || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该用户组？" @confirm="deleteGroup(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
            <el-button size="small" type="success" @click="editMembers(row)">成员管理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchGroups"
        />
      </div>
    </el-card>

    <!-- 新增/编辑 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogForm.id ? '编辑用户组' : '新增用户组'" width="400px">
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="组名">
          <el-input v-model="dialogForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveGroup">保存</el-button>
      </template>
    </el-dialog>

    <!-- 成员管理 弹窗 -->
    <el-dialog v-model="memberVisible" title="成员管理" width="400px">
      <el-tag
        v-for="id in selectedGroup.terminal_ids"
        :key="id"
        closable
        class="mb-1"
        @close="removeMember(id)"
      >{{ id }}</el-tag>
      <el-input-number v-model="newMemberId" class="mt-4" placeholder="输入终端ID" />
      <el-button type="primary" class="mt-2" @click="addMember">添加成员</el-button>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const groups = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const dialogVisible = ref(false)
const dialogForm = reactive({ id: null, name: '' })

const memberVisible = ref(false)
const selectedGroup = ref({})
const newMemberId = ref(null)

const fetchGroups = async () => {
  const res = await request.get(`/user_groups/?page=${page.value}&size=${pageSize}`)
  console.log('fetchGroups 返回：', res)

  groups.value = res.data.items.map(g => ({
  ...g,
  terminal_ids: g.members ? g.members.split(',').map(id => parseInt(id)) : []
  }))
  total.value = res.total
}

const openDialog = (row = null) => {
  if (row) {
    dialogForm.id = row.id
    dialogForm.name = row.name
  } else {
    dialogForm.id = null
    dialogForm.name = ''
  }
  dialogVisible.value = true
}

const saveGroup = async () => {
  if (!dialogForm.name.trim()) {
    ElMessage.warning('请输入组名')
    return
  }
  if (dialogForm.id) {
    await request.put(`/user_groups/${dialogForm.id}`, { name: dialogForm.name })
  } else {
    await request.post('/user_groups/', { name: dialogForm.name })
  }
  dialogVisible.value = false
  fetchGroups()
}

const deleteGroup = async (id) => {
  await request.delete(`/user_groups/${id}`)
  ElMessage.success('删除成功')
  fetchGroups()
}

const editMembers = async (row) => {
  const res = await request.get(`/user_groups/${row.id}/members`)
  selectedGroup.value = { ...row, terminal_ids: res.members }
  memberVisible.value = true
}

const addMember = async () => {
  if (!newMemberId.value) return
  await request.post(`/user_groups/${selectedGroup.value.id}/members`, {
    terminal_id: newMemberId.value
  })
  ElMessage.success('添加成功')
  newMemberId.value = null
  editMembers(selectedGroup.value)
}

const removeMember = async (term_id) => {
  await request.delete(`/user_groups/${selectedGroup.value.id}/members/${term_id}`)
  ElMessage.success('移除成功')
  editMembers(selectedGroup.value)
}

onMounted(fetchGroups)
</script>

<style scoped>
.user-group {
  padding: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
