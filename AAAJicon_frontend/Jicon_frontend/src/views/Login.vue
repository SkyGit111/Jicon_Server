<!-- src/views/Login.vue -->
<template>
  <el-card class="login-card">
    <h2>济控管理平台 - 登录</h2>
    <el-form :model="form" :rules="rules" ref="loginForm" label-width="80px">
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleLogin">登录</el-button>
        <el-button type="text" @click="goRegister">去注册</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { useUserStore } from '../store/user'
import {ElMessage} from "element-plus";

const router = useRouter()
const loginForm = ref(null)
const userStore = useUserStore()

const form = reactive({
  email: '',
  password: '',
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = () => {
  loginForm.value.validate(async (valid) => {
    if (!valid) return

    try {
      const res = await request.post('/admin/signin', {
        email: form.email,
        password: form.password,
      })

      const token = res.data.access_token
      userStore.setToken(token)
      ElMessage.success('登录成功')
      await router.push('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.message || '登录失败，请检查账号或密码'
      ElMessage.error(msg)
    }
  })
}

const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-card {
  width: 400px;
  margin: 100px auto;
  padding: 20px;
}
</style>
