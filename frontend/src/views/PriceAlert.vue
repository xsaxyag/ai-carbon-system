<template>
  <div class="price-alert">
    <h2>碳价实时预警</h2>

    <!-- 实时碳价卡片 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="price-card">
          <div class="price-header">
            <span class="market-name">全国碳市场 (CET)</span>
            <el-tag :type="priceData.is_real ? 'success' : 'info'" size="small">
              {{ priceData.is_real ? '实时' : '参考' }}
            </el-tag>
          </div>
          <div class="price-value">
            <span class="price-number">{{ priceData.price?.toFixed(2) || '--' }}</span>
            <span class="price-unit">元/吨</span>
          </div>
          <div class="price-change" :class="priceClass">
            <el-icon><component :is="priceIcon" /></el-icon>
            <span>{{ priceData.change > 0 ? '+' : '' }}{{ priceData.change?.toFixed(2) }} ({{ priceData.change_percent > 0 ? '+' : '' }}{{ priceData.change_percent?.toFixed(2) }}%)</span>
          </div>
          <div class="price-meta">
            <span>成交量: {{ (priceData.volume || 0).toLocaleString() }} 吨</span>
            <span style="margin-left: 16px;">{{ priceData.source }}</span>
          </div>
          <el-button type="primary" size="small" @click="refreshPrice" :loading="loading" style="margin-top: 12px;">
            刷新价格
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="trend-card">
          <template #header><span>趋势分析</span></template>
          <div v-if="trendData.trend" class="trend-content">
            <div class="trend-direction">
              <el-icon :class="'trend-' + trendData.trend" :size="32">
                <component :is="trendIcon" />
              </el-icon>
              <span class="trend-text">{{ trendData.description }}</span>
            </div>
            <div class="trend-stats">
              <div>7日均价: <strong>{{ trendData.ma7?.toFixed(2) }}</strong> 元/吨</div>
              <div>上涨天数: {{ trendData.up_days }} / 下跌天数: {{ trendData.down_days }}</div>
              <div v-if="trendData.prediction">
                预测价格: <strong :class="trendData.prediction > trendData.ma7 ? 'text-danger' : 'text-success'">{{ trendData.prediction?.toFixed(2) }}</strong> 元/吨
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无趋势数据" :image-size="60" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="alert-summary-card">
          <template #header><span>预警汇总</span></template>
          <div class="alert-stats">
            <div class="stat-item critical">
              <div class="stat-value">{{ alertSummary.critical_count || 0 }}</div>
              <div class="stat-label">严重</div>
            </div>
            <div class="stat-item warning">
              <div class="stat-value">{{ alertSummary.warning_count || 0 }}</div>
              <div class="stat-label">警告</div>
            </div>
            <div class="stat-item info">
              <div class="stat-value">{{ (alertSummary.alert_count || 0) - (alertSummary.critical_count || 0) - (alertSummary.warning_count || 0) }}</div>
              <div class="stat-label">提示</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警列表 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>预警消息</span>
          <el-select v-model="alertFilter" size="small" style="width: 120px;">
            <el-option label="全部" value="all" />
            <el-option label="严重" value="critical" />
            <el-option label="警告" value="warning" />
            <el-option label="提示" value="info" />
          </el-select>
        </div>
      </template>
      <div v-if="filteredAlerts.length > 0" class="alert-list">
        <div v-for="alert in filteredAlerts" :key="alert.type + alert.message" class="alert-item" :class="'alert-' + alert.level">
          <div class="alert-icon">
            <el-icon :size="24"><component :is="getAlertIcon(alert.level)" /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div v-if="alert.suggestion" class="alert-suggestion">{{ alert.suggestion }}</div>
          </div>
          <el-tag :type="getAlertTagType(alert.level)" size="small">
            {{ getAlertLabel(alert.level) }}
          </el-tag>
        </div>
      </div>
      <el-empty v-else description="暂无预警" :image-size="80" />
    </el-card>

    <!-- 价格历史图表 -->
    <el-card style="margin-top: 20px;">
      <template #header><span>价格走势</span></template>
      <div ref="priceChart" style="height: 300px;"></div>
    </el-card>

    <!-- 企业配额风险 -->
    <el-card style="margin-top: 20px;" v-if="companies.length > 0">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>企业配额风险</span>
          <el-select v-model="selectedCompanyId" placeholder="选择企业" size="small" style="width: 200px;" @change="loadCompanyAlerts">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
      </template>
      <div v-if="companyAlerts.length > 0" class="alert-list">
        <div v-for="alert in companyAlerts" :key="alert.type" class="alert-item" :class="'alert-' + alert.level">
          <div class="alert-icon">
            <el-icon :size="24"><component :is="getAlertIcon(alert.level)" /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div v-if="alert.suggestion" class="alert-suggestion">{{ alert.suggestion }}</div>
          </div>
          <el-tag :type="getAlertTagType(alert.level)" size="small">
            {{ getAlertLabel(alert.level) }}
          </el-tag>
        </div>
      </div>
      <el-empty v-else description="选择企业查看配额风险" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Top, Bottom, Minus, WarningFilled, InfoFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { API_BASE } from '../utils/auth'

const loading = ref(false)
const priceData = ref({})
const trendData = ref({})
const alertSummary = ref({})
const alerts = ref([])
const alertFilter = ref('all')
const companies = ref([])
const selectedCompanyId = ref(null)
const companyAlerts = ref([])
const priceHistory = ref([])
const priceChart = ref(null)

