<template>
  <div class="carbon-report">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="32"><DocumentCopy /></el-icon>
        </div>
        <div>
          <h2>碳排放报告</h2>
          <p class="header-desc">生成企业碳排放报告，支持多格式导出与可视化分析</p>
        </div>
      </div>
    </div>

    <!-- 筛选条件卡片 -->
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Filter /></el-icon>
            <span>报告筛选</span>
          </div>
        </div>
      </template>
      <el-form :inline="true" size="large">
        <el-form-item label="选择企业" class="form-item-icon">
          <el-icon style="margin-right:6px;color:#409eff;"><OfficeBuilding /></el-icon>
          <el-select v-model="selectedCompany" placeholder="请选择企业" filterable @change="loadReport" style="width: 200px;">
            <el-option v-for="company in companies" :key="company.id" :label="company.name" :value="company.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告类型" class="form-item-icon">
          <el-icon style="margin-right:6px;color:#67c23a;"><Calendar /></el-icon>
          <el-radio-group v-model="reportType" @change="loadReport">
            <el-radio-button label="monthly">月度</el-radio-button>
            <el-radio-button label="quarterly">季度</el-radio-button>
            <el-radio-button label="annual">年度</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReport" :loading="loading" size="large" round style="min-width: 120px;">
            <el-icon><DataAnalysis /></el-icon> 生成报告
          </el-button>
          <el-dropdown @command="handleExport" style="margin-left: 10px;" trigger="click">
            <el-button size="large" round>
              <el-icon><Download /></el-icon> 导出<i class="el-icon--right"><ArrowDown /></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf"><el-icon><PictureFilled /></el-icon> PDF 报告</el-dropdown-item>
                <el-dropdown-item command="excel"><el-icon><Grid /></el-icon> Excel 报告</el-dropdown-item>
                <el-dropdown-item command="csv"><el-icon><Document /></el-icon> CSV 数据</el-dropdown-item>
                <el-dropdown-item command="json"><el-icon><Files /></el-icon> JSON 数据</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告内容 -->
    <transition name="el-fade-in-linear">
      <div v-if="report">
        <!-- 排放汇总卡片 -->
        <el-row :gutter="20" class="summary-row" style="margin-top: 24px;">
          <el-col :span="6" v-for="(card, idx) in summaryCards" :key="idx">
            <div class="summary-card" :class="card.cssClass" :style="{ animationDelay: (idx * 0.1) + 's' }">
              <div class="card-icon" :style="{ background: card.iconGradient }">
                <el-icon :size="24"><component :is="card.icon" /></el-icon>
              </div>
              <div class="card-body">
                <div class="card-value">
                  <span class="counter" :ref="el => setSummaryCounterRef(el, idx)">0</span>
                  <span class="card-unit">{{ card.unit }}</span>
                </div>
                <div class="card-label">{{ card.label }}</div>
              </div>
              <div class="card-bar" :style="{ width: card.barWidth + '%', background: card.barColor }"></div>
            </div>
          </el-col>
        </el-row>

        <!-- 图表区域 -->
        <el-row :gutter="24" style="margin-top: 24px;">
          <!-- 瀑布图：排放结构 -->
          <el-col :span="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <el-icon><Histogram /></el-icon>
                  <span>排放结构瀑布图</span>
                </div>
              </template>
              <div ref="waterfallChart" style="height: 320px;"></div>
            </el-card>
          </el-col>
          <!-- 饼图：排放源分布 -->
          <el-col :span="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <el-icon><PieChart /></el-icon>
                  <span>排放源分布</span>
                </div>
              </template>
              <div ref="sourcePieChart" style="height: 320px;"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 月度趋势折线图 -->
        <el-card shadow="hover" class="chart-card" style="margin-top: 24px;">
          <template #header>
            <div class="chart-header">
              <el-icon><TrendCharts /></el-icon>
              <span>月度排放趋势</span>
            </div>
          </template>
          <div ref="trendChart" style="height: 320px;"></div>
        </el-card>

        <!-- 雷达图：行业基准对比 + 减排建议 -->
        <el-row :gutter="24" style="margin-top: 24px;">
          <el-col :span="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>行业基准对比</span>
                </div>
              </template>
              <div ref="radarChart" style="height: 320px;"></div>
            </el-card>
          </el-col>
          <!-- 减排建议 -->
          <el-col :span="12">
            <el-card shadow="hover" class="suggestion-card">
              <template #header>
                <div class="chart-header">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>AI 减排建议</span>
                  <el-tag v-if="report.suggestions && report.suggestions.length > 0" type="success" size="small" effect="dark" round style="margin-left: 8px;">
                    {{ report.suggestions.length }} 条建议
                  </el-tag>
                </div>
              </template>
              <div v-if="report.suggestions && report.suggestions.length > 0" class="suggestion-list">
                <div v-for="(sug, i) in report.suggestions" :key="i" class="suggestion-item" :style="{ animationDelay: (i * 0.1) + 's' }">
                  <div class="sug-header">
                    <div class="sug-icon">
                      <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
                    </div>
                    <div class="sug-title">{{ sug.title }}</div>
                    <el-tag size="small" type="success" effect="dark" round>减排 {{ sug.potential }} kgCO₂</el-tag>
                  </div>
                  <div class="sug-desc">{{ sug.description }}</div>
                </div>
              </div>
              <el-empty v-else description="暂无减排建议" :image-size="80" />
            </el-card>
          </el-col>
        </el-row>

        <div class="report-footer">
          <el-icon><InfoFilled /></el-icon>
          <span>共 {{ report.summary.record_count }} 条碳记录 · 报告生成于 {{ report.generated_at?.slice(0, 19) }}</span>
        </div>
      </div>
    </transition>

    <!-- 空状态 -->
    <el-card v-if="!report && !loading" class="empty-card" shadow="hover">
      <el-empty description="请选择企业后生成报告">
        <el-button type="primary" @click="loadCompanies" size="large" round>
          <el-icon><OfficeBuilding /></el-icon> 加载企业列表
        </el-button>
      </el-empty>
    </el-card>

    <!-- 加载状态 -->
    <el-card v-if="loading" class="loading-card" shadow="hover">
      <el-skeleton :rows="6" animated />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DocumentCopy, Filter, OfficeBuilding, Calendar, DataAnalysis, Download, ArrowDown,
  PictureFilled, Grid, Document, Files, Histogram, PieChart, TrendCharts, ChatDotRound, CircleCheckFilled, InfoFilled,
  Flag, Lightning, Connection
} from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'

