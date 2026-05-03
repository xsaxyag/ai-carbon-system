<template>
  <div class="carbon-entry">
    <h2>碳数据录入</h2>
    
    <el-card>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="选择企业" prop="company_id">
          <el-select v-model="form.company_id" placeholder="请选择企业" filterable style="width: 300px;">
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
          <el-button type="primary" link @click="goToCompany">+ 新建企业</el-button>
        </el-form-item>
        
        <el-form-item label="记录月份" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
          />
        </el-form-item>
        
        <el-form-item label="碳排放范围" prop="scope">
          <el-radio-group v-model="form.scope" @change="onScopeChange">
            <el-radio label="scope1">范围1（直接排放）</el-radio>
            <el-radio label="scope2">范围2（间接排放）</el-radio>
            <el-radio label="scope3">范围3（其他间接）</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="排放源类型" prop="emission_source">
          <el-select v-model="form.emission_source" placeholder="请选择排放源" @change="onSourceChange" style="width: 300px;">
            <el-option
              v-for="source in currentSources"
              :key="source.value"
              :label="source.label"
              :value="source.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="消耗数量" prop="quantity">
          <el-input-number 
            v-model="form.quantity" 
            :min="0.01" 
            :precision="2" 
            :step="100"
            placeholder="请输入消耗数量"
            style="width: 250px;"
            @change="onQuantityChange"
          />
          <el-select v-model="form.unit" style="width: 100px; margin-left: 10px;">
            <el-option v-for="unit in currentUnits" :key="unit" :value="unit" :label="unit" />
          </el-select>
          <el-button type="primary" link @click="quickValidate" style="margin-left: 10px;">
            <el-icon><CircleCheck /></el-icon> 校验
          </el-button>
        </el-form-item>

        <!-- 实时校验结果 -->
        <div v-if="validationResult" style="margin-bottom: 20px;">
          <el-alert
            v-for="(err, idx) in validationResult.errors"
            :key="'e'+idx"
            :title="err.message"
            type="error"
            show-icon
            style="margin-bottom: 8px;"
          >
            <template v-if="err.suggestion" #default>
              <span style="font-size: 12px;">💡 {{ err.suggestion }}</span>
            </template>
          </el-alert>
          <el-alert
            v-for="(warn, idx) in validationResult.warnings"
            :key="'w'+idx"
            :title="warn.message"
            type="warning"
            show-icon
            :closable="true"
            style="margin-bottom: 8px;"
          >
            <template v-if="warn.suggestion" #default>
              <span style="font-size: 12px;">💡 {{ warn.suggestion }}</span>
            </template>
          </el-alert>
          <el-alert
            v-for="(info, idx) in validationResult.infos"
            :key="'i'+idx"
            :title="info.message"
            type="info"
            show-icon
            :closable="true"
            style="margin-bottom: 8px;"
          />
          <el-alert
            v-if="validationResult.passed && validationResult.errors.length === 0 && validationResult.warnings.length === 0"
            title="数据校验通过 ✓"
            type="success"
            show-icon
            :closable="true"
          />
        </div>

        <!-- 预估碳排放 -->
        <div v-if="estimatedEmission" style="margin-bottom: 20px;">
          <el-card shadow="never" style="background: #f0f9eb;">
            <div style="display: flex; align-items: center;">
              <el-icon :size="24" style="color: #67c23a; margin-right: 10px;"><DataAnalysis /></el-icon>
              <div>
                <div style="font-size: 12px; color: #909399;">预估碳排放</div>
                <div style="font-size: 24px; font-weight: bold; color: #303133;">
                  {{ estimatedEmission.co2_emission }} <span style="font-size: 14px;">kgCO2</span>
                </div>
                <div style="font-size: 12px; color: #909399;">
                  排放因子: {{ estimatedEmission.emission_factor }} kgCO2/{{ form.unit }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading" :disabled="hasErrors">
            提交记录
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 历史记录 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>碳排放记录</span>
          <div>
            <el-button type="warning" size="small" @click="batchValidate" :disabled="records.length === 0">
              批量校验
            </el-button>
            <el-button type="primary" link @click="loadRecords">刷新</el-button>
          </div>
        </div>
      </template>
      <el-table :data="records" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="company_id" label="企业ID" width="80" />
        <el-table-column prop="record_date" label="月份" width="100" />
        <el-table-column prop="scope" label="范围" width="80">
          <template #default="{ row }">
            <el-tag :type="row.scope === 'scope1' ? 'danger' : row.scope === 'scope2' ? 'warning' : 'info'" size="small">
              {{ row.scope }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="emission_source" label="排放源" width="140" />
        <el-table-column prop="quantity" label="消耗量" width="100" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="co2_emission" label="碳排放(kgCO2)" width="130">
          <template #default="{ row }">
            <span style="color: #409eff; font-weight: bold;">{{ typeof row.co2_emission === 'number' ? row.co2_emission.toFixed(2) : row.co2_emission }}</span>
          </template>
        </el-table-column>
        <el-table-column label="校验" width="60">
          <template #default="{ row }">
            <el-tag v-if="row.validation && row.validation.warnings_count > 0" type="warning" size="small">
              {{ row.validation.warnings_count }}⚠
            </el-tag>
            <el-tag v-else-if="row.validation" type="success" size="small">✓</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="deleteRecord(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量校验结果 -->
      <div v-if="batchResult" style="margin-top: 15px;">
        <el-divider>批量校验结果</el-divider>
        <el-alert
          :title="`共 ${batchResult.total} 条，通过 ${batchResult.passed} 条，问题 ${batchResult.failed} 条`"
          :type="batchResult.failed > 0 ? 'warning' : 'success'"
          show-icon
        />
        <div v-for="(r, idx) in batchResult.results" :key="idx" style="margin-top: 8px;">
          <el-alert v-for="(e, eidx) in r.errors" :key="'be'+idx+'_'+eidx" :title="e.message" type="error" show-icon style="margin-bottom: 4px;" />
          <el-alert v-for="(w, widx) in r.warnings" :key="'bw'+idx+'_'+widx" :title="w.message" type="warning" show-icon style="margin-bottom: 4px;" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, DataAnalysis } from '@element-plus/icons-vue'
import { authFetch } from '../utils/auth'

const API_BASE = 'https://ai-carbon-system.onrender.com/api/v1'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const result = ref(null)
const validationResult = ref(null)
const estimatedEmission = ref(null)
const batchResult = ref(null)

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

const hasErrors = computed(() => validationResult.value && validationResult.value.errors && validationResult.value.errors.length > 0)

// scope切换时自动更新排放源和单位
watch(() => form.scope, (newScope) => {
  const srcs = sourcesByScope[newScope] || []
  if (srcs.length > 0) {
    form.emission_source = srcs[0].value
    form.unit = srcs[0].units[0]
  }
  validationResult.value = null
  estimatedEmission.value = null
})

function onScopeChange() {
  validationResult.value = null
  estimatedEmission.value = null
}

function onSourceChange(val) {
  const src = currentSources.value.find(s => s.value === val)
  if (src) {
    form.unit = src.units[0]
  }
  validationResult.value = null
  estimatedEmission.value = null
}

function onQuantityChange() {
  // 数量变化时自动预估碳排放
  if (form.quantity > 0 && form.emission_source && form.unit) {
    estimateEmission()
  }
}

async function estimateEmission() {
  try {
    const res = await authFetch(`${API_BASE}/carbon/calculate/`, {
      method: 'POST',
      body: JSON.stringify({
        scope: form.scope,
        emission_source: form.emission_source,
        quantity: form.quantity,
        unit: form.unit
      })
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
  try {
    const res = await authFetch(`${API_BASE}/validation/validate/quick/`, {
      method: 'POST',
      body: JSON.stringify({
        scope: form.scope,
        emission_source: form.emission_source,
        quantity: form.quantity,
        unit: form.unit
      })
    })
    const data = await res.json()
    if (data.success) {
      validationResult.value = data.data
    }
  } catch (e) {
    ElMessage.error('校验请求失败')
  }
}

async function fullValidate() {
  if (!form.company_id || !form.record_date) {
    return // 表单不完整，跳过全量校验
  }
  try {
    const res = await authFetch(`${API_BASE}/validation/validate/`, {
      method: 'POST',
      body: JSON.stringify({
        company_id: form.company_id,
        scope: form.scope,
        emission_source: form.emission_source,
        quantity: form.quantity,
        unit: form.unit,
        record_date: form.record_date
      })
    })
    const data = await res.json()
    if (data.success) {
      validationResult.value = data.data
    }
  } catch (e) {
    // 校验失败不阻断流程
  }
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
  } catch (e) {
    companies.value = []
  }
}

async function loadRecords() {
  try {
    const res = await authFetch(`${API_BASE}/carbon/records/`)
    records.value = await res.json()
  } catch (e) {
    records.value = []
  }
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 提交前自动全量校验
    await fullValidate()
    if (hasErrors.value) {
      ElMessage.error('数据校验未通过，请修正后重试')
      return
    }
    
    // 如果有warning，确认后继续
    if (validationResult.value && validationResult.value.warnings && validationResult.value.warnings.length > 0) {
      try {
        await ElMessageBox.confirm(
          `存在 ${validationResult.value.warnings.length} 条警告，是否继续提交？`,
          '数据校验警告',
          { type: 'warning' }
        )
      } catch {
        return // 用户取消
      }
    }

    loading.value = true
    try {
      const res = await authFetch(`${API_BASE}/carbon/records/`, {
        method: 'POST',
        body: JSON.stringify(form)
      })
      const data = await res.json()
      if (res.ok) {
        result.value = data
        ElMessage.success(`提交成功！碳排放: ${data.co2_emission} kgCO2`)
        if (data.validation && data.validation.warnings_count > 0) {
          ElMessage.warning(`有 ${data.validation.warnings_count} 条校验警告`)
        }
        loadRecords()
        resetForm()
      } else {
        // 处理422校验错误
        if (data.detail && data.detail.errors) {
          validationResult.value = {
            passed: false,
            errors: data.detail.errors || [],
            warnings: data.detail.warnings || [],
            infos: []
          }
          ElMessage.error('数据校验未通过')
        } else {
          ElMessage.error(data.detail || '提交失败')
        }
      }
    } catch (e) {
      ElMessage.error('提交失败')
    }
    loading.value = false
  })
}

async function batchValidate() {
  if (records.value.length === 0) return
  try {
    const batchData = records.value.map(r => ({
      company_id: r.company_id,
      scope: r.scope,
      emission_source: r.emission_source,
      quantity: r.quantity,
      unit: r.unit,
      record_date: r.record_date
    }))
    const res = await authFetch(`${API_BASE}/validation/validate/batch/`, {
      method: 'POST',
      body: JSON.stringify({ records: batchData })
    })
    const data = await res.json()
    if (data.success) {
      batchResult.value = data.data
    }
  } catch (e) {
    ElMessage.error('批量校验失败')
  }
}

function resetForm() {
  formRef.value?.resetFields()
  result.value = null
  validationResult.value = null
  estimatedEmission.value = null
}

async function deleteRecord(id) {
  try {
    await ElMessageBox.confirm('确定删除此记录？', '提示', { type: 'warning' })
    await authFetch(`${API_BASE}/carbon/records/${id}/`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadRecords()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function goToCompany() {
  router.push('/company')
}
</script>

<style scoped>
.carbon-entry {
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
</style>
