<template>
  <div class="company-manage">
    <h2>企业管理</h2>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>企业列表</span>
          <el-button type="primary" @click="showDialog()">+ 添加企业</el-button>
        </div>
      </template>
      
      <el-table :data="companies" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="企业名称" />
        <el-table-column prop="registration_no" label="统一社会信用代码" width="180" />
        <el-table-column prop="industry" label="所属行业" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.industry || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" width="180" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button type="text" size="small" @click="deleteCompany(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="total > pageSize"
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        @current-change="loadCompanies"
        style="margin-top: 20px; text-align: center;"
      />
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑企业' : '添加企业'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="企业名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入企业名称" />
        </el-form-item>
        <el-form-item label="信用代码" prop="registration_no">
          <el-input v-model="form.registration_no" placeholder="统一社会信用代码" />
        </el-form-item>
        <el-form-item label="所属行业" prop="industry">
          <el-select v-model="form.industry" placeholder="请选择行业" filterable>
            <el-option v-for="ind in industries" :key="ind" :value="ind" :label="ind" />
          </el-select>
        </el-form-item>
        <el-form-item label="企业地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="企业地址" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const companies = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)
const total = ref(0)
const pageSize = 10
const editingId = ref(null)

const industries = [
  '制造业', '信息技术', '金融服务', '批发零售', '交通运输',
  '建筑房地产', '教育培训', '医疗卫生', '文化传媒', '科学研究'
]

const form = reactive({
  name: '',
  registration_no: '',
  industry: '',
  address: ''
})

const rules = {
  name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
}

onMounted(() => {
  loadCompanies()
})

async function loadCompanies() {
  loading.value = true
  try {
    const res = await fetch('/api/v1/carbon/company/')
    companies.value = await res.json()
    total.value = companies.value.length
  } catch (e) {
    companies.value = []
  }
  loading.value = false
}

function showDialog(company = null) {
  if (company) {
    isEdit.value = true
    editingId.value = company.id
    Object.assign(form, company)
  } else {
    isEdit.value = false
    editingId.value = null
    Object.assign(form, { name: '', registration_no: '', industry: '', address: '' })
  }
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      const url = isEdit.value ? `/api/v1/carbon/company/${editingId.value}/` : '/api/v1/carbon/company/'
      const method = isEdit.value ? 'PUT' : 'POST'
      
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      loadCompanies()
    } catch (e) {
      ElMessage.error('操作失败')
    }
    saving.value = false
  })
}

async function deleteCompany(id) {
  try {
    await ElMessageBox.confirm('确定要删除该企业吗?', '提示', {
      type: 'warning'
    })
    await fetch(`/api/v1/carbon/company/${id}/`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadCompanies()
  } catch (e) {
    // cancelled
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.company-manage {
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