const loading = ref(false)
const companies = ref([])
const selectedCompany = ref(null)
const reportType = ref('monthly')
const report = ref(null)

const waterfallChart = ref(null)
const sourcePieChart = ref(null)
const trendChart = ref(null)
const radarChart = ref(null)
let chartInstances = []

// 排放源标签映射
const sourceLabelMap = {
  natural_gas: '天然气', coal: '煤炭', electricity: '外购电力',
  gasoline: '汽油', diesel: '柴油', renewable: '可再生能源',
  business_flight_short: '短途航班', business_flight_medium: '中途航班',
  business_flight_long: '长途航班', business_train: '火车', business_car: '公务车',
  waste_landfill: '填埋', waste_incineration: '焚烧', waste_composting: '堆肥',
  purchased_office: '办公用品', purchased_equipment: '设备采购'
}

// 汇总卡片数据
const summaryCards = computed(() => {
  if (!report.value) return []
  const s = report.value.summary
  const total = s.total_emission || 0
  return [
    {
      label: '总排放量', value: total, unit: 'kgCO₂',
      icon: markRaw(DataAnalysis), cssClass: 'total',
      iconGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      barWidth: 100, barColor: 'linear-gradient(90deg, #667eea, #764ba2)'
    },
    {
      label: '范围1 直接排放', value: s.scope1 || 0, unit: 'kgCO₂',
      icon: markRaw(Flag), cssClass: 'scope1',
      iconGradient: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
      barWidth: total > 0 ? ((s.scope1 || 0) / total * 100) : 0,
      barColor: 'linear-gradient(90deg, #e74c3c, #c0392b)'
    },
    {
      label: '范围2 间接排放', value: s.scope2 || 0, unit: 'kgCO₂',
      icon: markRaw(Lightning), cssClass: 'scope2',
      iconGradient: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)',
      barWidth: total > 0 ? ((s.scope2 || 0) / total * 100) : 0,
      barColor: 'linear-gradient(90deg, #f39c12, #e67e22)'
    },
    {
      label: '范围3 其他间接', value: s.scope3 || 0, unit: 'kgCO₂',
      icon: markRaw(Connection), cssClass: 'scope3',
      iconGradient: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
      barWidth: total > 0 ? ((s.scope3 || 0) / total * 100) : 0,
      barColor: 'linear-gradient(90deg, #27ae60, #2ecc71)'
    }
  ]
})

