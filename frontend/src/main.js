import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
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
import Carbon3DDashboard from './views/Carbon3DDashboard.vue'
import CarbonFootprint3D from './views/CarbonFootprint3D.vue'
import DigitalTwinFactory from './views/DigitalTwinFactory.vue'
import SupplyChainGraph from './views/SupplyChainGraph.vue'
import EnergySynergy from './views/EnergySynergy.vue'
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
  { path: '/price-alert', name: 'PriceAlert', component: PriceAlert },
  { path: '/3d-dashboard', name: 'Carbon3DDashboard', component: Carbon3DDashboard },
  { path: '/footprint-3d', name: 'CarbonFootprint3D', component: CarbonFootprint3D },
  { path: '/digital-twin', name: 'DigitalTwinFactory', component: DigitalTwinFactory },
  { path: '/supply-chain', name: 'SupplyChainGraph', component: SupplyChainGraph },
  { path: '/energy-synergy', name: 'EnergySynergy', component: EnergySynergy }
]

const router = createRouter({
  history: createWebHashHistory('/ai-carbon-system/'),
  routes
})

// 路由守卫 - 未登录跳转登录页
router.beforeEach((to, from, next) => {
  if (to.meta.public || isAuthenticated()) {
    next()
  } else {
    next('/login')
  }
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
