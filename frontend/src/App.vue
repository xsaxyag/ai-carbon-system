<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="200px">
      <div class="logo">
        <el-icon :size="24"><DataBoard /></el-icon>
        <span>AI碳枢算</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#1a1a2e"
        text-color="#fff"
        active-text-color="#409eff"
      >
        <el-menu-item index="/ai-carbon-system/">
          <el-icon><DataBoard /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/carbon">
          <el-icon><Coin /></el-icon>
          <span>碳数据录入</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/ocr">
          <el-icon><Camera /></el-icon>
          <span>OCR识别</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/company">
          <el-icon><OfficeBuilding /></el-icon>
          <span>企业管理</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/report">
          <el-icon><Document /></el-icon>
          <span>碳排报告</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/compare">
          <el-icon><Scale /></el-icon>
          <span>企业对比</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/price-alert">
          <el-icon><Bell /></el-icon>
          <span>碳价预警</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/optimization">
          <el-icon><TrendCharts /></el-icon>
          <span>降碳优化</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/carbon-asset">
          <el-icon><Wallet /></el-icon>
          <span>碳资产</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/carbon-trace">
          <el-icon><Box /></el-icon>
          <span>碳足迹</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/wizard">
          <el-icon><Guide /></el-icon>
          <span>智能填报</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/backup">
          <el-icon><FolderOpened /></el-icon>
          <span>数据备份</span>
        </el-menu-item>
        <el-menu-item index="/ai-carbon-system/ai-advisor">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI顾问</span>
        </el-menu-item>
      </el-menu>

      <!-- 侧边栏底部用户信息 -->
      <div class="sidebar-user" v-if="currentUser">
        <el-divider style="margin: 8px 0; border-color: #2d2d4a;" />
        <div class="user-info">
          <el-icon><User /></el-icon>
          <span class="user-name">{{ currentUser.username }}</span>
        </div>
        <div class="user-company">{{ currentUser.company_name }}</div>
        <el-button type="danger" text size="small" @click="handleLogout" style="margin-top:6px; width:100%;">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header>
        <div class="header-title">碳中和智能管理系统</div>
        <div class="header-right">
          <el-tag v-if="currentUser" type="success" size="small">{{ currentUser.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
          <el-button text>{{ currentDate }}</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUser, clearAuth } from './utils/auth'

const router = useRouter()
const currentDate = ref('')
const currentUser = computed(() => getUser())

onMounted(() => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

function handleLogout() {
  ElMessageBox.confirm('确定退出登录？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    clearAuth()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#app {
  height: 100vh;
}

.app-container {
  height: 100vh;
  background: #f5f7fa;
}

.el-aside {
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  border-bottom: 1px solid #2d2d4a;
  flex-shrink: 0;
}

.el-menu {
  border-right: none;
  flex: 1;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-menu-item:hover {
  background: #2d2d4a !important;
}

.sidebar-user {
  padding: 8px 16px 16px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  font-size: 14px;
}

.user-name {
  font-weight: 600;
}

.user-company {
  color: #909399;
  font-size: 12px;
  margin-top: 2px;
  padding-left: 22px;
}

.el-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.el-main {
  padding: 20px;
  overflow-y: auto;
}
</style>
