<template>
  <div class="company-compare">
    <h2>多企业碳排放对比</h2>

    <!-- 企业选择 -->
    <el-card class="select-card">
      <el-form :inline="true">
        <el-form-item label="选择企业">
          <el-select v-model="selectedIds" multiple collapse-tags collapse-tags-tooltip
            placeholder="请选择要对比的企业" filterable style="width: 400px;" @change="loadCompare">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id">
              <span>{{ c.name }}</span>
              <span style="color: #999; margin-left: 8px; font-size: 12px;">{{ c.industry }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadCompare" :loading="loading" :disabled="selectedIds.length < 2">
            对比分析
          </el-button>
          <el-button @click="selectAll">全选</el-button>
          <el-button @click="clearAll">清空</el-button>
        </el-form-item>
      </el-form>
      <div v-if="selectedIds.length > 0" class="selected-info">
        已选择 <strong>{{ selectedIds.length }}</strong> 家企业
      </div>
    </el-card>

    <!-- 对比结果 -->
    <template v-if="compareData">
      <!-- 排名卡片 -->
      <el-row :gutter="16" class="rank-row">
        <el-col :span="6" v-for="(c, i) in topCompanies" :key="c.company_id">
          <div class="rank-card" :class="'rank-' + (i + 1)">
            <div class="rank-badge">{{ i + 1 }}</div>
            <div class="rank-name">{{ c.name }}</div>
            <div class="rank-value">{{ c.total_emission.toLocaleString() }}</div>
            <div class="rank-unit">kgCO₂</div>
            <div class="rank-industry">{{ c.industry }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 总排放对比柱状图 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>总排放量对比</span></template>
            <div ref="barChart" style="height: 350px;"></div>
          </el-card>
        </el-col>
        <!-- 范围堆叠柱状图 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>排放范围分布</span></template>
            <div ref="stackChart" style="height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 碳排放强度散点图 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>碳排放强度 (kgCO₂/人)</span></template>
            <div ref="scatterChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
        <!-- 月度趋势对比 -->
        <el-col :span="12">
          <el-card>
            <template #header><span>月度排放趋势</span></template>
            <div ref="trendChart" style="height: 320px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细数据表格 -->
      <el-card style="margin-top: 20px;">
        <template #header><span>详细对比数据</span></template>
        <el-table :data="compareData.companies" border stripe>
          <el-table-column prop="rank" label="排名" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.rank <= 3 ? 'danger' : 'info'" size="small">{{ row.rank }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="企业名称" min-width="150" />
          <el-table-column prop="industry" label="行业" width="100" />
          <el-table-column prop="employee_count" label="员工数" width="80" align="right" />
          <el-table-column prop="total_emission" label="总排放(kgCO₂)" width="130" align="right" sortable>
            <template #default="{ row }">{{ row.total_emission.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="scope1" label="范围1" width="100" align="right">
            <template #default="{ row }">{{ row.scope1.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="scope2" label="范围2" width="100" align="right">
            <template #default="{ row }">{{ row.scope2.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="scope3" label="范围3" width="100" align="right">
            <template #default="{ row }">{{ row.scope3.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="intensity" label="人均排放" width="100" align="right" sortable>
            <template #default="{ row }">{{ row.intensity.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="record_count" label="记录数" width="80" align="right" />
        </el-table>
      </el-card>
    </template>

    <!-- 空状态 -->
    <el-card v-else-if="!loading" style="margin-top: 20px;">
      <el-empty description="请选择至少2家企业进行对比">
        <el-button type="primary" @click="loadCompanies">加载企业列表</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { API_BASE } from '../utils/auth'

const loading = ref(false)
const companies = ref([])
const selectedIds = ref([])
const compareData = ref(null)

const barChart = ref(null)
const stackChart = ref(null)
const scatterChart = ref(null)
const trendChart = ref(null)

const topCompanies = computed(() => {
  if (!compareData.value) return []
  return compareData.value.companies.slice(0, 4)
})

onMounted(() => { loadCompanies() })

async function loadCompanies() {
  try {
    const res = await fetch(`${API_BASE}/carbon/company/`)
    companies.value = await res.json()
    if (companies.value.length >= 2) {
      selectedIds.value = companies.value.slice(0, 3).map(c => c.id)
    }
  } catch (e) {
    ElMessage.error('加载企业列表失败')
    companies.value = []
  }
}

function selectAll() {
  selectedIds.value = companies.value.map(c => c.id)
}

function clearAll() {
  selectedIds.value = []
  compareData.value = null
}

async function loadCompare() {
  if (selectedIds.value.length < 2) {
    ElMessage.warning('请选择至少2家企业')
    return
  }
  loading.value = true
  try {
    const ids = selectedIds.value.join(',')
    const res = await fetch(`/api/v1/report/compare/?company_ids=${ids}`)
    if (!res.ok) throw new Error('对比失败')
    compareData.value = await res.json()
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('加载对比数据失败: ' + e.message)
    compareData.value = null
  }
  loading.value = false
}

function renderCharts() {
  if (!compareData.value) return
  const data = compareData.value.companies

  // 柱状图：总排放对比
  if (barChart.value) {
    const chart = echarts.init(barChart.value)
    const sorted = [...data].sort((a, b) => b.total_emission - a.total_emission)
    chart.setOption({
      tooltip: { trigger: 'axis', formatter: p => `${p[0].name}<br/>总排放: ${p[0].value.toLocaleString()} kgCO₂` },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: sorted.map(c => c.name), axisLabel: { rotate: 30, fontSize: 11 } },
      yAxis: { type: 'value', name: 'kgCO₂' },
      series: [{
        type: 'bar',
        data: sorted.map(c => ({
          value: c.total_emission,
          itemStyle: { color: c.rank === 1 ? '#e74c3c' : c.rank === 2 ? '#f39c12' : '#409eff' }
        })),
        label: { show: true, position: 'top', formatter: p => p.value > 0 ? p.value.toLocaleString() : '', fontSize: 10 }
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 堆叠柱状图：范围分布
  if (stackChart.value) {
    const chart = echarts.init(stackChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['范围1', '范围2', '范围3'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: data.map(c => c.name), axisLabel: { rotate: 30, fontSize: 11 } },
      yAxis: { type: 'value', name: 'kgCO₂' },
      series: [
        { name: '范围1', type: 'bar', stack: 'total', data: data.map(c => c.scope1), itemStyle: { color: '#e74c3c' } },
        { name: '范围2', type: 'bar', stack: 'total', data: data.map(c => c.scope2), itemStyle: { color: '#f39c12' } },
        { name: '范围3', type: 'bar', stack: 'total', data: data.map(c => c.scope3), itemStyle: { color: '#27ae60' } }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 散点图：碳排放强度
  if (scatterChart.value) {
    const chart = echarts.init(scatterChart.value)
    const sorted = [...data].sort((a, b) => b.intensity - a.intensity)
    chart.setOption({
      tooltip: { formatter: p => `${p.data.name}<br/>人均排放: ${p.data.value.toFixed(2)} kgCO₂/人<br/>员工数: ${p.data.emp}` },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: sorted.map(c => c.name), axisLabel: { rotate: 30, fontSize: 11 } },
      yAxis: { type: 'value', name: 'kgCO₂/人' },
      series: [{
        type: 'scatter',
        symbolSize: p => Math.max(15, Math.min(50, p.emp / 5)),
        data: sorted.map(c => ({ value: c.intensity, name: c.name, emp: c.employee_count })),
        itemStyle: { color: '#409eff', opacity: 0.7 }
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 折线图：月度趋势
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
    const allMonths = new Set()
    data.forEach(c => Object.keys(c.monthly).forEach(m => allMonths.add(m)))
    const months = Array.from(allMonths).sort()
    const colors = ['#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6', '#1abc9c']
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: data.map(c => c.name), bottom: 0, type: 'scroll' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: 'kgCO₂' },
      series: data.map((c, i) => ({
        name: c.name,
        type: 'line',
        data: months.map(m => c.monthly[m]?.total || 0),
        itemStyle: { color: colors[i % colors.length] },
        smooth: true
      }))
    })
    window.addEventListener('resize', () => chart.resize())
  }
}
</script>

<style scoped>
.company-compare { padding: 20px; }
h2 { margin-bottom: 20px; color: #303133; }
.select-card { margin-bottom: 20px; }
.selected-info { margin-top: 10px; color: #909399; font-size: 13px; }
.rank-row { margin: 20px 0; }
.rank-card {
  text-align: center; padding: 20px; border-radius: 12px;
  background: #f5f7fa; position: relative;
}
.rank-card.rank-1 { background: linear-gradient(135deg, #ffebee, #fff); border: 2px solid #e74c3c; }
.rank-card.rank-2 { background: linear-gradient(135deg, #fff8e1, #fff); border: 2px solid #f39c12; }
.rank-card.rank-3 { background: linear-gradient(135deg, #e8f5e9, #fff); border: 2px solid #27ae60; }
.rank-badge {
  position: absolute; top: -10px; left: -10px;
  width: 32px; height: 32px; border-radius: 50%;
  background: #409eff; color: #fff; font-weight: bold;
  display: flex; align-items: center; justify-content: center;
}
.rank-1 .rank-badge { background: #e74c3c; }
.rank-2 .rank-badge { background: #f39c12; }
.rank-3 .rank-badge { background: #27ae60; }
.rank-name { font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #303133; }
.rank-value { font-size: 28px; font-weight: bold; color: #409eff; }
.rank-1 .rank-value { color: #e74c3c; }
.rank-2 .rank-value { color: #f39c12; }
.rank-3 .rank-value { color: #27ae60; }
.rank-unit { font-size: 12px; color: #909399; margin-bottom: 4px; }
.rank-industry { font-size: 12px; color: #606266; }
</style>
