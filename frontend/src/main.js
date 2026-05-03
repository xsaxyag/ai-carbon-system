import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import CarbonEntry from './views/CarbonEntry.vue'
import OCRUpload from './views/OCRUpload.vue'
import CompanyManage from './views/CompanyManage.vue'
import CarbonReport from './views/CarbonReport.vue'
import AIAdvisor from './views/AIAdvisor.vue'
import CarbonAsset from './views/CarbonAsset.vue'
import Optimization from './views/Optimization.vue'
import CarbonTrace from './views/CarbonTrace.vue'
import Backup from './views/Backup.vue'
import CarbonWizard from './views/CarbonWizard.vue'
import CompanyCompare from './views/CompanyCompare.vue'
import PriceAlert from './views/PriceAlert.vue'
import Login from './views/Login.vue'
import { isAuthenticated } from './utils/auth'

// 路由配置
const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/carbon', name: 'CarbonEntry', component: CarbonEntry },
  { path: '/ocr', name: 'OCRUpload', component: OCRUpload },
  { path: '/company', name: 'CompanyManage', component: CompanyManage },
  { path: '/report', name: 'CarbonReport', component: CarbonReport },
  { path: '/ai-advisor', name: 'AIAdvisor', component: AIAdvisor },
  { path: '/carbon-asset', name: 'CarbonAsset', component: CarbonAsset },
  { path: '/optimization', name: 'Optimization', component: Optimization },
  { path: '/carbon-trace', name: 'CarbonTrace', component: CarbonTrace },
  { path: '/backup', name: 'Backup', component: Backup },
  { path: '/wizard', name: 'CarbonWizard', component: CarbonWizard },
  { path: '/compare', name: 'CompanyCompare', component: CompanyCompare },
  { path: '/price-alert', name: 'PriceAlert', component: PriceAlert }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 已禁用登录验证，直接放行
router.beforeEach((to, from, next) => {
  // 自动设置模拟登录状态（免登录）
  if (!localStorage.getItem('token')) {
    localStorage.setItem('token', 'demo-token')
    localStorage.setItem('user', JSON.stringify({ username: 'admin', role: 'admin' }))
  }
  next()
})

// 创建应用
const app = createApp(App)

// 注册Element Plus
app.use(ElementPlus)
app.use(router)

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
