<template>
  <div class="wizard-container">
    <!-- 顶部统计 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ industries.length }}</div>
          <div class="stat-label">行业模板</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ allSources.length }}</div>
          <div class="stat-label">排放源类型</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ selectedIndustry ? profileSources.length : '-' }}</div>
          <div class="stat-label">推荐填报项</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ estimatedTotal > 0 ? formatNumber(estimatedTotal) + ' kg' : '-' }}</div>
          <div class="stat-label">预估月排放量</div>
        </div>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- Tab 1: 行业选择 + 模板填报 -->
      <el-tab-pane label="行业模板" name="template">
        <el-row :gutter="20">
          <!-- 左侧：行业选择 -->
          <el-col :span="8">
            <div class="industry-list">
              <div class="section-title">选择行业</div>
              <div
                v-for="ind in industries"
                :key="ind.industry"
                :class="['industry-card', { active: selectedIndustry === ind.industry }]"
                @click="selectIndustry(ind.industry)"
              >
                <span class="industry-icon">{{ ind.icon }}</span>
                <div class="industry-info">
                  <div class="industry-name">{{ ind.name }}</div>
                  <div class="industry-desc">{{ ind.description }}</div>
                </div>
                <el-tag size="small" type="info">{{ ind.source_count }}项</el-tag>
              </div>
            </div>
          </el-col>

          <!-- 右侧：填报模板 -->
          <el-col :span="16">
            <div v-if="!selectedIndustry" class="empty-hint">
              <el-icon :size="48"><Guide /></el-icon>
              <p>请先选择行业，系统将自动推荐该行业的典型排放源</p>
            </div>

            <div v-else class="template-panel">
              <div class="template-header">
                <h3>{{ currentProfile.icon }} {{ currentProfile.name }} - 填报模板</h3>
                <div class="template-actions">
                  <el-select v-model="selectedRegion" placeholder="选择地区" size="small" style="width:200px">
                    <el-option v-for="reg in regions" :key="reg.value" :label="reg.label" :value="reg.value" />
                  </el-select>
                  <el-button type="primary" size="small" @click="generateTemplate" :loading="generating">
                    生成模板
                  </el-button>
                  <el-button type="success" size="small" @click="batchSubmit" :loading="submitting"
                    :disabled="templateRecords.length === 0">
                    批量提交
                  </el-button>
                </div>
              </div>

              <el-alert v-if="templateRecords.length > 0"
                title="以下为行业典型值，请根据实际情况修改消耗量后提交"
                type="info" :closable="false" show-icon style="margin-bottom:16px" />

              <!-- 模板记录表格 -->
              <el-table :data="templateRecords" border stripe style="width:100%"
                :row-class-name="tableRowClass">
                <el-table-column label="范围" width="120">
                  <template #default="{ row }">
                    <el-tag :type="scopeTagType(row.scope)" size="small">{{ scopeLabel(row.scope) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="排放源" prop="label" min-width="180" />
                <el-table-column label="消耗量" width="200">
                  <template #default="{ row }">
                    <el-input-number v-model="row.quantity" :min="0" :step="getStep(row.emission_source)"
                      size="small" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="单位" width="100">
                  <template #default="{ row }">
                    <el-select v-model="row.unit" size="small" style="width:80px">
                      <el-option v-for="u in getSourceUnits(row.emission_source)" :key="u" :label="u" :value="u" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="预估CO2(kg)" width="120">
                  <template #default="{ row }">
                    <span class="co2-value">{{ formatNumber(row.estimated_co2) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="提示" min-width="160">
                  <template #default="{ row }">
                    <span class="tip-text">{{ row.tip }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="70" fixed="right">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" link @click="templateRecords.splice($index, 1)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 合计 -->
              <div v-if="templateRecords.length > 0" class="total-bar">
                <span>预估月排放总量: <strong>{{ formatNumber(estimatedTotal) }} kgCO2</strong></span>
                <span style="margin-left:24px">
                  范围1: {{ formatNumber(scopeTotal('scope1')) }} |
                  范围2: {{ formatNumber(scopeTotal('scope2')) }} |
                  范围3: {{ formatNumber(scopeTotal('scope3')) }}
                </span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Tab 2: 快速估算 -->
      <el-tab-pane label="快速估算" name="estimate">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="section-title">选择行业估算</div>
            <div class="estimate-cards">
              <div v-for="ind in industries" :key="ind.industry"
                :class="['estimate-card', { active: estimateIndustry === ind.industry }]"
                @click="doEstimate(ind.industry)">
                <span class="industry-icon">{{ ind.icon }}</span>
                <span>{{ ind.name }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="16">
            <div v-if="!estimateResult" class="empty-hint">
              <el-icon :size="48"><DataAnalysis /></el-icon>
              <p>选择行业查看碳排放量级估算</p>
            </div>
            <div v-else class="estimate-result">
              <h3>{{ estimateResult.industry }} - 典型企业月排放估算</h3>
              <el-row :gutter="16" style="margin-top:16px">
                <el-col :span="8">
                  <div class="stat-card highlight">
                    <div class="stat-value">{{ formatNumber(estimateResult.total_estimated) }}</div>
                    <div class="stat-label">kgCO2/月</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="stat-card">
                    <div class="stat-value">{{ formatNumber(estimateResult.scope_breakdown.scope1) }}</div>
                    <div class="stat-label">范围1</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="stat-card">
                    <div class="stat-value">{{ formatNumber(estimateResult.scope_breakdown.scope2) }}</div>
                    <div class="stat-label">范围2</div>
                  </div>
                </el-col>
              </el-row>

              <!-- 排放构成饼图 -->
              <div ref="estimateChartRef" style="height:300px;margin-top:16px"></div>

              <el-table :data="estimateResult.details" border stripe style="margin-top:16px">
                <el-table-column label="排放源" prop="source" />
                <el-table-column label="范围">
                  <template #default="{ row }">
                    <el-tag :type="scopeTagType(row.scope)" size="small">{{ scopeLabel(row.scope) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="预估CO2(kg)">
                  <template #default="{ row }">{{ formatNumber(row.estimated_co2) }}</template>
                </el-table-column>
                <el-table-column label="占比">
                  <template #default="{ row }">
                    <el-progress :percentage="row.percentage" :stroke-width="8" style="width:120px" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Tab 3: 企业填报推荐 -->
      <el-tab-pane label="填报推荐" name="recommend">
        <div class="recommend-header">
          <span class="section-title">企业填报状态分析</span>
          <el-select v-model="selectedCompany" placeholder="选择企业" size="small" style="width:250px"
            @change="loadRecommendation">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>

        <div v-if="!recommendData" class="empty-hint">
          <el-icon :size="48"><Warning /></el-icon>
          <p>选择企业查看填报推荐</p>
        </div>

        <div v-else class="recommend-panel">
          <el-alert
            :title="recommendData.suggestion"
            :type="recommendData.missing_sources > 0 ? 'warning' : 'success'"
            :closable="false" show-icon style="margin-bottom:16px" />

          <el-table :data="recommendData.recommendations" border stripe>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'filled' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'filled' ? '已填' : '未填' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="范围" width="120">
              <template #default="{ row }">
                <el-tag :type="scopeTagType(row.scope)" size="small">{{ scopeLabel(row.scope) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="排放源" prop="label" />
            <el-table-column label="典型值" width="160">
              <template #default="{ row }">
                {{ row.typical_quantity }} {{ row.unit }}
              </template>
            </el-table-column>
            <el-table-column label="说明" prop="reason" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'missing'" type="primary" size="small"
                  @click="quickFill(row)">快速填报</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 快速填报对话框 -->
    <el-dialog v-model="quickFillVisible" title="快速填报" width="500px">
      <el-form :model="quickFillForm" label-width="100px">
        <el-form-item label="企业">
          <el-input :value="selectedCompanyName" disabled />
        </el-form-item>
        <el-form-item label="范围">
          <el-tag>{{ scopeLabel(quickFillForm.scope) }}</el-tag>
        </el-form-item>
        <el-form-item label="排放源">
          {{ quickFillForm.label }}
        </el-form-item>
        <el-form-item label="消耗量">
          <el-input-number v-model="quickFillForm.quantity" :min="0" :step="getStep(quickFillForm.emission_source)"
            style="width:100%" />
        </el-form-item>
        <el-form-item label="单位">
          {{ quickFillForm.unit }}
        </el-form-item>
        <el-form-item label="填报月份">
          <el-input v-model="quickFillForm.record_date" placeholder="YYYY-MM" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickFillVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuickFill" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Guide, DataAnalysis, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

const API = 'https://ai-carbon-system.onrender.com/api/v1'

// State
const activeTab = ref('template')
const industries = ref([])
const allSources = ref([])
const regions = ref([])
const selectedIndustry = ref('')
const selectedRegion = ref('华东')
const currentProfile = ref({})
const profileSources = ref([])
const templateRecords = ref([])
const generating = ref(false)
const submitting = ref(false)
const estimateIndustry = ref('')
const estimateResult = ref(null)
const estimateChartRef = ref(null)
const companies = ref([])
const selectedCompany = ref(null)
const recommendData = ref(null)
const quickFillVisible = ref(false)
const quickFillForm = ref({})
let estimateChart = null

// Computed
const estimatedTotal = computed(() => {
  return templateRecords.value.reduce((sum, r) => sum + (r.estimated_co2 || 0), 0)
})

const selectedCompanyName = computed(() => {
  const c = companies.value.find(c => c.id === selectedCompany.value)
  return c ? c.name : ''
})

// Methods
function formatNumber(n) {
  if (!n && n !== 0) return '-'
  return n.toLocaleString('zh-CN', { maximumFractionDigits: 1 })
}

function scopeLabel(scope) {
  const map = { scope1: '范围1', scope2: '范围2', scope3: '范围3' }
  return map[scope] || scope
}

function scopeTagType(scope) {
  const map = { scope1: 'danger', scope2: 'warning', scope3: 'info' }
  return map[scope] || ''
}

function scopeTotal(scope) {
  return templateRecords.value
    .filter(r => r.scope === scope)
    .reduce((sum, r) => sum + (r.estimated_co2 || 0), 0)
}

function getSourceUnits(source) {
  const s = allSources.value.find(s => s.emission_source === source)
  return s ? s.units : []
}

function getStep(source) {
  const ranges = {
    natural_gas: 1000, coal: 100, gasoline: 100, diesel: 100,
    electricity: 10000, renewable: 1000,
    business_flight_short: 1000, business_flight_medium: 1000, business_flight_long: 1000,
    business_train: 1000, business_car: 500,
    waste_landfill: 100, waste_incineration: 100, waste_composting: 100,
    purchased_office: 10000, purchased_equipment: 100000,
  }
  return ranges[source] || 100
}

function tableRowClass({ row }) {
  const range = row.quantity_range
  if (range && (row.quantity < range[0] || row.quantity > range[1])) return 'warning-row'
  return ''
}

async function authFetch(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('认证过期')
  }
  return res.json()
}

// Load data
async function loadIndustries() {
  const d = await authFetch(`${API}/wizard/industries`)
  industries.value = d.data || []
}

async function loadSources() {
  const d = await authFetch(`${API}/wizard/sources`)
  allSources.value = d.data || []
}

async function loadRegions() {
  const d = await authFetch(`${API}/wizard/regions`)
  regions.value = d.data || []
}

async function loadCompanies() {
  const d = await authFetch(`${API}/carbon/companies/`)
  companies.value = d.data || d.companies || []
}

// Industry selection
async function selectIndustry(industry) {
  selectedIndustry.value = industry
  const d = await authFetch(`${API}/wizard/industries/${encodeURIComponent(industry)}`)
  currentProfile.value = d.data || {}
  profileSources.value = d.data?.recommended_sources || []
  templateRecords.value = []
}

// Generate template
async function generateTemplate() {
  if (!selectedIndustry.value) return
  generating.value = true
  try {
    const now = new Date()
    const recordDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    const companyId = selectedCompany.value || (companies.value[0]?.id)
    if (!companyId) {
      ElMessage.warning('请先选择企业')
      generating.value = false
      return
    }
    const d = await authFetch(
      `${API}/wizard/template?industry=${encodeURIComponent(selectedIndustry.value)}&company_id=${companyId}&record_date=${recordDate}&region=${encodeURIComponent(selectedRegion.value)}`,
      { method: 'POST' }
    )
    templateRecords.value = d.data?.records || []
    ElMessage.success('模板已生成，请修改消耗量后批量提交')
  } catch (e) {
    ElMessage.error('生成模板失败: ' + e.message)
  }
  generating.value = false
}

// Batch submit
async function batchSubmit() {
  if (templateRecords.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确认提交 ${templateRecords.value.length} 条碳数据记录？`,
      '批量提交确认',
      { type: 'warning' }
    )
  } catch { return }

  submitting.value = true
  let successCount = 0
  let errorCount = 0
  const errors = []

  for (const record of templateRecords.value) {
    try {
      const d = await authFetch(`${API}/carbon/records/`, {
        method: 'POST',
        body: JSON.stringify({
          company_id: record.company_id,
          scope: record.scope,
          emission_source: record.emission_source,
          quantity: record.quantity,
          unit: record.unit,
          record_date: templateRecords.value[0]?.record_date || new Date().toISOString().slice(0, 7),
        }),
      })
      if (d.success || d.id) {
        successCount++
      } else {
        errorCount++
        errors.push(`${record.label}: ${d.detail || '未知错误'}`)
      }
    } catch (e) {
      errorCount++
      errors.push(`${record.label}: ${e.message}`)
    }
  }

  submitting.value = false
  if (errorCount === 0) {
    ElMessage.success(`全部 ${successCount} 条记录提交成功！`)
    templateRecords.value = []
  } else {
    ElMessage.warning(`成功 ${successCount} 条，失败 ${errorCount} 条`)
    if (errors.length > 0) {
      ElMessageBox.alert(errors.join('\n'), '提交错误详情')
    }
  }
}

// Quick estimate
async function doEstimate(industry) {
  estimateIndustry.value = industry
  try {
    const d = await authFetch(`${API}/wizard/estimate/${encodeURIComponent(industry)}?region=${encodeURIComponent(selectedRegion.value)}`)
    estimateResult.value = d.data
    await nextTick()
    renderEstimateChart()
  } catch (e) {
    ElMessage.error('估算失败: ' + e.message)
  }
}

function renderEstimateChart() {
  if (!estimateChartRef.value || !estimateResult.value) return
  if (estimateChart) estimateChart.dispose()
  estimateChart = echarts.init(estimateChartRef.value)

  const details = estimateResult.value.details.filter(d => d.estimated_co2 > 0)
  estimateChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} kg ({d}%)' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      label: { formatter: '{b}\n{d}%' },
      data: details.map(d => ({
        name: d.source,
        value: Math.round(d.estimated_co2),
      })),
    }],
  })
}

// Company recommendation
async function loadRecommendation(companyId) {
  if (!companyId) return
  try {
    const d = await authFetch(`${API}/wizard/recommend/${companyId}`)
    recommendData.value = d.data
  } catch (e) {
    ElMessage.error('获取推荐失败: ' + e.message)
  }
}

function quickFill(row) {
  const now = new Date()
  quickFillForm.value = {
    ...row,
    company_id: selectedCompany.value,
    record_date: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`,
  }
  quickFillVisible.value = true
}

async function submitQuickFill() {
  submitting.value = true
  try {
    const d = await authFetch(`${API}/carbon/records/`, {
      method: 'POST',
      body: JSON.stringify({
        company_id: quickFillForm.value.company_id,
        scope: quickFillForm.value.scope,
        emission_source: quickFillForm.value.emission_source,
        quantity: quickFillForm.value.quantity,
        unit: quickFillForm.value.unit,
        record_date: quickFillForm.value.record_date,
      }),
    })
    if (d.success || d.id) {
      ElMessage.success('填报成功！')
      quickFillVisible.value = false
      loadRecommendation(selectedCompany.value)
    } else {
      const detail = d.detail || ''
      if (typeof detail === 'object' && detail.errors) {
        ElMessage.error('校验未通过: ' + detail.errors.map(e => e.message).join('; '))
      } else {
        ElMessage.error('填报失败: ' + (typeof detail === 'string' ? detail : JSON.stringify(detail)))
      }
    }
  } catch (e) {
    ElMessage.error('填报失败: ' + e.message)
  }
  submitting.value = false
}

onMounted(() => {
  loadIndustries()
  loadSources()
  loadRegions()
  loadCompanies()
})

// Watch region change for estimate refresh
watch(selectedRegion, () => {
  if (estimateIndustry.value) doEstimate(estimateIndustry.value)
})
</script>

<style scoped>
.wizard-container { padding: 20px; }

.stat-row { margin-bottom: 20px; }
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.stat-card.highlight { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.stat-card.highlight .stat-label { color: rgba(255,255,255,0.8); }

.section-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #303133; }

.industry-list { max-height: 600px; overflow-y: auto; }
.industry-card {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
  cursor: pointer; border: 2px solid transparent;
  transition: all 0.2s;
}
.industry-card:hover { background: #f5f7fa; }
.industry-card.active { border-color: #409eff; background: #ecf5ff; }
.industry-icon { font-size: 24px; }
.industry-info { flex: 1; }
.industry-name { font-weight: 600; font-size: 14px; }
.industry-desc { font-size: 12px; color: #909399; margin-top: 2px; }

.empty-hint {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 300px; color: #909399;
}
.empty-hint p { margin-top: 12px; }

.template-panel { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.template-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.template-header h3 { margin: 0; }
.template-actions { display: flex; gap: 8px; align-items: center; }

.co2-value { font-weight: 600; color: #e6a23c; }
.tip-text { font-size: 12px; color: #909399; }
.total-bar {
  margin-top: 12px; padding: 12px 16px;
  background: #f5f7fa; border-radius: 6px;
  font-size: 14px;
}

.estimate-cards { display: flex; flex-direction: column; gap: 8px; }
.estimate-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-radius: 8px; cursor: pointer;
  border: 2px solid transparent; transition: all 0.2s;
}
.estimate-card:hover { background: #f5f7fa; }
.estimate-card.active { border-color: #409eff; background: #ecf5ff; }

.estimate-result { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

.recommend-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.recommend-panel { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

:deep(.warning-row) { background-color: #fdf6ec !important; }
:deep(.el-table .warning-row:hover > td) { background-color: #faecd8 !important; }
</style>
