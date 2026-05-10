<template>
  <div class="carbon-entry">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="32"><DataAnalysis /></el-icon>
        </div>
        <div>
          <h2>碳数据录入</h2>
          <p class="header-desc">录入企业碳排放数据，系统自动计算排放量并提供智能校验</p>
        </div>
      </div>
    </div>

    <!-- 录入表单 -->
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="form-header">
          <el-icon><Edit /></el-icon>
          <span>数据录入表单</span>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="130px" size="large">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="选择企业" prop="company_id">
              <el-select v-model="form.company_id" placeholder="请选择企业" filterable style="width: 100%;">
                <el-option v-for="company in companies" :key="company.id" :label="company.name" :value="company.id" />
              </el-select>
              <el-button type="primary" link @click="goToCompany" class="add-btn">
                <el-icon><CirclePlus /></el-icon> 新建企业
              </el-button>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="记录月份" prop="record_date">
              <el-date-picker v-model="form.record_date" type="month" placeholder="选择月份" format="YYYY-MM" value-format="YYYY-MM" style="width: 100%;" :shortcuts="monthShortcuts" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="碳排放范围" prop="scope">
          <el-radio-group v-model="form.scope" @change="onScopeChange" class="scope-radio-group">
            <el-radio-button label="scope1">
              <el-icon><HotWater /></el-icon> 范围1（直接排放）
            </el-radio-button>
            <el-radio-button label="scope2">
              <el-icon><Lightning /></el-icon> 范围2（能源间接）
            </el-radio-button>
            <el-radio-button label="scope3">
              <el-icon><Connection /></el-icon> 范围3（其他间接）
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="排放源类型" prop="emission_source">
              <el-select v-model="form.emission_source" placeholder="请选择排放源" @change="onSourceChange" style="width: 100%;">
                <el-option v-for="source in currentSources" :key="source.value" :label="source.label" :value="source.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="消耗数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="0.01" :precision="2" :step="100" placeholder="请输入消耗数量" style="width: 100%;" @change="onQuantityChange" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="form.unit" style="width: 100%;">
                <el-option v-for="unit in currentUnits" :key="unit" :value="unit" :label="unit" />
              </el-select>
              <el-button type="primary" link @click="quickValidate" class="validate-btn" :loading="validating">
                <el-icon><CircleCheck /></el-icon> 实时校验
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 预估碳排放 -->
        <transition name="el-fade-in-linear">
          <div v-if="estimatedEmission" class="emission-preview">
            <div class="preview-header">
              <el-icon :size="20"><DataAnalysis /></el-icon>
              <span>预估碳排放</span>
            </div>
            <div class="preview-body">
              <div class="preview-value">
                <span class="value-number">{{ estimatedEmission.co2_emission }}</span>
                <span class="value-unit">kgCO₂</span>
              </div>
              <div class="preview-detail">
                排放因子: <b>{{ estimatedEmission.emission_factor }}</b> kgCO₂/{{ form.unit }}
              </div>
            </div>
          </div>
        </transition>

        <!-- 校验结果 -->
        <transition-group name="el-zoom-in-top" tag="div">
          <div v-for="(err, idx) in validationResult.errors" :key="'e'+idx" style="margin-bottom: 8px;">
            <el-alert :title="err.message" type="error" show-icon :closable="true" @close="removeError(idx)" style="border-radius: 8px;">
              <template v-if="err.suggestion" #default>
                <div style="font-size: 12px; margin-top: 4px;"><el-icon><InfoFilled /></el-icon> {{ err.suggestion }}</div>
              </template>
            </el-alert>
          </div>
          <div v-for="(warn, idx) in validationResult.warnings" :key="'w'+idx" style="margin-bottom: 8px;">
            <el-alert :title="warn.message" type="warning" show-icon :closable="true" @close="removeWarning(idx)" style="border-radius: 8px;">
              <template v-if="warn.suggestion" #default>
                <div style="font-size: 12px; margin-top: 4px;"><el-icon><InfoFilled /></el-icon> {{ warn.suggestion }}</div>
              </template>
            </el-alert>
          </div>
          <div v-for="(info, idx) in validationResult.infos" :key="'i'+idx" style="margin-bottom: 8px;">
            <el-alert :title="info.message" type="info" show-icon :closable="true" @close="removeInfo(idx)" style="border-radius: 8px;" />
          </div>
          <div v-if="validationResult.passed && validationResult.errors.length === 0 && validationResult.warnings.length === 0" :key="'ok'" style="margin-bottom: 12px;">
            <el-alert title="数据校验通过 ✓" type="success" show-icon :closable="true" style="border-radius: 8px;" />
          </div>
        </transition-group>

        <el-form-item style="margin-top: 24px;">
          <el-button type="primary" @click="submitForm" :loading="loading" :disabled="hasErrors" size="large" round style="min-width: 140px;">
            <el-icon><Check /></el-icon> 提交记录
          </el-button>
          <el-button @click="resetForm" size="large" round>重置</el-button>
          <el-tooltip v-if="hasErrors" content="请先修正数据错误后再提交" placement="top">
            <el-icon style="margin-left: 8px; color: #f56c6c;"><WarningFilled /></el-icon>
          </el-tooltip>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="records-card" style="margin-top: 24px;" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><List /></el-icon>
            <span>碳排放记录</span>
            <el-tag type="info" size="small" effect="plain" round>{{ records.length }} 条</el-tag>
          </div>
          <div class="header-right">
            <el-button type="warning" size="small" @click="batchValidate" :disabled="records.length === 0" :loading="batchLoading" round>
              <el-icon><Finished /></el-icon> 批量校验
            </el-button>
            <el-button type="primary" link @click="loadRecords" :loading="loadingRecords" size="small">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="records" stripe size="large" max-height="420" style="width: 100%;" :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: '600' }" :row-style="{ transition: 'all 0.3s' }" row-key="id" :expand-row-keys="expandedRows" @expand-change="handleExpandChange">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div style="padding: 16px; background: #f5f7fa; border-radius: 8px;">
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="记录ID">{{ row.id }}</el-descriptions-item>
                <el-descriptions-item label="企业ID">{{ row.company_id }}</el-descriptions-item>
                <el-descriptions-item label="记录月份">{{ row.record_date }}</el-descriptions-item>
                <el-descriptions-item label="范围">{{ scopeLabel(row.scope) }}</el-descriptions-item>
                <el-descriptions-item label="排放源">{{ sourceLabel(row.emission_source) }}</el-descriptions-item>
                <el-descriptions-item label="排放量">{{ row.co2_emission?.toFixed(2) }} kgCO₂</el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="record_date" label="月份" width="110" />
        <el-table-column prop="scope" label="范围" width="110">
          <template #default="{ row }">
            <el-tag :type="row.scope === 'scope1' ? 'danger' : row.scope === 'scope2' ? 'warning' : 'success'" size="small" effect="dark" round>
              {{ scopeLabel(row.scope) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="emission_source" label="排放源" width="140">
          <template #default="{ row }">{{ sourceLabel(row.emission_source) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="消耗量" width="110" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="co2_emission" label="碳排放" width="140">
          <template #default="{ row }">
            <span style="color: #409eff; font-weight: bold; font-size: 15px;">
              {{ typeof row.co2_emission === 'number' ? row.co2_emission.toFixed(2) : row.co2_emission }}
            </span>
            <span style="font-size: 12px; color: #909399;"> kgCO₂</span>
          </template>
        </el-table-column>
        <el-table-column label="校验" width="90" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="row.validation && row.validation.warnings_count > 0" :content="row.validation.warnings.map(w => w.message).join('; ')" placement="top">
              <el-tag type="warning" size="small" effect="dark" round>{{ row.validation.warnings_count }} ⚠</el-tag>
            </el-tooltip>
            <el-tag v-else-if="row.validation" type="success" size="small" effect="dark" round>✓</el-tag>
            <span v-else style="color: #c0c4cc;">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-popconfirm title="确定删除此记录？" @confirm="deleteRecord(row.id)" placement="top">
              <template #reference>
                <el-button type="danger" link size="small"><el-icon><Delete /></el-icon> 删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量校验结果 -->
      <transition name="el-zoom-in-top">
        <div v-if="batchResult" style="margin-top: 20px;">
          <el-divider content-position="left"><el-icon><InfoFilled /></el-icon> 批量校验结果</el-divider>
          <el-alert :title="`共 ${batchResult.total} 条，通过 ${batchResult.passed} 条，问题 ${batchResult.failed} 条`" :type="batchResult.failed > 0 ? 'warning' : 'success'" show-icon :closable="true" @close="batchResult = null" style="border-radius: 8px;" />
          <div v-for="(r, idx) in batchResult.results" :key="idx" style="margin-top: 10px;">
            <el-alert v-for="(e, eidx) in r.errors" :key="'be'+idx+'_'+eidx" :title="`记录 ${r.index !== undefined ? r.index + 1 : idx + 1}: ${e.message}`" type="error" show-icon style="margin-bottom: 6px; border-radius: 8px;" />
            <el-alert v-for="(w, widx) in r.warnings" :key="'bw'+idx+'_'+widx" :title="`记录 ${r.index !== undefined ? r.index + 1 : idx + 1}: ${w.message}`" type="warning" show-icon style="margin-bottom: 6px; border-radius: 8px;" />
          </div>
        </div>
      </transition>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, DataAnalysis, Edit, HotWater, Lightning, Connection, CirclePlus, InfoFilled, WarningFilled, Check, List, Finished, Refresh, Delete } from '@element-plus/icons-vue'
import { authFetch, API_BASE } from '../utils/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const loadingRecords = ref(false)
const validating = ref(false)
const batchLoading = ref(false)
const result = ref(null)
const validationResult = reactive({ passed: false, errors: [], warnings: [], infos: [] })
const estimatedEmission = ref(null)
const batchResult = ref(null)
const expandedRows = ref([])

const form = reactive({
  company_id: null,
  record_date: '',
  scope: 'scope2',
  emission_source: 'electricity',
  quantity: null,
  unit: 'kWh'
})

const rules = {
  company_id: [{ required: true, message: '请选择企业', trigger: 'change' }],
  record_date: [{ required: true, message: '请选择月份', trigger: 'change' }],
  scope: [{ required: true, message: '请选择范围', trigger: 'change' }],
  emission_source: [{ required: true, message: '请选择排放源', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入消耗量', trigger: 'blur' }]
}

const monthShortcuts = [
  { text: '本月', value: new Date() },
  { text: '上月', value: new Date(new Date().setMonth(new Date().getMonth() - 1)) },
  { text: '本季度', value: new Date() },
]

const sourcesByScope = {
  scope1: [
    { value: 'natural_gas', label: '天然气', units: ['m3', 'GJ'] },
    { value: 'coal', label: '煤炭', units: ['kg', 't'] },
    { value: 'gasoline', label: '汽油', units: ['L', 'kg'] },
    { value: 'diesel', label: '柴油', units: ['L', 'kg'] }
  ],
  scope2: [
    { value: 'electricity', label: '外购电力', units: ['kWh', 'MWh'] }
  ],
  scope3: [
    { value: 'renewable', label: '可再生能源(绿电)', units: ['kWh', 'MWh'] },
    { value: 'business_flight_short', label: '短途航班(<3h)', units: ['km'] },
    { value: 'business_flight_medium', label: '中途航班(3-6h)', units: ['km'] },
    { value: 'business_flight_long', label: '长途航班(>6h)', units: ['km'] },
    { value: 'business_train', label: '火车', units: ['km'] },
    { value: 'business_car', label: '公务汽车', units: ['km', 'L'] },
    { value: 'waste_landfill', label: '填埋处理', units: ['kg', 't'] },
    { value: 'waste_incineration', label: '焚烧处理', units: ['kg', 't'] },
    { value: 'waste_composting', label: '堆肥处理', units: ['kg', 't'] },
    { value: 'purchased_office', label: '办公用品采购', units: ['CNY'] },
    { value: 'purchased_equipment', label: '设备采购', units: ['CNY'] }
  ]
}

const currentSources = computed(() => sourcesByScope[form.scope] || [])
const currentUnits = computed(() => {
  const src = currentSources.value.find(s => s.value === form.emission_source)
  return src ? src.units : ['kWh']
})

const hasErrors = computed(() => validationResult.errors && validationResult.errors.length > 0)

const scopeLabelMap = { scope1: '范围1 直接排放', scope2: '范围2 能源间接', scope3: '范围3 其他间接' }
const sourceLabelMap = {
  natural_gas: '天然气', coal: '煤炭', gasoline: '汽油', diesel: '柴油',
  electricity: '外购电力', renewable: '绿电',
  business_flight_short: '短途航班', business_flight_medium: '中途航班', business_flight_long: '长途航班',
  business_train: '火车', business_car: '公务汽车',
  waste_landfill: '填埋', waste_incineration: '焚烧', waste_composting: '堆肥',
  purchased_office: '办公用品', purchased_equipment: '设备采购'
}
const scopeLabel = (s) => scopeLabelMap[s] || s
const sourceLabel = (s) => sourceLabelMap[s] || s

// scope切换时自动更新排放源和单位
watch(() => form.scope, (newScope) => {
  const srcs = sourcesByScope[newScope] || []
  if (srcs.length > 0) {
    form.emission_source = srcs[0].value
    form.unit = srcs[0].units[0]
  }
  Object.assign(validationResult, { passed: false, errors: [], warnings: [], infos: [] })
  estimatedEmission.value = null
})

function onScopeChange() {
  Object.assign(validationResult, { passed: false, errors: [], warnings: [], infos: [] })
  estimatedEmission.value = null
}

function onSourceChange(val) {
  const src = currentSources.value.find(s => s.value === val)
  if (src) form.unit = src.units[0]
  Object.assign(validationResult, { passed: false, errors: [], warnings: [], infos: [] })
  estimatedEmission.value = null
}

function onQuantityChange() {
  if (form.quantity > 0 && form.emission_source && form.unit) {
    estimateEmission()
  }
}

async function estimateEmission() {
  try {
    const res = await authFetch(`${API_BASE}/carbon/calculate/`, {
      method: 'POST',
      body: JSON.stringify({ scope: form.scope, emission_source: form.emission_source, quantity: form.quantity, unit: form.unit })
    })
    const data = await res.json()
    estimatedEmission.value = data
  } catch (e) {
    estimatedEmission.value = null
  }
}

async function quickValidate() {
  if (!form.emission_source || !form.unit || !form.quantity) {
    ElMessage.warning('请先填写完整数据')
    return
  }
  validating.value = true
  try {
    const res = await authFetch(`${API_BASE}/validation/validate/quick/`, {
      method: 'POST',
      body: JSON.stringify({ scope: form.scope, emission_source: form.emission_source, quantity: form.quantity, unit: form.unit })
    })
    const data = await res.json()
    if (data.success) {
      Object.assign(validationResult, data.data)
    }
  } catch (e) {
    ElMessage.error('校验请求失败')
  }
  validating.value = false
}

function removeError(idx) { validationResult.errors.splice(idx, 1) }
function removeWarning(idx) { validationResult.warnings.splice(idx, 1) }
function removeInfo(idx) { validationResult.infos.splice(idx, 1) }

async function fullValidate() {
  if (!form.company_id || !form.record_date) return
  try {
    const res = await authFetch(`${API_BASE}/validation/validate/`, {
      method: 'POST',
      body: JSON.stringify({ company_id: form.company_id, scope: form.scope, emission_source: form.emission_source, quantity: form.quantity, unit: form.unit, record_date: form.record_date })
    })
    const data = await res.json()
    if (data.success) {
      Object.assign(validationResult, data.data)
    }
  } catch (e) {}
}

const companies = ref([])
const records = ref([])

onMounted(() => {
  loadCompanies()
  loadRecords()
})

async function loadCompanies() {
  try {
    const res = await authFetch(`${API_BASE}/carbon/company/`)
    companies.value = await res.json()
  } catch (e) { companies.value = [] }
}

async function loadRecords() {
  loadingRecords.value = true
  try {
    const res = await authFetch(`${API_BASE}/carbon/records/`)
    records.value = await res.json()
  } catch (e) { records.value = [] }
  loadingRecords.value = false
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    await fullValidate()
    if (hasErrors.value) {
      ElMessage.error('数据校验未通过，请修正后重试')
      return
    }

    if (validationResult.warnings && validationResult.warnings.length > 0) {
      try {
        await ElMessageBox.confirm(`存在 ${validationResult.warnings.length} 条警告，是否继续提交？`, '数据校验警告', { type: 'warning' })
      } catch { return }
    }

    loading.value = true
    try {
      const res = await authFetch(`${API_BASE}/carbon/records/`, { method: 'POST', body: JSON.stringify(form) })
      const data = await res.json()
      if (res.ok) {
        result.value = data
        ElMessage.success(`提交成功！碳排放: ${data.co2_emission} kgCO₂`)
        if (data.validation && data.validation.warnings_count > 0) {
          ElMessage.warning(`有 ${data.validation.warnings_count} 条校验警告`)
        }
        loadRecords()
        resetForm()
      } else {
        if (data.detail && data.detail.errors) {
          Object.assign(validationResult, { passed: false, errors: data.detail.errors || [], warnings: data.detail.warnings || [], infos: [] })
          ElMessage.error('数据校验未通过')
        } else {
          ElMessage.error(data.detail || '提交失败')
        }
      }
    } catch (e) { ElMessage.error('提交失败') }
    loading.value = false
  })
}

async function batchValidate() {
  if (records.value.length === 0) return
  batchLoading.value = true
  try {
    const batchData = records.value.map(r => ({ company_id: r.company_id, scope: r.scope, emission_source: r.emission_source, quantity: r.quantity, unit: r.unit, record_date: r.record_date }))
    const res = await authFetch(`${API_BASE}/validation/validate/batch/`, { method: 'POST', body: JSON.stringify({ records: batchData }) })
    const data = await res.json()
    if (data.success) { batchResult.value = data.data }
  } catch (e) { ElMessage.error('批量校验失败') }
  batchLoading.value = false
}

function resetForm() {
  formRef.value?.resetFields()
  result.value = null
  Object.assign(validationResult, { passed: false, errors: [], warnings: [], infos: [] })
  estimatedEmission.value = null
}

async function deleteRecord(id) {
  try {
    await ElMessageBox.confirm('确定删除此记录？', '提示', { type: 'warning' })
    await authFetch(`${API_BASE}/carbon/records/${id}/`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadRecords()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

function handleExpandChange(row, expanded) {
  expandedRows.value = expanded ? [row.id] : []
}

function goToCompany() {
  router.push('/company')
}
</script>

<style scoped>
.carbon-entry { padding: 24px; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }

/* 页面标题区 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(102,126,234,0.25);
  animation: fadeInUp 0.6s ease both;
}
.header-content { display: flex; align-items: center; gap: 20px; color: #fff; }
.header-icon { width: 64px; height: 64px; border-radius: 16px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
h2 { font-size: 26px; font-weight: 700; margin: 0; color: #fff; }
.header-desc { font-size: 14px; color: rgba(255,255,255,0.85); margin-top: 6px; }

/* 表单卡片 */
.form-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.1s ease both; }
.form-card :deep(.el-card__header) { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); font-size: 16px; font-weight: 600; color: #303133; padding: 16px 24px; }
.form-header { display: flex; align-items: center; gap: 8px; }
.form-header .el-icon { font-size: 20px; color: #409eff; }

/* scope 单选按钮组 */
.scope-radio-group { display: flex; gap: 12px; flex-wrap: wrap; }
.scope-radio-group :deep(.el-radio-button__inner) { border-radius: 10px !important; padding: 10px 20px; font-size: 14px; display: flex; align-items: center; gap: 6px; transition: all 0.3s; }
.scope-radio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) { background: linear-gradient(135deg, #409eff 0%, #3a7bd5 100%); border-color: #409eff; box-shadow: 0 4px 12px rgba(64,158,255,0.3); }

/* 预估碳排放预览 */
.emission-preview {
  margin: 20px 0; border-radius: 12px; overflow: hidden;
  background: linear-gradient(135deg, #ecf5ff 0%, #e0f2fe 100%);
  border: 1px solid #b3d8fd;
  animation: fadeInUp 0.4s ease both;
}
.preview-header { display: flex; align-items: center; gap: 8px; padding: 12px 20px; background: rgba(64,158,255,0.1); font-weight: 600; color: #303133; font-size: 14px; }
.preview-body { padding: 16px 20px; }
.preview-value { display: flex; align-items: baseline; gap: 8px; }
.value-number { font-size: 36px; font-weight: 800; color: #409eff; }
.value-unit { font-size: 14px; color: #909399; }
.preview-detail { margin-top: 8px; font-size: 13px; color: #606266; }

/* 按钮 */
.add-btn, .validate-btn { margin-left: 10px; font-size: 13px; }
.validate-btn { color: #67c23a; }

/* 记录卡片 */
.records-card { border-radius: 16px; border: none; animation: fadeInUp 0.6s 0.2s ease both; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: #303133; }
.header-left .el-tag { margin-left: 8px; }
.header-right { display: flex; gap: 8px; align-items: center; }

/* 表格 */
:deep(.el-table) { border-radius: 12px; overflow: hidden; }
:deep(.el-table__row) { transition: all 0.3s ease; }
:deep(.el-table__row:hover) { background: #ecf5ff !important; transform: scale(1.002); }

/* 展开行 */
:deep(.el-table__expanded-cell) { padding: 0 !important; }
:deep(.el-descriptions) { margin: 8px; }

/* 删除确认 */
:deep(.el-popconfirm__main) { font-size: 14px; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 768px) {
  .carbon-entry { padding: 12px; }
  .page-header { padding: 20px; }
  h2 { font-size: 22px; }
  .scope-radio-group { flex-direction: column; }
  .header-content { flex-direction: column; text-align: center; }
}
</style>