const priceClass = computed(() => {
  if (!priceData.value.change) return ''
  return priceData.value.change > 0 ? 'price-up' : 'price-down'
})

const priceIcon = computed(() => {
  if (!priceData.value.change) return Minus
  return priceData.value.change > 0 ? Top : Bottom
})

const trendIcon = computed(() => {
  if (trendData.value.trend === 'up') return Top
  if (trendData.value.trend === 'down') return Bottom
  return Minus
})

const filteredAlerts = computed(() => {
  if (alertFilter.value === 'all') return alerts.value
  return alerts.value.filter(a => a.level === alertFilter.value)
})

onMounted(() => {
  loadPrice()
  loadAlerts()
  loadCompanies()
})

async function loadPrice() {
  try {
    const res = await fetch(`${API_BASE}/price-alert/price`)
    priceData.value = await res.json()
    loadHistory()
  } catch (e) {
    ElMessage.error('获取碳价失败')
  }
}

async function refreshPrice() {
  loading.value = true
  await loadPrice()
  await loadAlerts()
  loading.value = false
  ElMessage.success('已刷新')
}

async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/price-alert/price/history?days=30`)
    const data = await res.json()
    priceHistory.value = data.history || []
    await nextTick()
    renderChart()
  } catch (e) {}
}

async function loadAlerts() {
  try {
    const res = await fetch(`${API_BASE}/price-alert/alerts`)
    const data = await res.json()
    alerts.value = data.alerts || []
    alertSummary.value = data
    trendData.value = data.trend || {}
  } catch (e) {
    ElMessage.error('获取预警失败')
  }
}

async function loadCompanies() {
  try {
    const res = await fetch(`${API_BASE}/carbon/company/`)
    companies.value = await res.json()
    if (companies.value.length > 0) {
      selectedCompanyId.value = companies.value[0].id
      loadCompanyAlerts()
    }
  } catch (e) {}
}

async function loadCompanyAlerts() {
  if (!selectedCompanyId.value) return
  try {
    const res = await fetch(`${API_BASE}/price-alert/alerts/company/${selectedCompanyId.value}`)
    const data = await res.json()
    companyAlerts.value = data.quota_alerts || []
  } catch (e) {}
}

function getAlertIcon(level) {
  if (level === 'critical') return WarningFilled
  if (level === 'warning') return InfoFilled
  return CircleCheckFilled
}

function getAlertTagType(level) {
  if (level === 'critical') return 'danger'
  if (level === 'warning') return 'warning'
  return 'info'
}

function getAlertLabel(level) {
  if (level === 'critical') return '严重'
  if (level === 'warning') return '警告'
  return '提示'
}

function renderChart() {
  if (!priceChart.value || priceHistory.value.length < 2) return
  const chart = echarts.init(priceChart.value)
  const data = priceHistory.value
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: p => `${p[0].name}<br/>价格: ${p[0].value.toFixed(2)} 元/吨` },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.map(h => h.timestamp?.substring(11, 19) || ''), axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', name: '元/吨', min: v => Math.floor(v.min - 5), max: v => Math.ceil(v.max + 5) },
    series: [{
      type: 'line',
      data: data.map(h => h.price),
      smooth: true,
      itemStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}
</script>

<style scoped>
.price-alert { padding: 20px; }
h2 { margin-bottom: 20px; color: #303133; }
.price-card { text-align: center; }
.price-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.market-name { font-size: 16px; font-weight: bold; }
.price-value { margin: 20px 0; }
.price-number { font-size: 48px; font-weight: bold; color: #409eff; }
.price-unit { font-size: 16px; color: #909399; margin-left: 8px; }
.price-change { font-size: 16px; display: flex; align-items: center; justify-content: center; gap: 4px; }
.price-up { color: #f56c6c; }
.price-down { color: #67c23a; }
.price-meta { font-size: 12px; color: #909399; margin-top: 8px; }
.trend-content { padding: 10px 0; }
.trend-direction { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.trend-up { color: #f56c6c; }
.trend-down { color: #67c23a; }
.trend-stable { color: #909399; }
.trend-text { font-size: 16px; font-weight: bold; }
.trend-stats { font-size: 13px; color: #606266; line-height: 2; }
.alert-stats { display: flex; justify-content: space-around; padding: 20px 0; }
.stat-item { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-item.critical .stat-value { color: #f56c6c; }
.stat-item.warning .stat-value { color: #e6a23c; }
.stat-item.info .stat-value { color: #909399; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.alert-list { }
.alert-item { display: flex; align-items: flex-start; padding: 16px; margin-bottom: 12px; border-radius: 8px; }
.alert-critical { background: #fef0f0; border-left: 4px solid #f56c6c; }
.alert-warning { background: #fdf6ec; border-left: 4px solid #e6a23c; }
.alert-info { background: #f4f4f5; border-left: 4px solid #909399; }
.alert-icon { margin-right: 12px; }
.alert-critical .alert-icon { color: #f56c6c; }
.alert-warning .alert-icon { color: #e6a23c; }
.alert-info .alert-icon { color: #909399; }
.alert-content { flex: 1; }
.alert-title { font-size: 15px; font-weight: bold; color: #303133; margin-bottom: 4px; }
.alert-message { font-size: 13px; color: #606266; margin-bottom: 4px; }
.alert-suggestion { font-size: 12px; color: #909399; font-style: italic; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>
