<!-- src/layouts/AdminLayout.vue -->
<template>
  <el-container style="height: 100vh">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">济控管理平台</div>
      <el-menu :default-active="activeMenu" router class="el-menu-vertical">
        <el-menu-item index="/dashboard">
          <i class="el-icon-menu"></i>
          <span>总览仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/terminal">
          <span>终端管理</span>
        </el-menu-item>
         <el-menu-item index="/userGroup">
          <span>用户组管理</span>
        </el-menu-item>
         <el-menu-item index="/message">
          <span>消息记录管理</span>
        </el-menu-item>
        <el-menu-item index="/detection">
          <span>检测记录管理</span>
        </el-menu-item>
         <el-menu-item index="/result">
          <span>结果管理</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <span>知识库管理</span>
        </el-menu-item>
        <el-menu-item index="/model">
          <span>模型版本管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 内容区域 -->
    <el-container>
      <el-header class="header">
        <div>欢迎使用济控管理平台</div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar {
  background-color: #2d3a4b;
  color: #fff;
}

.logo {
  padding: 20px;
  font-size: 18px;
  color: #fff;
  font-weight: bold;
  text-align: center;
  background-color: #1f2d3d;
}

.el-menu-vertical {
  border-right: none;
  background-color: #2d3a4b;
}

.el-menu-vertical .el-menu-item {
  color: #fff;
}

.el-menu-vertical .el-menu-item.is-active {
  background-color: #409eff;
  color: white;
}

.header {
  background-color: #fff;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  height: 100%;
}
</style>
