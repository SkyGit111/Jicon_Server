<!-- src/views/Register.vue -->
<template>
  <el-card class="login-card">
    <h2>济控管理平台 - 注册</h2>
    <el-form :model="form" :rules="rules" ref="registerForm" label-width="80px">
      <el-form-item label="用户名" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleRegister">注册</el-button>
        <el-button type="text" @click="goLogin">去登录</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import {ElMessage} from "element-plus";

const router = useRouter()
const registerForm = ref(null)

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirm: '',
})

const rules = {
  name: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const handleRegister = () => {
  registerForm.value.validate(async (valid) => {
    if (!valid) return

    try {
      const res = await request.post('/admin/signup', {
        name: form.name,
        email: form.email,
        password: form.password,
      })
      ElMessage.success('注册成功，请登录')
      await router.push('/login')
    } catch (err) {
      const msg = err.response?.data?.message || '注册失败，请检查输入'
      ElMessage.error(msg)
    }
  })
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.login-card {
  width: 400px;
  margin: 100px auto;
  padding: 20px;
}
</style>
