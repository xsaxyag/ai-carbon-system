<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #409eff, #337ecc);">
            <el-icon :size="32"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.companies }}</div>
            <div class="stat-label">企业数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #67c23a, #529b2e);">
            <el-icon :size="32"><Coin /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.records }}</div>
            <div class="stat-label">碳记录数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6a23c, #cf8e24);">
            <el-icon :size="32"><DataLine /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalEmission }}</div>
            <div class="stat-label">碳排放总量(kgCO2)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f56c6c, #dd4a4a);">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.reduction }}</div>
            <div class="stat-label">减排潜力(kg)</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 碳排预警 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span>碳排预警</span>
              <el-tag v-if="alertData.alert_count > 0" :type="alertData.danger_count > 0 ? 'danger' : alertData.warning_count > 0 ? 'warning' : 'info'" size="small">
                {{ alertData.alert_count }} 条预警
              </el-tag>
              <el-tag v-else type="success" size="small">正常</el-tag>
            </div>
          </template>
          <div v-if="alertData.alerts && alertData.alerts.length > 0">
            <el-alert
              v-for="(alert, idx) in alertData.alerts.slice(0, 5)"
              :key="idx"
              :title="alert.message"
              :type="alert.level === 'danger' ? 'error' : alert.level === 'warning' ? 'warning' : 'info'"
              :closable="false"
              show-icon
              style="margin-bottom: 8px;"
            />
          </div>
          <div v-else style="text-align:center;padding:40px 0;color:#67c23a;">
            <el-icon :size="48"><CircleCheckFilled /></el-icon>
            <div style="margin-top:12px;font-size:14px;">碳排放状况正常，无预警</div>
          </div>
          <div v-if="alertData.current_month_data" style="margin-top:12px;font-size:12px;color:#909399;">
            当月排放: {{ alertData.current_month_data.total }} kgCO2
            <span v-if="alertData.last_month_data && alertData.last_month_data.total > 0">
              | 上月: {{ alertData.last_month_data.total }} kgCO2
            </span>
          </div>
        </el-card>
      </el-col>
      <!-- 排放结构饼图 -->
      <el-col :span="16">
        <el-card>
          <template #header><span>排放结构分布</span></template>
          <div ref="pieChart" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度排放趋势 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header><span>月度排放趋势</span></template>
          <div ref="lineChart" style="height: 280px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行图表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 排放源柱状图 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>排放源排行</span></template>
          <div ref="barChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <!-- 数据表格 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>最近碳排放记录</span></template>
          <el-table :data="recentRecords" stripe size="small" max-height="300">
            <el-table-column prop="record_date" label="月份" width="90" />
            <el-table-column prop="scope" label="范围" width="80">
              <template #default="{ row }">
                <el-tag :type="row.scope === 'scope1' ? 'danger' : row.scope === 'scope2' ? 'warning' : 'success'" size="small">
                  {{ scopeLabel(row.scope) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="emission_source" label="排放源" width="100">
              <template #default="{ row }">{{ sourceLabel(row.emission_source) }}</template>
            </el-table-column>
            <el-table-column prop="quantity" label="消耗量" width="80" />
            <el-table-column prop="co2_emission" label="kgCO2">
              <template #default="{ row }">
                <span style="color: #409eff; font-weight: bold;">{{ row.co2_emission }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import { CircleCheckFilled } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'

const stats = reactive({ companies: 0, records: 0, totalEmission: 0, reduction: 0 })
const recentRecords = ref([])
const alertData = reactive({ alert_count: 0, danger_count: 0, warning_count: 0, info_count: 0, alerts: [], current_month_data: null, last_month_data: null })
const pieChart = ref(null)
const lineChart = ref(null)
const barChart = ref(null)

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
      { id: 4, company_id: 1, record_date: '2026-01', scope: 'scope1', emission_source: 'diesel', quantity: 200, unit: 'L', co2_emission: 526 }
    ]
    companies = [{ id: 1, name: '示例企业' }]
  }

  stats.companies = companies.length
  stats.records = records.length
  recentRecords.value = records.slice(-10).reverse()
  
  if (records.length > 0) {
    stats.totalEmission = records.reduce((sum, r) => sum + (parseFloat(r.co2_emission) || 0), 0).toFixed(2)
    stats.reduction = (stats.totalEmission * 0.15).toFixed(2)
  }

  await nextTick()
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

function renderCharts(records) {
  // === 饼图：排放结构 ===
  const scopeData = [
    { value: records.filter(r => r.scope === 'scope1').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围1 直接排放', itemStyle: { color: '#e74c3c' } },
    { value: records.filter(r => r.scope === 'scope2').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围2 间接排放', itemStyle: { color: '#f39c12' } },
    { value: records.filter(r => r.scope === 'scope3').reduce((s, r) => s + (parseFloat(r.co2_emission) || 0), 0), name: '范围3 其他间接', itemStyle: { color: '#27ae60' } },
  ].filter(d => d.value > 0)

  if (pieChart.value) {
    const pie = echarts.init(pieChart.value)
    pie.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO2 ({d}%)' },
      legend: { bottom: 0, textStyle: { fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
        label: { formatter: '{d}%', fontSize: 11 },
        emphasis: { label: { fontSize: 14, fontWeight: 'bold' } },
        data: scopeData
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
    const line = echarts.init(lineChart.value)
    line.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['范围1', '范围2', '范围3'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', name: 'kgCO2', axisLabel: { fontSize: 11 } },
      series: [
        { name: '范围1', type: 'line', smooth: true, data: months.map(m => monthlyMap[m].scope1.toFixed(2)), itemStyle: { color: '#e74c3c' }, areaStyle: { opacity: 0.1 } },
        { name: '范围2', type: 'line', smooth: true, data: months.map(m => monthlyMap[m].scope2.toFixed(2)), itemStyle: { color: '#f39c12' }, areaStyle: { opacity: 0.1 } },
        { name: '范围3', type: 'line', smooth: true, data: months.map(m => monthlyMap[m].scope3.toFixed(2)), itemStyle: { color: '#27ae60' }, areaStyle: { opacity: 0.1 } },
      ]
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
    const bar = echarts.init(barChart.value)
    bar.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} kgCO2' },
      grid: { left: '3%', right: '10%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'value', name: 'kgCO2' },
      yAxis: { type: 'category', data: sortedSources.map(s => s[0]).reverse(), axisLabel: { fontSize: 11 } },
      series: [{
        type: 'bar',
        data: sortedSources.map(s => s[1].toFixed(2)).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#67c23a' }
          ])
        },
        barWidth: '60%',
        label: { show: true, position: 'right', fontSize: 10 }
      }]
    })
    window.addEventListener('resize', () => bar.resize())
  }
}
</script>

<style scoped>
.dashboard { padding: 20px; }
h2 { margin-bottom: 20px; color: #303133; }
.stats-row { margin-top: 10px; }
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 60px; height: 60px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.stat-content { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
</style>
