// src/store/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
  }),
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('access_token', token)
    },
    logout() {
      this.token = ''
      localStorage.removeItem('access_token')
    },
  },
})
