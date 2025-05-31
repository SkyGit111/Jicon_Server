import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminLayout from '../layouts/AdminLayout.vue'

import Dashboard from '../views/Dashboard.vue'
import DetectionRecords from '../views/DetectionRecords.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'
import ModelVersion from '../views/ModelVersion.vue'
import UserGroup from "../views/UserGroup.vue"
import Terminal from "../views/Terminal.vue"
import Result from "../views/Result.vue";
import MessageRecords from "../views/MessageRecords.vue";

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {
    path: '/',
    component: AdminLayout,
    children: [
      { path: '/dashboard', component: Dashboard },
      { path: '/userGroup', component: UserGroup },
      { path: '/terminal', component: Terminal },
      { path: '/message', component: MessageRecords },
      { path: '/detection', component: DetectionRecords },
      { path: '/result', component: Result },
      { path: '/knowledge', component: KnowledgeBase },
      { path: '/model', component: ModelVersion },

    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
