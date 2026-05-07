<template>
  <div class="optimization">
    <h2>降碳优化</h2>
    
    <!-- 行业选择 -->
    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true">
        <el-form-item label="行业类型">
          <el-select v-model="selectedIndustry" @change="loadMeasures" style="width: 150px;">
            <el-option label="制造业" value="制造业" />
            <el-option label="纺织业" value="纺织业" />
            <el-option label="零售业" value="零售业" />
            <el-option label="科技" value="科技" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算(万元)">
          <el-input-number v-model="budget" :min="1" :max="500" />
        </el-form-item>
        <el-form-item label="目标减排(%)">
          <el-input-number v-model="targetReduction" :min="5" :max="50" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runOptimization" :loading="optimizing">
            智能优化
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 行业基准对比 -->
    <el-card style="margin-bottom: 20px;" v-if="benchmark">
      <template #header>
        <span>行业基准对比</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="benchmark-item">
            <div class="benchmark-label">行业平均排放强度</div>
            <div class="benchmark-value">{{ benchmark.emission_intensity_avg }} 吨CO2/万元产值</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="benchmark-item">
            <div class="benchmark-label">行业先进值</div>
            <div class="benchmark-value" style="color: #67c23a;">{{ benchmark.emission_intensity_advanced }} 吨CO2/万元产值</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="benchmark-item">
            <div class="benchmark-label">减排潜力</div>
            <div class="benchmark-value" style="color: #409eff;">{{ (benchmark.reduction_potential * 100).toFixed(0) }}%</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 优化结果 -->
    <el-card style="margin-bottom: 20px;" v-if="result">
      <template #header>
        <div class="card-header">
          <span>优化方案</span>
          <el-tag type="success">置信度: {{ (result.confidence * 100).toFixed(0) }}%</el-tag>
        </div>
      </template>
      
      <!-- 结果汇总 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic title="总投资" :value="result.total_investment" suffix="万元" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="总减排量" :value="result.total_reduction" suffix="吨CO2" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="年节省" :value="result.annual_saving" suffix="万元" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="综合ROI" :value="result.overall_roi" suffix="%" />
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="12">
          <el-progress :percentage="result.reduction_rate" :format="p => `减排率: ${p.toFixed(1)}%`" />
        </el-col>
        <el-col :span="12">
          <span>回收期: {{ result.payback_period.toFixed(1) }} 年</span>
        </el-col>
      </el-row>
      
      <!-- 措施列表 -->
      <el-table :data="result.selected_measures" stripe>
        <el-table-column prop="name" label="措施名称" width="180" />
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reduction_potential" label="减排潜力(吨)" width="120" />
        <el-table-column prop="investment_cost" label="投资(万元)" width="100" />
        <el-table-column prop="annual_saving" label="年节省(万元)" width="100" />
        <el-table-column prop="payback_period" label="回收期(年)" width="100" />
        <el-table-column prop="roi" label="ROI" width="80">
          <template #default="{ row }">
            <span :style="{color: row.roi > 20 ? '#67c23a' : '#e6a23c'}">{{ row.roi }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="row.difficulty === 'easy' ? 'success' : row.difficulty === 'medium' ? 'warning' : 'danger'" size="small">
              {{ row.difficulty === 'easy' ? '简单' : row.difficulty === 'medium' ? '中等' : '困难' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" />
      </el-table>
      
      <!-- 图表可视化 -->
      <div style="margin-top: 30px;">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>投资分布</h4>
              <div ref="investmentChart" style="height: 280px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>减排效果</h4>
              <div ref="reductionChart" style="height: 280px;"></div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 可用措施库 -->
    <el-card>
      <template #header>
        <span>行业降碳措施库</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6" v-for="measure in measures" :key="measure.id">
          <el-card shadow="hover" style="margin-bottom: 15px;">
            <div class="measure-card">
              <div class="measure-name">{{ measure.name }}</div>
              <el-tag :type="getCategoryType(measure.category)" size="small">
                {{ getCategoryName(measure.category) }}
              </el-tag>
              <div class="measure-stats">
                <div>减排: {{ measure.reduction_potential }} 吨</div>
                <div>投资: {{ measure.investment_cost }} 万</div>
                <div>年省: {{ measure.annual_saving }} 万</div>
              </div>
              <div class="measure-desc">{{ measure.description }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { API_BASE } from '../utils/auth'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const selectedIndustry = ref('制造业')
const budget = ref(50)
const targetReduction = ref(20)
const optimizing = ref(false)

const measures = ref([])
const benchmark = ref(null)
const result = ref(null)

// 图表引用
const investmentChart = ref(null)
const reductionChart = ref(null)
let investmentChartInstance = null
let reductionChartInstance = null

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
      body: JSON.stringify({
        company_id: 1,
        current_emission: 1000,
        target_reduction: targetReduction.value,
        budget: budget.value,
        industry: selectedIndustry.value
      })
    })
    result.value = await res.json()
    ElMessage.success('优化完成')
    
    // 渲染图表
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('优化失败')
  }
  optimizing.value = false
}

function renderCharts() {
  if (!result.value || result.value.selected_measures.length === 0) return
  
  // 投资分布饼图
  if (investmentChart.value) {
    if (investmentChartInstance) {
      investmentChartInstance.dispose()
    }
    investmentChartInstance = echarts.init(investmentChart.value)
    
    const categoryData = {}
    result.value.selected_measures.forEach(m => {
      const catName = getCategoryName(m.category)
      categoryData[catName] = (categoryData[catName] || 0) + m.investment_cost
    })
    
    investmentChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}万 ({d}%)' },
      legend: { bottom: 0, left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: Object.entries(categoryData).map(([name, value]) => ({ name, value }))
      }],
      color: ['#409EFF', '#67C23A', '#E6A23C', '#909399']
    })
  }
  
  // 减排效果柱状图
  if (reductionChart.value) {
    if (reductionChartInstance) {
      reductionChartInstance.dispose()
    }
    reductionChartInstance = echarts.init(reductionChart.value)
    
    const measures_data = result.value.selected_measures.slice(0, 8)
    
    reductionChartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: measures_data.map(m => m.name.length > 6 ? m.name.slice(0, 6) + '...' : m.name),
        axisLabel: { interval: 0, rotate: 30, fontSize: 11 }
      },
      yAxis: { type: 'value', name: '吨CO2' },
      series: [{
        type: 'bar',
        data: measures_data.map(m => ({
          value: m.reduction_potential,
          itemStyle: { color: getCategoryColor(m.category) }
        })),
        barWidth: '60%',
        label: { show: true, position: 'top', fontSize: 10 }
      }]
    })
  }
}

function getCategoryColor(category) {
  const colors = {
    energy: '#409EFF',
    process: '#67C23A',
    equipment: '#E6A23C',
    renewable: '#909399'
  }
  return colors[category] || '#409EFF'
}

function getCategoryType(category) {
  const types = {
    energy: 'primary',
    process: 'success',
    equipment: 'warning',
    renewable: 'info'
  }
  return types[category] || 'info'
}

function getCategoryName(category) {
  const names = {
    energy: '能源优化',
    process: '工艺改进',
    equipment: '设备升级',
    renewable: '清洁能源'
  }
  return names[category] || category
}
</script>

<style scoped>
.optimization {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.benchmark-item {
  text-align: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.benchmark-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.benchmark-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.measure-card {
  padding: 10px;
}

.measure-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.measure-stats {
  margin: 10px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.measure-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.chart-container {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
}

.chart-container h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}
</style>
