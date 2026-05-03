<template>
  <div class="carbon-report">
    <h2>碳排放报告</h2>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="选择企业">
          <el-select v-model="selectedCompany" placeholder="请选择企业" filterable @change="loadReport">
            <el-option v-for="company in companies" :key="company.id" :label="company.name" :value="company.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告类型">
          <el-radio-group v-model="reportType" @change="loadReport">
            <el-radio-button label="monthly">月度</el-radio-button>
            <el-radio-button label="quarterly">季度</el-radio-button>
            <el-radio-button label="annual">年度</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReport" :loading="loading">生成报告</el-button>
          <el-dropdown @command="handleExport" style="margin-left: 8px;">
            <el-button>导出 <el-icon><ArrowDown /></el-icon></el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="json">JSON</el-dropdown-item>
                <el-dropdown-item command="csv">CSV</el-dropdown-item>
                <el-dropdown-item command="pdf">PDF 报告</el-dropdown-item>
                <el-dropdown-item command="excel">Excel 报告</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告内容 -->
    <template v-if="report">
      <!-- 排放汇总卡片 -->
      <el-row :gutter="16" class="summary-row">
        <el-col :span="6">
          <div class="summary-card total">
            <div class="summary-value">{{ report.summary.total_emission }}</div>
            <div class="summary-label">总排放量 (kgCO2)</div>
            <div class="summary-bar" :style="{ width: '100%' }"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card scope1">
            <div class="summary-value">{{ report.summary.scope1 }}</div>
            <div class="summary-label">范围1 直接排放</div>
            <div class="summary-bar" :style="{ width: scopePercent('scope1') + '%' }"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card scope2">
            <div class="summary-value">{{ report.summary.scope2 }}</div>
            <div class="summary-label">范围2 间接排放</div>
            <div class="summary-bar" :style="{ width: scopePercent('scope2') + '%' }"></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-card scope3">
            <div class="summary-value">{{ report.summary.scope3 }}</div>
            <div class="summary-label">范围3 其他间接</div>
            <div class="summary-bar" :style="{ width: scopePercent('scope3') + '%' }"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 瀑布图：排放结构 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>排放结构瀑布图</span></template>
            <div ref="waterfallChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
        <!-- 饼图：排放源分布 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>排放源分布</span></template>
            <div ref="sourcePieChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 月度趋势折线图 -->
      <el-card style="margin-top: 20px;">
        <template #header><span>月度排放趋势</span></template>
        <div ref="trendChart" style="height: 300px;"></div>
      </el-card>

      <!-- 雷达图：行业基准对比 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header><span>行业基准对比</span></template>
            <div ref="radarChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <!-- 减排建议 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>AI减排建议</span></template>
            <div v-if="report.suggestions && report.suggestions.length > 0">
              <div v-for="(sug, i) in report.suggestions" :key="i" class="suggestion-item">
                <div class="sug-header">
                  <el-icon color="#67c23a"><CircleCheck /></el-icon>
                  <span class="sug-title">{{ sug.title }}</span>
                  <el-tag size="small" type="success">减排 {{ sug.potential }} kgCO2</el-tag>
                </div>
                <div class="sug-desc">{{ sug.description }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无减排建议" :image-size="60" />
          </el-card>
        </el-col>
      </el-row>

      <div class="report-footer">
        <span>共 {{ report.summary.record_count }} 条碳记录 · 报告生成于 {{ report.generated_at?.slice(0, 19) }}</span>
      </div>
    </template>

    <!-- 空状态 -->
    <el-card v-else-if="!loading">
      <el-empty description="请选择企业后生成报告">
        <el-button type="primary" @click="loadCompanies">加载企业列表</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const companies = ref([])
const selectedCompany = ref(null)
const reportType = ref('monthly')
const report = ref(null)

const waterfallChart = ref(null)
const sourcePieChart = ref(null)
const trendChart = ref(null)
const radarChart = ref(null)

const sourceLabelMap = {
  natural_gas: '天然气', coal: '煤炭', electricity: '外购电力',
  gasoline: '汽油', diesel: '柴油', renewable: '可再生能源',
  business_flight_short: '短途航班', business_flight_medium: '中途航班',
  business_flight_long: '长途航班', business_train: '火车', business_car: '公务车',
  waste_landfill: '填埋', waste_incineration: '焚烧', waste_composting: '堆肥',
  purchased_office: '办公用品', purchased_equipment: '设备采购'
}

const reportTypeName = computed(() => {
  return { monthly: '月度', quarterly: '季度', annual: '年度' }[reportType.value] || '月度'
})

const scopePercent = (scope) => {
  if (!report.value || !report.value.summary.total_emission) return 0
  return ((report.value.summary[scope] / report.value.summary.total_emission) * 100).toFixed(1)
}

onMounted(() => { loadCompanies() })

async function loadCompanies() {
  try {
    const res = await fetch('/api/v1/carbon/company/')
    companies.value = await res.json()
    if (companies.value.length > 0 && !selectedCompany.value) {
      selectedCompany.value = companies.value[0].id
      loadReport()
    }
  } catch (e) { companies.value = [] }
}

async function loadReport() {
  if (!selectedCompany.value) { ElMessage.warning('请先选择企业'); return }
  loading.value = true
  try {
    const res = await fetch(`/api/v1/report/report/${selectedCompany.value}/?report_type=${reportType.value}`)
    report.value = await res.json()
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('加载报告失败')
    report.value = null
  }
  loading.value = false
}

async function handleExport(format) {
  if (!selectedCompany.value) return
  if (format === 'pdf') {
    try {
      const res = await fetch(`/api/v1/report/export-pdf/${selectedCompany.value}/?report_type=${reportType.value}`)
      if (!res.ok) throw new Error('PDF生成失败')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `carbon_report_${selectedCompany.value}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('PDF导出成功')
    } catch (e) { ElMessage.error('PDF导出失败: ' + e.message) }
  } else if (format === 'excel') {
    try {
      const res = await fetch(`/api/v1/report/export-excel/${selectedCompany.value}/?report_type=${reportType.value}`)
      if (!res.ok) throw new Error('Excel生成失败')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `carbon_report_${selectedCompany.value}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('Excel导出成功')
    } catch (e) { ElMessage.error('Excel导出失败: ' + e.message) }
  } else if (format === 'csv') {
    try {
      const res = await fetch(`/api/v1/report/export/${selectedCompany.value}/?format=csv`)
      const data = await res.json()
      const blob = new Blob([data.content], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = data.filename || `carbon_report_${selectedCompany.value}.csv`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('CSV导出成功')
    } catch (e) { ElMessage.error('导出失败') }
  } else {
    try {
      const res = await fetch(`/api/v1/report/export/${selectedCompany.value}/?format=json`)
      const data = await res.json()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `carbon_report_${selectedCompany.value}.json`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('JSON导出成功')
    } catch (e) { ElMessage.error('导出失败') }
  }
}

function renderCharts() {
  if (!report.value) return
  const { summary, monthly_data, source_data } = report.value

  // === 瀑布图：排放结构 ===
  if (waterfallChart.value) {
    const chart = echarts.init(waterfallChart.value)
    const s1 = summary.scope1 || 0, s2 = summary.scope2 || 0, s3 = summary.scope3 || 0
    chart.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => {
        const p = params[0]
        if (p.name === '范围1') return `范围1 直接排放: ${s1} kgCO2`
        if (p.name === '范围2') return `范围2 间接排放: ${s2} kgCO2`
        if (p.name === '范围3') return `范围3 其他间接: ${s3} kgCO2`
        return `总排放: ${summary.total_emission} kgCO2`
      }},
      grid: { left: '3%', right: '10%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: ['范围1', '范围2', '范围3', '总排放'] },
      yAxis: { type: 'value', name: 'kgCO2' },
      series: [{
        type: 'bar', stack: 'waterfall',
        label: { show: true, position: 'top', formatter: (p) => {
          if (p.name === '范围1') return s1.toFixed(2)
          if (p.name === '范围2') return s2.toFixed(2)
          if (p.name === '范围3') return s3.toFixed(2)
          return summary.total_emission.toFixed(2)
        }},
        data: [
          { value: s1, itemStyle: { color: '#e74c3c' } },
          { value: s2, itemStyle: { color: '#f39c12' } },
          { value: s3, itemStyle: { color: '#27ae60' } },
          { value: summary.total_emission, itemStyle: { color: '#3498db' } }
        ]
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 饼图：排放源 ===
  if (sourcePieChart.value) {
    const chart = echarts.init(sourcePieChart.value)
    const colors = ['#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#2ecc71', '#34495e', '#16a085']
    const pieData = Object.entries(source_data).map(([k, v], i) => ({
      value: parseFloat(v.toFixed(2)),
      name: sourceLabelMap[k] || k,
      itemStyle: { color: colors[i % colors.length] }
    })).sort((a, b) => b.value - a.value)

    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO2 ({d}%)' },
      legend: { type: 'scroll', bottom: 0, textStyle: { fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['35%', '65%'], center: ['50%', '45%'],
        label: { formatter: '{d}%', fontSize: 11 },
        emphasis: { label: { fontSize: 14, fontWeight: 'bold' } },
        data: pieData
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 折线图：月度趋势 ===
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
    const months = Object.keys(monthly_data).sort()
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: 'kgCO2' },
      series: [{
        type: 'line', smooth: true,
        data: months.map(m => parseFloat(monthly_data[m].toFixed(2))),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.3)' },
            { offset: 1, color: 'rgba(64,158,255,0.05)' }
          ])
        },
        itemStyle: { color: '#409eff' },
        lineStyle: { width: 3 }
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // === 雷达图：行业基准 ===
  if (radarChart.value && summary.total_emission > 0) {
    const chart = echarts.init(radarChart.value)
    const industry = report.value.company?.industry || '制造业'
    // 用当前数据计算强度指标
    const employeeCount = report.value.company?.employee_count || 50
    const intensity = summary.total_emission / employeeCount
    // 行业基准值
    const benchmarkAvg = { '制造业': 0.85, '纺织业': 1.2, '零售业': 0.35, '科技': 0.25 }[industry] || 0.58
    const benchmarkAdv = benchmarkAvg * 0.65

    chart.setOption({
      tooltip: {},
      legend: { data: ['本企业', '行业平均', '先进水平'], bottom: 0 },
      radar: {
        indicator: [
          { name: '排放强度(tCO2/人)', max: Math.max(benchmarkAvg * 2, intensity * 1.5) },
          { name: '范围1占比', max: 100 },
          { name: '范围2占比', max: 100 },
          { name: '范围3占比', max: 100 },
          { name: '减排潜力', max: 100 },
        ],
        shape: 'polygon',
        splitArea: { areaStyle: { color: ['#fff', '#f5f7fa'] } }
      },
      series: [{
        type: 'radar',
        data: [
          {
            value: [intensity, (summary.scope1/summary.total_emission*100), (summary.scope2/summary.total_emission*100), (summary.scope3/summary.total_emission*100), 15],
            name: '本企业', itemStyle: { color: '#409eff' }, areaStyle: { opacity: 0.2 }
          },
          {
            value: [benchmarkAvg, 40, 45, 15, 25],
            name: '行业平均', itemStyle: { color: '#f39c12' }, areaStyle: { opacity: 0.1 }
          },
          {
            value: [benchmarkAdv, 25, 40, 35, 35],
            name: '先进水平', itemStyle: { color: '#67c23a' }, areaStyle: { opacity: 0.1 }
          }
        ]
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }
}
</script>

<style scoped>
.carbon-report { padding: 20px; }
h2 { margin-bottom: 20px; color: #303133; }
.filter-card { margin-bottom: 20px; }
.summary-row { margin: 20px 0; }
.summary-card {
  text-align: center; padding: 24px 16px; border-radius: 12px;
  position: relative; overflow: hidden;
}
.summary-card.total { background: linear-gradient(135deg, #409eff, #337ecc); color: #fff; }
.summary-card.scope1 { background: #fef0f0; }
.summary-card.scope2 { background: #fdf6ec; }
.summary-card.scope3 { background: #f0f9eb; }
.summary-value { font-size: 28px; font-weight: bold; margin-bottom: 4px; }
.summary-card.total .summary-value { font-size: 36px; }
.summary-label { font-size: 13px; opacity: 0.8; margin-bottom: 8px; }
.summary-bar {
  height: 4px; border-radius: 2px; margin-top: 8px;
  background: linear-gradient(90deg, #67c23a, #409eff);
  transition: width 0.8s ease;
}
.suggestion-item {
  padding: 12px; margin-bottom: 10px;
  background: #f0f9eb; border-radius: 8px; border-left: 3px solid #67c23a;
}
.sug-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.sug-title { font-weight: bold; color: #303133; }
.sug-desc { font-size: 13px; color: #606266; padding-left: 24px; }
.report-footer {
  margin-top: 20px; text-align: center; color: #909399; font-size: 13px;
  padding: 16px; border-top: 1px solid #ebeef5;
}
</style>
