// src/utils/request.js
import axios from 'axios'
import { useUserStore } from '../store/user'

const BASE_URL = 'http://localhost:5001'

const request = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
})

// 拦截请求加上 token
request.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

export default request
