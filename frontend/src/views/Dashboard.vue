<template>
  <div class="dashboard">
    <!-- 骨架屏 -->
    <div v-if="loading" class="skeleton-wrapper">
      <el-skeleton :rows="3" animated />
      <el-row :gutter="20" style="margin-top:20px;">
        <el-col :span="6" v-for="i in 4" :key="i">
          <el-skeleton style="height:100px;" animated />
        </el-col>
      </el-row>
    </div>

    <template v-else>
      <!-- 统计卡片（带数字滚动 + hover 动效） -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6" v-for="(card, idx) in statCards" :key="idx">
          <el-card shadow="hover" class="stat-card" :class="'stat-card-' + idx">
            <div class="stat-icon" :style="{ background: card.gradient }">
              <el-icon :size="36"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">
                <span class="counter" :ref="el => setCounterRef(el, idx)">0</span>
                <span v-if="card.unit" class="stat-unit">{{ card.unit }}</span>
              </div>
              <div class="stat-label">{{ card.label }}</div>
              <div class="stat-trend" v-if="card.trend !== undefined">
                <span :class="card.trend >= 0 ? 'trend-up' : 'trend-down'">
                  {{ card.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(card.trend) }}%
                </span>
                <span class="trend-label">较上月</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 碳排预警 + 排放饼图 -->
      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="8">
          <el-card class="alert-card" :class="{ 'alert-active': alertData.alert_count > 0 }">
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span><el-icon><Bell /></el-icon> 碳排预警</span>
                <el-tag v-if="alertData.alert_count > 0"
                  :type="alertData.danger_count > 0 ? 'danger' : 'warning'"
                  size="small" effect="dark" round>
                  {{ alertData.alert_count }} 条预警
                </el-tag>
                <el-tag v-else type="success" size="small" effect="dark" round>
                  <el-icon><CircleCheckFilled /></el-icon> 正常
                </el-tag>
              </div>
            </template>
            <div v-if="alertData.alerts && alertData.alerts.length > 0">
              <el-alert
                v-for="(alert, idx) in alertData.alerts.slice(0, 5)"
                :key="idx"
                :title="alert.message"
                :type="alert.level === 'danger' ? 'error' : alert.level === 'warning' ? 'warning' : 'info'"
                :closable="false" show-icon style="margin-bottom: 8px;border-radius:8px;"
              />
            </div>
            <div v-else style="text-align:center;padding:40px 0;color:#67c23a;">
              <el-icon :size="56"><CircleCheckFilled /></el-icon>
              <div style="margin-top:12px;font-size:15px;font-weight:500;">碳排放状况正常，无预警</div>
            </div>
            <div v-if="alertData.current_month_data" style="margin-top:16px;font-size:13px;color:#909399;display:flex;justify-content:space-between;">
              <span>当月排放: <b>{{ alertData.current_month_data.total }}</b> kgCO₂</span>
              <span v-if="alertData.last_month_data && alertData.last_month_data.total > 0">
                上月: {{ alertData.last_month_data.total }} kgCO₂
              </span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header><span><el-icon><PieChart /></el-icon> 排放结构分布</span></template>
            <div ref="pieChart" style="height: 340px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 月度排放趋势 -->
      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <span><el-icon><TrendCharts /></el-icon> 月度排放趋势</span>
            </template>
            <div ref="lineChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 排放源排行 + 最近记录 -->
      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header><span><el-icon><Histogram /></el-icon> 排放源排行</span></template>
            <div ref="barChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="table-card">
            <template #header><span><el-icon><Document /></el-icon> 最近碳排放记录</span></template>
            <el-table :data="recentRecords" stripe size="small" max-height="340" style="width:100%;">
              <el-table-column prop="record_date" label="月份" width="100" />
              <el-table-column prop="scope" label="范围" width="90">
                <template #default="{ row }">
                  <el-tag :type="row.scope === 'scope1' ? 'danger' : row.scope === 'scope2' ? 'warning' : 'success'" size="small" effect="dark" round>
                    {{ scopeLabel(row.scope) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="emission_source" label="排放源" width="100">
                <template #default="{ row }">{{ sourceLabel(row.emission_source) }}</template>
              </el-table-column>
              <el-table-column prop="quantity" label="消耗量" width="90" />
              <el-table-column prop="co2_emission" label="kgCO₂">
                <template #default="{ row }">
                  <span style="color: #409eff; font-weight: bold;">{{ row.co2_emission }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'
import {
  OfficeBuilding, Coin, DataLine, TrendCharts, Bell, CircleCheckFilled,
  PieChart, Histogram, Document
} from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'

const loading = ref(true)
setTimeout(() => { loading.value = false }, 800) // 模拟加载

const stats = reactive({ companies: 0, records: 0, totalEmission: 0, reduction: 0 })
const recentRecords = ref([])
const alertData = reactive({ alert_count: 0, danger_count: 0, warning_count: 0, info_count: 0, alerts: [], current_month_data: null, last_month_data: null })
const pieChart = ref(null)
const lineChart = ref(null)
const barChart = ref(null)

// 统计卡片配置
const statCards = ref([
  { label: '企业数量', value: 0, unit: '家', icon: markRaw(OfficeBuilding), gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', trend: undefined },
  { label: '碳记录数', value: 0, unit: '条', icon: markRaw(Coin), gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', trend: undefined },
  { label: '碳排放总量', value: 0, unit: 'kgCO₂', icon: markRaw(DataLine), gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', trend: undefined },
  { label: '减排潜力', value: 0, unit: 'kg', icon: markRaw(TrendCharts), gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', trend: 15 },
])

const counterRefs = []
function setCounterRef(el, idx) {
  if (el) counterRefs[idx] = el
}

// 数字滚动动画
function animateCounter(el, target, duration = 1600) {
  if (!el) return
  const start = 0
  const startTime = performance.now()
  const isFloat = String(target).includes('.')
  const decimalPlaces = isFloat ? String(target).split('.')[1].length : 0

  function update(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    // easeOutExpo
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    const current = start + (target - start) * eased
    el.textContent = isFloat ? current.toFixed(decimalPlaces) : Math.floor(current)
    if (progress < 1) requestAnimationFrame(update)
  }
  requestAnimationFrame(update)
}

const scopeLabelMap = { scope1: '范围1', scope2: '范围2', scope3: '范围3' }
const sourceLabelMap = {
  natural_gas: '天然气', coal: '煤炭', electricity: '电力', gasoline: '汽油',
  diesel: '柴油', renewable: '绿电', business_flight_short: '短途航班',
  business_flight_medium: '中途航班', business_flight_long: '长途航班',
  business_train: '火车', business_car: '公务车', waste_landfill: '填埋',
  waste_incineration: '焚烧', waste_composting: '堆肥',
  purchased_office: '办公用品', purchased_equipment: '设备采购'
}
const scopeLabel = (s) => scopeLabelMap[s] || s
const sourceLabel = (s) => sourceLabelMap[s] || s

onMounted(async () => {
  let companies = [], records = []
  try {
    const [compRes, recordRes] = await Promise.all([
      fetch(`${API_BASE}/carbon/company/`),
      fetch(`${API_BASE}/carbon/records/`)
    ])
    companies = await compRes.json()
    records = await recordRes.json()
  } catch (e) {
    records = [
      { id: 1, company_id: 1, record_date: '2026-04', scope: 'scope2', emission_source: 'electricity', quantity: 1000, unit: 'kWh', co2_emission: 581 },
      { id: 2, company_id: 1, record_date: '2026-03', scope: 'scope2', emission_source: 'electricity', quantity: 950, unit: 'kWh', co2_emission: 551.95 },
      { id: 3, company_id: 1, record_date: '2026-02', scope: 'scope1', emission_source: 'natural_gas', quantity: 500, unit: 'm3', co2_emission: 1045 },
      { id: 4, company_id: 1, record_date: '2026-01', scope: 'scope1', emission_source: 'diesel', quantity: 200, unit: 'L', co2_emission: 526 },
      { id: 5, company_id: 1, record_date: '2026-05', scope: 'scope3', emission_source: 'business_flight_short', quantity: 2, unit: '次', co2_emission: 800 },
    ]
    companies = [{ id: 1, name: '示例企业' }]
  }

  stats.companies = companies.length
  stats.records = records.length
  recentRecords.value = records.slice(-10).reverse()

  if (records.length > 0) {
    stats.totalEmission = parseFloat(records.reduce((sum, r) => sum + (parseFloat(r.co2_emission) || 0), 0).toFixed(2))
    stats.reduction = parseFloat((stats.totalEmission * 0.15).toFixed(2))
  }

  // 更新卡片数值并触发动画
  statCards.value[0].value = stats.companies
  statCards.value[1].value = stats.records
  statCards.value[2].value = stats.totalEmission
  statCards.value[3].value = stats.reduction

  await nextTick()

  // 启动数字滚动动画
  setTimeout(() => {
    counterRefs.forEach((el, idx) => {
      if (el) animateCounter(el, statCards.value[idx].value)
    })
  }, 300)

  renderCharts(records)
  loadAlerts()
})

async function loadAlerts() {
  try {
    const res = await fetch(`${API_BASE}/alert/check/1/`)
    const data = await res.json()
    Object.assign(alertData, data)
  } catch (e) {
    console.error('加载预警数据失败', e)
  }
}

let chartInstances = []

function renderCharts(records) {
  // 销毁旧图表
  chartInstances.forEach(c => c.dispose?.())
  chartInstances = []

  // === 饼图：排放结构 ===
  const scopeData = [
    { value: records.filter(r => r.scope === 'scope1').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围1 直接排放', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#e74c3c' }, { offset: 1, color: '#c0392b' }]) } },
    { value: records.filter(r => r.scope === 'scope2').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围2 能源间接', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#f39c12' }, { offset: 1, color: '#e67e22' }]) } },
    { value: records.filter(r => r.scope === 'scope3').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围3 其他间接', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#27ae60' }, { offset: 1, color: '#2ecc71' }]) } },
  ].filter(d => d.value > 0)

  if (pieChart.value) {
    const pie = markRaw(echarts.init(pieChart.value))
    chartInstances.push(pie)
    pie.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO₂ ({d}%)', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      legend: { bottom: 0, textStyle: { fontSize: 12, color: '#606266' }, icon: 'circle', itemWidth: 10, itemHeight: 10 },
      series: [{
        type: 'pie', radius: ['35%', '68%'], center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { formatter: '{b}\n{d}%', fontSize: 12, lineHeight: 20 },
        emphasis: {
          label: { fontSize: 16, fontWeight: 'bold' },
          itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.3)' }
        },
        data: scopeData,
        animationType: 'scale',
        animationEasing: 'elasticOut',
        animationDelay: (idx) => idx * 200
      }]
    })
    window.addEventListener('resize', () => pie.resize())
  }

  // === 折线图：月度趋势 ===
  const monthlyMap = {}
  records.forEach(r => {
    const month = r.record_date?.slice(0, 7) || '未知'
    if (!monthlyMap[month]) monthlyMap[month] = { scope1: 0, scope2: 0, scope3: 0 }
    monthlyMap[month][r.scope] = (monthlyMap[month][r.scope] || 0) + (parseFloat(r.co2_emission) || 0)
  })
  const months = Object.keys(monthlyMap).sort()

  if (lineChart.value) {
    const line = markRaw(echarts.init(lineChart.value))
    chartInstances.push(line)
    line.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      legend: { data: ['范围1', '范围2', '范围3'], bottom: 0, textStyle: { fontSize: 12 } },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11, color: '#909399' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
      yAxis: { type: 'value', name: 'kgCO₂', nameTextStyle: { fontSize: 11, color: '#909399' }, axisLabel: { fontSize: 11, color: '#909399' }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } } },
      series: [
        {
          name: '范围1', type: 'line', smooth: true,
          data: months.map(m => monthlyMap[m].scope1.toFixed(2)),
          itemStyle: { color: '#e74c3c' },
          lineStyle: { width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(231,76,60,0.3)' }, { offset: 1, color: 'rgba(231,76,60,0.01)' }]) },
          symbol: 'circle', symbolSize: 8,
        },
        {
          name: '范围2', type: 'line', smooth: true,
          data: months.map(m => monthlyMap[m].scope2.toFixed(2)),
          itemStyle: { color: '#f39c12' },
          lineStyle: { width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(243,156,18,0.3)' }, { offset: 1, color: 'rgba(243,156,18,0.01)' }]) },
          symbol: 'circle', symbolSize: 8,
        },
        {
          name: '范围3', type: 'line', smooth: true,
          data: months.map(m => monthlyMap[m].scope3.toFixed(2)),
          itemStyle: { color: '#27ae60' },
          lineStyle: { width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(39,174,96,0.3)' }, { offset: 1, color: 'rgba(39,174,96,0.01)' }]) },
          symbol: 'circle', symbolSize: 8,
        },
      ],
      animationDuration: 2000,
      animationEasing: 'cubicOut',
    })
    window.addEventListener('resize', () => line.resize())
  }

  // === 柱状图：排放源排行 ===
  const sourceMap = {}
  records.forEach(r => {
    const src = sourceLabel(r.emission_source)
    sourceMap[src] = (sourceMap[src] || 0) + (parseFloat(r.co2_emission) || 0)
  })
  const sortedSources = Object.entries(sourceMap).sort((a, b) => b[1] - a[1]).slice(0, 8)

  if (barChart.value) {
    const bar = markRaw(echarts.init(barChart.value))
    chartInstances.push(bar)
    bar.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} kgCO₂', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      grid: { left: '3%', right: '10%', bottom: '3%', top: '5%', containLabel: true },
      xAxis: { type: 'value', name: 'kgCO₂', nameTextStyle: { fontSize: 11, color: '#909399' }, axisLabel: { fontSize: 11, color: '#909399' }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } } },
      yAxis: { type: 'category', data: sortedSources.map(s => s[0]).reverse(), axisLabel: { fontSize: 12, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
      series: [{
        type: 'bar',
        data: sortedSources.map(s => ({ value: s[1].toFixed(2), itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }]) } })).reverse(),
        itemStyle: { borderRadius: [0, 8, 8, 0] },
        barWidth: '55%',
        label: { show: true, position: 'right', fontSize: 11, color: '#606266', fontWeight: 500 },
        animationDuration: 1500,
        animationEasing: 'elasticOut',
        animationDelay: (idx) => idx * 150
      }]
    })
    window.addEventListener('resize', () => bar.resize())
  }
}