const summaryCounterRefs = []
function setSummaryCounterRef(el, idx) { if (el) summaryCounterRefs[idx] = el }

function animateCounter(el, target, duration = 1600) {
  if (!el) return
  const start = 0
  const startTime = performance.now()
  const isFloat = String(target).includes('.')
  const decimalPlaces = isFloat ? String(target).split('.')[1].length : 0
  function update(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    const current = start + (target - start) * eased
    el.textContent = isFloat ? current.toFixed(decimalPlaces) : Math.floor(current)
    if (progress < 1) requestAnimationFrame(update)
  }
  requestAnimationFrame(update)
}

const reportTypeName = computed(() => {
  return { monthly: '月度', quarterly: '季度', annual: '年度' }[reportType.value] || '月度'
})

onMounted(() => { loadCompanies() })

async function loadCompanies() {
  try {
    const res = await fetch(`${API_BASE}/carbon/company/`)
    companies.value = await res.json()
    if (companies.value.length > 0 && !selectedCompany.value) {
      selectedCompany.value = companies.value[0].id
      loadReport()
    }
  } catch (e) {
    companies.value = []
    ElMessage.error('加载企业列表失败')
  }
}

async function loadReport() {
  if (!selectedCompany.value) { ElMessage.warning('请先选择企业'); return }
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/report/report/${selectedCompany.value}/?report_type=${reportType.value}`)
    report.value = await res.json()
    await nextTick()
    renderCharts()
    // 启动数字滚动动画
    setTimeout(() => {
      summaryCounterRefs.forEach((el, idx) => {
        if (el && summaryCards.value[idx]) animateCounter(el, summaryCards.value[idx].value)
      })
    }, 300)
  } catch (e) {
    ElMessage.error('加载报告失败')
    report.value = null
  }
  loading.value = false
}

async function handleExport(format) {
  if (!selectedCompany.value) return
  try {
    let url = '', filename = ''
    if (format === 'pdf') {
      url = `${API_BASE}/report/export-pdf/${selectedCompany.value}/?report_type=${reportType.value}`
      filename = `carbon_report_${selectedCompany.value}.pdf`
    } else if (format === 'excel') {
      url = `${API_BASE}/report/export-excel/${selectedCompany.value}/?report_type=${reportType.value}`
      filename = `carbon_report_${selectedCompany.value}.xlsx`
    } else if (format === 'csv') {
      const res = await fetch(`${API_BASE}/report/export/${selectedCompany.value}/?format=csv`)
      const data = await res.json()
      const blob = new Blob([data.content], { type: 'text/csv;charset=utf-8' })
      const downloadUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = data.filename || `carbon_report_${selectedCompany.value}.csv`
      a.click()
      URL.revokeObjectURL(downloadUrl)
      ElMessage.success('CSV导出成功')
      return
    } else {
      const res = await fetch(`${API_BASE}/report/export/${selectedCompany.value}/?format=json`)
      const data = await res.json()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const downloadUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `carbon_report_${selectedCompany.value}.json`
      a.click()
      URL.revokeObjectURL(downloadUrl)
      ElMessage.success('JSON导出成功')
      return
    }

    const res = await fetch(url)
    if (!res.ok) throw new Error('导出失败')
    const blob = await res.blob()
    const downloadUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename
    a.click()
    URL.revokeObjectURL(downloadUrl)
    ElMessage.success(`${format.toUpperCase()}导出成功`)
  } catch (e) {
    ElMessage.error('导出失败: ' + e.message)
  }
}

function renderCharts() {
  if (!report.value) return
  const { summary, monthly_data, source_data } = report.value

  chartInstances.forEach(c => c.dispose?.())
  chartInstances = []

  // === 瀑布图：排放结构 ===
  if (waterfallChart.value) {
    const chart = markRaw(echarts.init(waterfallChart.value))
    chartInstances.push(chart)
    const s1 = summary.scope1 || 0, s2 = summary.scope2 || 0, s3 = summary.scope3 || 0
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const p = params[0]
          if (p.name === '范围1') return `范围1 直接排放: <b>${s1.toFixed(2)}</b> kgCO₂`
          if (p.name === '范围2') return `范围2 间接排放: <b>${s2.toFixed(2)}</b> kgCO₂`
          if (p.name === '范围3') return `范围3 其他间接: <b>${s3.toFixed(2)}</b> kgCO₂`
          return `总排放: <b>${summary.total_emission.toFixed(2)}</b> kgCO₂`
        },
        backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: ['范围1', '范围2', '范围3', '总排放'], axisLabel: { fontSize: 11, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
      yAxis: { type: 'value', name: 'kgCO₂', nameTextStyle: { fontSize: 11, color: '#909399' }, axisLabel: { fontSize: 11, color: '#909399' }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } } },
      series: [{
        type: 'bar', barWidth: '50%',
        label: {
          show: true, position: 'top', fontSize: 11, color: '#303133', fontWeight: 500,
          formatter: (p) => {
            if (p.name === '范围1') return s1.toFixed(1)
            if (p.name === '范围2') return s2.toFixed(1)
            if (p.name === '范围3') return s3.toFixed(1)
            return summary.total_emission.toFixed(1)
          }
        },
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params) => {
            const colors = [
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#e74c3c' }, { offset: 1, color: '#c0392b' }]),
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f39c12' }, { offset: 1, color: '#e67e22' }]),
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#27ae60' }, { offset: 1, color: '#2ecc71' }]),
              new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#3498db' }, { offset: 1, color: '#2980b9' }])
            ]
            return colors[params.dataIndex] || '#409eff'
          }
        },
        data: [s1, s2, s3, summary.total_emission]
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 饼图：排放源分布 ===
  if (sourcePieChart.value) {
    const chart = markRaw(echarts.init(sourcePieChart.value))
    chartInstances.push(chart)
    const colors = ['#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#2ecc71', '#34495e', '#16a085']
    const pieData = Object.entries(source_data || {}).map(([k, v], i) => ({
      value: parseFloat(v.toFixed(2)),
      name: sourceLabelMap[k] || k,
      itemStyle: { color: colors[i % colors.length] }
    })).sort((a, b) => b.value - a.value)

    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO₂ ({d}%)', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      legend: { type: 'scroll', bottom: 0, textStyle: { fontSize: 11, color: '#606266' }, icon: 'circle', itemWidth: 10, itemHeight: 10 },
      series: [{
        type: 'pie', radius: ['35%', '68%'], center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { formatter: '{b}\n{d}%', fontSize: 11, lineHeight: 18 },
        emphasis: { label: { fontSize: 16, fontWeight: 'bold' }, itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
        data: pieData,
        animationType: 'scale', animationEasing: 'elasticOut', animationDelay: (idx) => idx * 200
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 折线图：月度趋势 ===
  if (trendChart.value) {
    const chart = markRaw(echarts.init(trendChart.value))
    chartInstances.push(chart)
    const months = Object.keys(monthly_data || {}).sort()
    chart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11, color: '#909399' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
      yAxis: { type: 'value', name: 'kgCO₂', nameTextStyle: { fontSize: 11, color: '#909399' }, axisLabel: { fontSize: 11, color: '#909399' }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } } },
      series: [{
        type: 'line', smooth: true,
        data: months.map(m => parseFloat((monthly_data[m] || 0).toFixed(2))),
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.02)' }]) },
        itemStyle: { color: '#409eff' },
        lineStyle: { width: 3 },
        symbol: 'circle', symbolSize: 8,
        animationDuration: 2000, animationEasing: 'cubicOut'
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 雷达图：行业基准对比 ===
  if (radarChart.value && summary.total_emission > 0) {
    const chart = markRaw(echarts.init(radarChart.value))
    chartInstances.push(chart)
    const industry = report.value.company?.industry || '制造业'
    const employeeCount = report.value.company?.employee_count || 50
    const intensity = summary.total_emission / employeeCount
    const benchmarkAvg = { '制造业': 0.85, '纺织业': 1.2, '零售业': 0.35, '科技': 0.25 }[industry] || 0.58
    const benchmarkAdv = benchmarkAvg * 0.65

    chart.setOption({
      tooltip: { backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      legend: { data: ['本企业', '行业平均', '先进水平'], bottom: 0, textStyle: { fontSize: 12, color: '#606266' } },
      radar: {
        indicator: [
          { name: '排放强度(tCO₂/人)', max: Math.max(benchmarkAvg * 2, intensity * 1.5) },
          { name: '范围1占比(%)', max: 100 },
          { name: '范围2占比(%)', max: 100 },
          { name: '范围3占比(%)', max: 100 },
          { name: '减排潜力(%)', max: 100 }
        ],
        shape: 'polygon',
        splitArea: { areaStyle: { color: ['#fff', '#f5f7fa'] } },
        splitLine: { lineStyle: { color: '#e4e8f0' } },
        axisName: { color: '#606266', fontSize: 11 }
      },
      series: [{
        type: 'radar',
        data: [
          {
            value: [intensity, (summary.scope1 / summary.total_emission * 100), (summary.scope2 / summary.total_emission * 100), (summary.scope3 / summary.total_emission * 100), 15],
            name: '本企业', itemStyle: { color: '#409eff' }, areaStyle: { opacity: 0.2, color: '#409eff' }, lineStyle: { width: 2 }
          },
          {
            value: [benchmarkAvg, 40, 45, 15, 25],
            name: '行业平均', itemStyle: { color: '#f39c12' }, areaStyle: { opacity: 0.1, color: '#f39c12' }, lineStyle: { width: 2, type: 'dashed' }
          },
          {
            value: [benchmarkAdv, 25, 40, 35, 35],
            name: '先进水平', itemStyle: { color: '#67c23a' }, areaStyle: { opacity: 0.1, color: '#67c23a' }, lineStyle: { width: 2, type: 'dashed' }
          }
        ]
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }
}

onUnmounted(() => { chartInstances.forEach(c => c.dispose?.()) })
</script>

<style scoped>
.carbon-report { padding: 24px; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }

/* 页面标题区 */
.page-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(102,126,234,0.25); animation: fadeInUp 0.6s ease both; }
.header-content { display: flex; align-items: center; gap: 20px; color: #fff; }
.header-icon { width: 64px; height: 64px; border-radius: 16px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
h2 { font-size: 26px; font-weight: 700; margin: 0; color: #fff; }
.header-desc { font-size: 14px; color: rgba(255,255,255,0.85); margin-top: 6px; }

/* 筛选卡片 */
.filter-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.1s ease both; }
.filter-card :deep(.el-card__header) { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); font-size: 16px; font-weight: 600; color: #303133; padding: 16px 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 8px; }
.form-item-icon { display: flex; align-items: center; }

/* 汇总卡片 */
.summary-row { margin-top: 4px; }
.summary-card {
  border-radius: 16px; padding: 20px; position: relative; overflow: hidden;
  background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: fadeInUp 0.5s ease both;
}
.summary-card:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 12px 40px rgba(0,0,0,0.12); }
.summary-card.total { border-top: 4px solid #667eea; }
.summary-card.scope1 { border-top: 4px solid #e74c3c; }
.summary-card.scope2 { border-top: 4px solid #f39c12; }
.summary-card.scope3 { border-top: 4px solid #27ae60; }
.card-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; margin-bottom: 12px; }
.card-body { }
.card-value { font-size: 26px; font-weight: 800; color: #303133; display: flex; align-items: baseline; gap: 4px; }
.card-unit { font-size: 12px; color: #909399; font-weight: 400; }
.card-label { font-size: 13px; color: #909399; margin-top: 4px; }
.card-bar { height: 4px; border-radius: 2px; margin-top: 12px; transition: width 0.8s ease; }

/* 图表卡片 */
.chart-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s ease both; }
.chart-card :deep(.el-card__header) { padding: 14px 20px; border-bottom: 1px solid #f0f0f0; }
.chart-header { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; color: #303133; }

/* 建议卡片 */
.suggestion-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.2s ease both; }
.suggestion-list { max-height: 280px; overflow-y: auto; }
.suggestion-item {
  padding: 14px 16px; margin-bottom: 10px; background: #f0f9eb; border-radius: 10px;
  border-left: 4px solid #67c23a; transition: all 0.3s; animation: fadeInUp 0.4s ease both;
}
.suggestion-item:hover { background: #e1f3d8; transform: translateX(4px); }
.sug-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.sug-icon { flex-shrink: 0; }
.sug-title { font-weight: 600; color: #303133; flex: 1; }
.sug-desc { font-size: 13px; color: #606266; padding-left: 28px; line-height: 1.6; }

/* 报告底部 */
.report-footer {
  margin-top: 24px; padding: 16px; text-align: center;
  color: #909399; font-size: 13px; border-top: 1px solid #ebeef5;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}

/* 空状态卡片 */
.empty-card, .loading-card { border-radius: 16px; border: none; margin-top: 24px; }

/* 下拉菜单图标 */
:deep(.el-dropdown-menu__item .el-icon) { margin-right: 6px; }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .carbon-report { padding: 12px; }
  .page-header { padding: 20px; }
  h2 { font-size: 22px; }
  .header-content { flex-direction: column; text-align: center; }
}
</style>
