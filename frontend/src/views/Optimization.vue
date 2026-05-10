<template>
  <div class="optimization">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="32"><DataAnalysis /></el-icon>
        </div>
        <div>
          <h2>降碳优化</h2>
          <p class="header-desc">智能匹配行业降碳措施，生成最优投资回报方案</p>
        </div>
      </div>
    </div>

    <!-- 参数设置卡片 -->
    <el-card class="param-card" shadow="hover" style="margin-bottom: 24px;">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Setting /></el-icon>
            <span>优化参数设置</span>
          </div>
        </div>
      </template>
      <el-form :inline="true" size="large">
        <el-form-item label="行业类型" class="form-item-icon">
          <el-icon style="margin-right:6px;color:#409eff;"><OfficeBuilding /></el-icon>
          <el-select v-model="selectedIndustry" @change="loadMeasures" style="width: 160px;">
            <el-option label="制造业" value="制造业" />
            <el-option label="纺织业" value="纺织业" />
            <el-option label="零售业" value="零售业" />
            <el-option label="科技" value="科技" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算(万元)" class="form-item-icon">
          <el-icon style="margin-right:6px;color:#67c23a;"><Money /></el-icon>
          <el-input-number v-model="budget" :min="1" :max="500" :step="10" controls-position="right" style="width: 140px;" />
        </el-form-item>
        <el-form-item label="目标减排(%)" class="form-item-icon">
          <el-icon style="margin-right:6px;color:#e6a23c;"><TrendCharts /></el-icon>
          <el-input-number v-model="targetReduction" :min="5" :max="50" :step="5" controls-position="right" style="width: 140px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runOptimization" :loading="optimizing" size="large" round style="min-width: 130px;">
            <el-icon><MagicStick /></el-icon> 智能优化
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 行业基准对比 -->
    <transition name="el-zoom-in-top">
      <el-card v-if="benchmark" class="benchmark-card" shadow="hover" style="margin-bottom: 24px;">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon><DataLine /></el-icon>
              <span>行业基准对比</span>
            </div>
          </div>
        </template>
        <el-row :gutter="24">
          <el-col :span="8" v-for="(item, idx) in benchmarkItems" :key="idx">
            <div class="benchmark-item" :class="'benchmark-' + idx">
              <div class="benchmark-icon" :style="{ background: item.gradient }">
                <el-icon :size="24"><component :is="item.icon" /></el-icon>
              </div>
              <div class="benchmark-info">
                <div class="benchmark-label">{{ item.label }}</div>
                <div class="benchmark-value" :style="{ color: item.color }">{{ item.value }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </transition>

    <!-- 优化结果 -->
    <transition name="el-fade-in-linear">
      <el-card v-if="result" class="result-card" shadow="hover" style="margin-bottom: 24px;">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon><CircleCheckFilled /></el-icon>
              <span>优化方案</span>
            </div>
            <el-tag type="success" size="large" effect="dark" round>
              置信度: {{ (result.confidence * 100).toFixed(0) }}%
            </el-tag>
          </div>
        </template>

        <!-- 结果统计卡片 -->
        <el-row :gutter="20" style="margin-bottom: 24px;">
          <el-col :span="6" v-for="(stat, idx) in resultStats" :key="idx">
            <div class="result-stat-card" :class="'stat-' + idx">
              <div class="stat-header" :style="{ background: stat.gradient }">
                <el-icon :size="24"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-body">
                <div class="stat-value"><span class="counter" :ref="el => setResultCounterRef(el, idx)">0</span><span class="stat-unit">{{ stat.unit }}</span></div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 减排率进度条 -->
        <div style="margin-bottom: 24px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:14px;font-weight:600;color:#303133;">减排率</span>
            <span style="font-size:14px;color:#409eff;font-weight:600;">{{ result.reduction_rate.toFixed(1) }}%</span>
          </div>
          <el-progress :percentage="result.reduction_rate" :stroke-width="18" :format="p => `减排率: ${p.toFixed(1)}%`" :color="result.reduction_rate > 30 ? '#67c23a' : result.reduction_rate > 15 ? '#409eff' : '#e6a23c'" />
          <div style="margin-top:8px;font-size:12px;color:#909399;display:flex;justify-content:space-between;">
            <span>投资回收期: <b>{{ result.payback_period.toFixed(1) }}</b> 年</span>
            <span>综合ROI: <b>{{ result.overall_roi.toFixed(1) }}%</b></span>
          </div>
        </div>

        <!-- 措施列表 -->
        <el-divider content-position="left"><el-icon><List /></el-icon> 推荐措施清单</el-divider>
        <el-table :data="result.selected_measures" stripe size="large" style="width: 100%;" :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: '600' }" row-key="id">
          <el-table-column prop="name" label="措施名称" width="180" />
          <el-table-column prop="category" label="类别" width="110">
            <template #default="{ row }">
              <el-tag :type="getCategoryType(row.category)" effect="dark" size="small" round>
                {{ getCategoryName(row.category) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reduction_potential" label="减排潜力(吨)" width="130" sortable>
            <template #default="{ row }">
              <span style="color: #409eff; font-weight: bold;">{{ row.reduction_potential }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="investment_cost" label="投资(万元)" width="110" sortable />
          <el-table-column prop="annual_saving" label="年节省(万元)" width="130" sortable />
          <el-table-column prop="payback_period" label="回收期(年)" width="110" sortable />
          <el-table-column prop="roi" label="ROI" width="90" sortable>
            <template #default="{ row }">
              <span :style="{ color: row.roi > 20 ? '#67c23a' : row.roi > 10 ? '#e6a23c' : '#f56c6c', fontWeight: 'bold' }">{{ row.roi }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.difficulty === 'easy' ? 'success' : row.difficulty === 'medium' ? 'warning' : 'danger'" size="small" effect="dark" round>
                {{ row.difficulty === 'easy' ? '简单' : row.difficulty === 'medium' ? '中等' : '困难' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" min-width="200" />
        </el-table>

        <!-- 图表可视化 -->
        <el-divider content-position="left"><el-icon><PieChart /></el-icon> 可视化分析</el-divider>
        <el-row :gutter="24" style="margin-top: 16px;">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title"><el-icon><PieChart /></el-icon> 投资分布</div>
              <div ref="investmentChart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title"><el-icon><Histogram /></el-icon> 减排效果</div>
              <div ref="reductionChart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </transition>

    <!-- 可用措施库 -->
    <el-card class="measures-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Files /></el-icon>
            <span>行业降碳措施库</span>
            <el-tag type="info" size="small" effect="plain" round>{{ measures.length }} 条</el-tag>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8" v-for="measure in measures" :key="measure.id" style="margin-bottom: 20px;">
          <el-card shadow="hover" class="measure-card" :class="'measure-' + measure.category">
            <div class="measure-header">
              <div class="measure-name">{{ measure.name }}</div>
              <el-tag :type="getCategoryType(measure.category)" size="small" effect="dark" round>
                {{ getCategoryName(measure.category) }}
              </el-tag>
            </div>
            <div class="measure-stats">
              <div class="stat-item">
                <el-icon><ColdDrink /></el-icon>
                <span>减排: <b>{{ measure.reduction_potential }}</b> 吨</span>
              </div>
              <div class="stat-item">
                <el-icon><Money /></el-icon>
                <span>投资: <b>{{ measure.investment_cost }}</b> 万</span>
              </div>
              <div class="stat-item">
                <el-icon><Wallet /></el-icon>
                <span>年省: <b>{{ measure.annual_saving }}</b> 万</span>
              </div>
              <div class="stat-item">
                <el-icon><TrendCharts /></el-icon>
                <span>ROI: <b :style="{ color: measure.roi > 20 ? '#67c23a' : '#e6a23c' }">{{ measure.roi }}%</b></span>
              </div>
            </div>
            <div class="measure-footer">
              <el-tag :type="measure.difficulty === 'easy' ? 'success' : measure.difficulty === 'medium' ? 'warning' : 'danger'" size="small" effect="plain" round>
                {{ measure.difficulty === 'easy' ? '简单' : measure.difficulty === 'medium' ? '中等' : '困难' }}
              </el-tag>
              <span class="payback">回收期 {{ measure.payback_period }} 年</span>
            </div>
            <div class="measure-desc">{{ measure.description }}</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, onUnmounted, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, Setting, OfficeBuilding, Money, TrendCharts, MagicStick,
  DataLine, CircleCheckFilled, List, PieChart, Histogram, Files,
  ColdDrink, Wallet, InfoFilled
} from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'

const selectedIndustry = ref('制造业')
const budget = ref(50)
const targetReduction = ref(20)
const optimizing = ref(false)

const measures = ref([])
const benchmark = ref(null)
const result = ref(null)

const investmentChart = ref(null)
const reductionChart = ref(null)
let chartInstances = []

const benchmarkItems = computed(() => {
  if (!benchmark.value) return []
  return [
    { label: '行业平均排放强度', value: `${benchmark.value.emission_intensity_avg} 吨CO₂/万元产值`, color: '#f56c6c', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: markRaw(DataLine) },
    { label: '行业先进值', value: `${benchmark.value.emission_intensity_advanced} 吨CO₂/万元产值`, color: '#67c23a', gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: markRaw(CircleCheckFilled) },
    { label: '减排潜力', value: `${(benchmark.value.reduction_potential * 100).toFixed(0)}%`, color: '#409eff', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: markRaw(TrendCharts) }
  ]
})

const resultStats = computed(() => {
  if (!result.value) return []
  return [
    { label: '总投资', value: result.value.total_investment, unit: '万元', icon: markRaw(Money), gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { label: '总减排量', value: result.value.total_reduction, unit: '吨CO₂', icon: markRaw(ColdDrink), gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    { label: '年节省', value: result.value.annual_saving, unit: '万元', icon: markRaw(Wallet), gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    { label: '综合ROI', value: result.value.overall_roi, unit: '%', icon: markRaw(TrendCharts), gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }
  ]
})

const resultCounterRefs = []
function setResultCounterRef(el, idx) { if (el) resultCounterRefs[idx] = el }

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

onMounted(() => {
  loadMeasures()
  loadBenchmark()
})

async function loadMeasures() {
  try {
    const res = await fetch(`${API_BASE}/optimization/measures/${selectedIndustry.value}`)
    measures.value = await res.json()
  } catch (e) {
    console.error('加载措施失败', e)
    // 兜底数据
    measures.value = [
      { id: 1, name: 'LED照明改造', category: 'energy', reduction_potential: 12.5, investment_cost: 8, annual_saving: 2.5, roi: 31.25, payback_period: 3.2, difficulty: 'easy', description: '将传统灯具更换为LED灯具' },
      { id: 2, name: '空压机变频改造', category: 'equipment', reduction_potential: 45.8, investment_cost: 35, annual_saving: 12, roi: 34.3, payback_period: 2.9, difficulty: 'medium', description: '加装变频器实现智能调节' }
    ]
  }
}

async function loadBenchmark() {
  try {
    const res = await fetch(`${API_BASE}/optimization/benchmark/${selectedIndustry.value}`)
    benchmark.value = await res.json()
  } catch (e) {
    console.error('加载基准失败', e)
  }
}

async function runOptimization() {
  optimizing.value = true
  try {
    const res = await fetch(`${API_BASE}/optimization/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_id: 1, current_emission: 1000, target_reduction: targetReduction.value, budget: budget.value, industry: selectedIndustry.value })
    })
    result.value = await res.json()
    ElMessage.success('优化完成')

    await nextTick()
    renderCharts()

    // 启动数字滚动动画
    setTimeout(() => {
      resultCounterRefs.forEach((el, idx) => {
        if (el && resultStats.value[idx]) animateCounter(el, resultStats.value[idx].value)
      })
    }, 300)
  } catch (e) {
    ElMessage.error('优化失败')
  }
  optimizing.value = false
}

function renderCharts() {
  if (!result.value || result.value.selected_measures.length === 0) return

  chartInstances.forEach(c => c.dispose?.())
  chartInstances = []

  // 投资分布饼图
  if (investmentChart.value) {
    const categoryData = {}
    result.value.selected_measures.forEach(m => {
      const catName = getCategoryName(m.category)
      categoryData[catName] = (categoryData[catName] || 0) + m.investment_cost
    })

    const pie = markRaw(echarts.init(investmentChart.value))
    chartInstances.push(pie)
    pie.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}万 ({d}%)', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      legend: { bottom: 0, textStyle: { fontSize: 12, color: '#606266' }, icon: 'circle', itemWidth: 10, itemHeight: 10 },
      series: [{
        type: 'pie', radius: ['35%', '68%'], center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { formatter: '{b}\n{d}%', fontSize: 12, lineHeight: 20 },
        emphasis: { label: { fontSize: 16, fontWeight: 'bold' }, itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
        data: Object.entries(categoryData).map(([name, value], idx) => ({
          name, value,
          itemStyle: { color: ['#409eff', '#67c23a', '#e6a23c', '#909399'][idx % 4] }
        })),
        animationType: 'scale', animationEasing: 'elasticOut', animationDelay: (idx) => idx * 200
      }]
    })
    window.addEventListener('resize', () => pie.resize())
  }

  // 减排效果柱状图
  if (reductionChart.value) {
    const measures_data = result.value.selected_measures.slice(0, 8)
    const bar = markRaw(echarts.init(reductionChart.value))
    chartInstances.push(bar)
    bar.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} 吨CO₂', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'transparent', textStyle: { color: '#fff' } },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: measures_data.map(m => m.name.length > 6 ? m.name.slice(0, 6) + '...' : m.name), axisLabel: { interval: 0, rotate: 30, fontSize: 11, color: '#909399' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
      yAxis: { type: 'value', name: '吨CO₂', nameTextStyle: { fontSize: 11, color: '#909399' }, axisLabel: { fontSize: 11, color: '#909399' }, splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } } },
      series: [{
        type: 'bar',
        data: measures_data.map(m => ({
          value: m.reduction_potential,
          itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }]) }
        })),
        itemStyle: { borderRadius: [8, 8, 0, 0] },
        barWidth: '55%',
        label: { show: true, position: 'top', fontSize: 11, color: '#606266', fontWeight: 500 },
        animationDuration: 1500, animationEasing: 'elasticOut', animationDelay: (idx) => idx * 150
      }]
    })
    window.addEventListener('resize', () => bar.resize())
  }
}

function getCategoryColor(category) {
  const colors = { energy: '#409EFF', process: '#67C23A', equipment: '#E6A23C', renewable: '#909399' }
  return colors[category] || '#409EFF'
}

function getCategoryType(category) {
  const types = { energy: 'primary', process: 'success', equipment: 'warning', renewable: 'info' }
  return types[category] || 'info'
}

function getCategoryName(category) {
  const names = { energy: '能源优化', process: '工艺改进', equipment: '设备升级', renewable: '清洁能源' }
  return names[category] || category
}

onUnmounted(() => { chartInstances.forEach(c => c.dispose?.()) })
</script>

<style scoped>
.optimization { padding: 24px; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }

/* 页面标题区 */
.page-header { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(67,233,123,0.25); animation: fadeInUp 0.6s ease both; }
.header-content { display: flex; align-items: center; gap: 20px; color: #fff; }
.header-icon { width: 64px; height: 64px; border-radius: 16px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
h2 { font-size: 26px; font-weight: 700; margin: 0; color: #fff; }
.header-desc { font-size: 14px; color: rgba(255,255,255,0.85); margin-top: 6px; }

/* 参数卡片 */
.param-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.1s ease both; }
.param-card :deep(.el-card__header) { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); font-size: 16px; font-weight: 600; color: #303133; padding: 16px 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: #303133; }
.form-item-icon { display: flex; align-items: center; }

/* 基准对比卡片 */
.benchmark-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.15s ease both; }
.benchmark-item { display: flex; align-items: center; gap: 16px; padding: 20px; border-radius: 12px; background: #f5f7fa; transition: all 0.3s; }
.benchmark-item:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.benchmark-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
.benchmark-info { flex: 1; }
.benchmark-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.benchmark-value { font-size: 16px; font-weight: 700; }

/* 结果卡片 */
.result-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.2s ease both; }

/* 结果统计卡片 */
.result-stat-card { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: all 0.3s; }
.result-stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.stat-header { width: 100%; height: 6px; }
.stat-body { padding: 16px; }
.stat-value { font-size: 26px; font-weight: 800; color: #303133; display: flex; align-items: baseline; gap: 4px; }
.stat-unit { font-size: 12px; color: #909399; font-weight: 400; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }

/* 图表容器 */
.chart-container { background: #f5f7fa; border-radius: 12px; padding: 16px; height: 100%; }
.chart-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }

/* 措施卡片 */
.measures-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.25s ease both; }
.measure-card { border-radius: 12px; border: none; transition: all 0.35s; cursor: pointer; }
.measure-card:hover { transform: translateY(-6px) scale(1.01); box-shadow: 0 12px 36px rgba(0,0,0,0.1); }
.measure-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.measure-name { font-size: 15px; font-weight: 700; color: #303133; flex: 1; }
.measure-stats { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.stat-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #606266; }
.stat-item .el-icon { font-size: 14px; color: #909399; }
.stat-item b { color: #303133; }
.measure-footer { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.payback { font-size: 12px; color: #909399; }
.measure-desc { font-size: 12px; color: #909399; line-height: 1.6; padding-top: 8px; border-top: 1px solid #f0f0f0; }

/* 表格 */
:deep(.el-table) { border-radius: 12px; overflow: hidden; }
:deep(.el-table__row) { transition: all 0.3s ease; }
:deep(.el-table__row:hover) { background: #ecf5ff !important; }

/* 进度条 */
:deep(.el-progress-bar__inner) { transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1); }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .optimization { padding: 12px; }
  .page-header { padding: 20px; }
  h2 { font-size: 22px; }
  .header-content { flex-direction: column; text-align: center; }
}
</style>