onUnmounted(() => {
  chartInstances.forEach(c => c.dispose?.())
})
</script>

<style scoped>
.dashboard { padding: 24px; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }

/* 骨架屏 */
.skeleton-wrapper { padding: 20px; }

/* 统计卡片 */
.stats-row { margin-top: 4px; }
.stat-card {
  display: flex; align-items: center; gap: 18px; padding: 20px 18px;
  border-radius: 16px; border: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer; position: relative; overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  opacity: 0; transition: opacity 0.3s;
}
.stat-card:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 12px 40px rgba(0,0,0,0.12); }
.stat-card:hover::before { opacity: 1; }
.stat-icon {
  width: 64px; height: 64px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center; color: #fff;
  flex-shrink: 0;
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.stat-content { flex: 1; }
.stat-value { font-size: 28px; font-weight: 800; color: #303133; line-height: 1.2; display: flex; align-items: baseline; gap: 4px; }
.stat-unit { font-size: 13px; color: #909399; font-weight: 400; }
.stat-label { font-size: 14px; color: #909399; margin-top: 6px; }
.stat-trend { margin-top: 6px; font-size: 12px; }
.trend-up { color: #f56c6c; font-weight: 600; }
.trend-down { color: #67c23a; font-weight: 600; }
.trend-label { color: #c0c4cc; margin-left: 4px; }

/* 卡片统一样式 */
.chart-card, .table-card, .alert-card {
  border-radius: 16px; border: none;
  transition: all 0.3s ease;
}
.chart-card:hover, .table-card:hover {
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}
.alert-card {
  height: 100%;
}
.alert-active {
  border-left: 4px solid #f56c6c;
}

/* 表格 */
:deep(.el-table) { border-radius: 8px; }
:deep(.el-table th) { background: #f5f7fa !important; color: #606266; font-size: 13px; }
:deep(.el-table__row) { transition: background 0.2s; }
:deep(.el-table__row:hover) { background: #ecf5ff !important; }

/* 标题图标 */
:deep(.el-card__header) {
  font-size: 15px; font-weight: 600; color: #303133;
  border-bottom: 1px solid #f0f0f0; padding: 14px 18px;
}
:deep(.el-card__header span) { display: flex; align-items: center; gap: 6px; }
:deep(.el-card__body) { padding: 18px; }

/* 全局动画 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.stats-row .el-col:nth-child(1) .stat-card { animation: fadeInUp 0.5s ease both; }
.stats-row .el-col:nth-child(2) .stat-card { animation: fadeInUp 0.5s 0.1s ease both; }
.stats-row .el-col:nth-child(3) .stat-card { animation: fadeInUp 0.5s 0.2s ease both; }
.stats-row .el-col:nth-child(4) .stat-card { animation: fadeInUp 0.5s 0.3s ease both; }
</style>
