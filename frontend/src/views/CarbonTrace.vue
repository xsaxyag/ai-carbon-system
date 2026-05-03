<template>
  <div class="carbon-trace">
    <h2>产品碳足迹追踪</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ products.length }}</div>
              <div class="stat-label">产品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ calculatedCount }}</div>
              <div class="stat-label">已计算</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ avgFootprint.toFixed(2) }}</div>
              <div class="stat-label">平均足迹(kgCO2)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ highFootprintCount }}</div>
              <div class="stat-label">高排放产品</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <!-- 产品列表 -->
      <el-tab-pane label="产品管理" name="products">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>产品碳足迹档案</span>
              <el-button type="primary" @click="showAddProductDialog">
                <el-icon><Plus /></el-icon>
                新增产品
              </el-button>
            </div>
          </template>

          <el-table :data="products" stripe v-loading="loading">
            <el-table-column prop="product_name" label="产品名称" min-width="150" />
            <el-table-column prop="product_code" label="产品编号" width="120" />
            <el-table-column prop="category" label="类别" width="100" />
            <el-table-column prop="functional_unit" label="功能单位" width="100" />
            <el-table-column prop="lifespan_years" label="生命周期(年)" width="120" />
            <el-table-column prop="total_footprint" label="碳足迹(kgCO2)" width="140">
              <template #default="{ row }">
                <span v-if="row.total_footprint" :style="{color: row.total_footprint > 100 ? '#f56c6c' : '#67c23a'}">
                  {{ row.total_footprint.toFixed(2) }}
                </span>
                <span v-else style="color: #909399;">未计算</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160" />
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewProduct(row)">详情</el-button>
                <el-button type="success" size="small" @click="calculateFootprint(row)">计算</el-button>
                <el-button type="danger" size="small" @click="deleteProduct(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 产品对比 -->
      <el-tab-pane label="产品对比" name="compare">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>选择产品进行对比</span>
              <el-button type="primary" @click="runComparison" :disabled="selectedProducts.length < 2">
                开始对比
              </el-button>
            </div>
          </template>

          <el-checkbox-group v-model="selectedProducts">
            <el-row :gutter="15">
              <el-col :span="6" v-for="p in products" :key="p.id">
                <el-checkbox :label="p.id" style="margin-bottom: 10px;">
                  {{ p.product_name }} ({{ p.product_code || '无编号' }})
                </el-checkbox>
              </el-col>
            </el-row>
          </el-checkbox-group>

          <!-- 对比结果 -->
          <div v-if="comparisonResult" style="margin-top: 20px;">
            <el-divider>对比结果</el-divider>
            <el-table :data="comparisonResult.products" stripe>
              <el-table-column prop="product_name" label="产品" />
              <el-table-column prop="total_footprint" label="碳足迹(kgCO2)">
                <template #default="{ row }">{{ row.total_footprint?.toFixed(2) || '-' }}</template>
              </el-table-column>
              <el-table-column label="相对排名">
                <template #default="{ row }">
                  <el-tag :type="row.rank === 1 ? 'success' : row.rank === comparisonResult.products.length ? 'danger' : 'info'">
                    第{{ row.rank }}名
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <el-alert v-if="comparisonResult.best" type="success" style="margin-top: 15px;">
              最优产品：{{ comparisonResult.best.product_name }}，碳足迹 {{ comparisonResult.best.total_footprint?.toFixed(2) }} kgCO2
            </el-alert>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 新增产品对话框 -->
    <el-dialog v-model="productDialogVisible" title="新增产品碳足迹档案" width="600px">
      <el-form :model="productForm" label-width="120px">
        <el-form-item label="产品名称" required>
          <el-input v-model="productForm.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品编号">
          <el-input v-model="productForm.product_code" placeholder="可选" />
        </el-form-item>
        <el-form-item label="产品类别">
          <el-select v-model="productForm.category" placeholder="选择类别">
            <el-option label="电子产品" value="电子产品" />
            <el-option label="机械设备" value="机械设备" />
            <el-option label="纺织品" value="纺织品" />
            <el-option label="食品饮料" value="食品饮料" />
            <el-option label="化工产品" value="化工产品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="功能单位">
          <el-input v-model="productForm.functional_unit" placeholder="如：件、kg、m²" />
        </el-form-item>
        <el-form-item label="生命周期">
          <el-input-number v-model="productForm.lifespan_years" :min="0.1" :precision="1" /> 年
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="productForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProduct">确定</el-button>
      </template>
    </el-dialog>

    <!-- 产品详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="currentProduct?.product_name" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="产品名称">{{ currentProduct?.product_name }}</el-descriptions-item>
        <el-descriptions-item label="产品编号">{{ currentProduct?.product_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="类别">{{ currentProduct?.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="功能单位">{{ currentProduct?.functional_unit }}</el-descriptions-item>
        <el-descriptions-item label="生命周期">{{ currentProduct?.lifespan_years }} 年</el-descriptions-item>
        <el-descriptions-item label="总碳足迹">
          <span v-if="currentProduct?.total_footprint" style="font-weight: bold; color: #409eff;">
            {{ currentProduct.total_footprint.toFixed(2) }} kgCO2
          </span>
          <span v-else>未计算</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 生命周期阶段 -->
      <el-divider>生命周期阶段</el-divider>
      <el-button type="primary" size="small" @click="showAddStageDialog" style="margin-bottom: 15px;">
        <el-icon><Plus /></el-icon> 添加阶段
      </el-button>
      
      <el-table :data="currentProduct?.stages || []" stripe size="small">
        <el-table-column prop="stage" label="阶段" width="120">
          <template #default="{ row }">{{ stageLabels[row.stage] || row.stage }}</template>
        </el-table-column>
        <el-table-column prop="material_name" label="物料/活动" width="150" />
        <el-table-column prop="quantity" label="用量" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="emission" label="排放量(kgCO2)" width="120">
          <template #default="{ row }">{{ row.emission?.toFixed(4) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="source" label="数据来源" />
      </el-table>
    </el-dialog>

    <!-- 添加阶段对话框 -->
    <el-dialog v-model="stageDialogVisible" title="添加生命周期阶段" width="500px">
      <el-form :model="stageForm" label-width="100px">
        <el-form-item label="阶段" required>
          <el-select v-model="stageForm.stage" placeholder="选择阶段">
            <el-option v-for="(label, key) in stageLabels" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料名称" required>
          <el-input v-model="stageForm.material_name" placeholder="如：钢材、电力" />
        </el-form-item>
        <el-form-item label="用量" required>
          <el-input-number v-model="stageForm.quantity" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="单位" required>
          <el-input v-model="stageForm.unit" placeholder="如：kg、kWh、km" />
        </el-form-item>
        <el-form-item label="排放因子">
          <el-input-number v-model="stageForm.emission_factor" :min="0" :precision="4" />
          <span style="color: #909399; font-size: 12px; margin-left: 10px;">kgCO2/单位</span>
        </el-form-item>
        <el-form-item label="数据来源">
          <el-input v-model="stageForm.source" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStage">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authFetch } from '../utils/auth'
import { Box, DataAnalysis, TrendCharts, Warning, Plus } from '@element-plus/icons-vue'

const API_BASE = 'https://ai-carbon-system.onrender.com/api/v1/footprint'

const activeTab = ref('products')
const loading = ref(false)
const products = ref([])
const stages = ref({})
const stageLabels = {
  raw_material: '原材料获取',
  manufacturing: '生产制造',
  transportation: '运输配送',
  use: '使用阶段',
  end_of_life: '废弃处置'
}

const productDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const stageDialogVisible = ref(false)
const currentProduct = ref(null)
const selectedProducts = ref([])
const comparisonResult = ref(null)

const productForm = reactive({
  product_name: '',
  product_code: '',
  category: '',
  functional_unit: '件',
  lifespan_years: 1,
  description: ''
})

const stageForm = reactive({
  stage: 'raw_material',
  material_name: '',
  quantity: 1,
  unit: 'kg',
  emission_factor: 0,
  source: ''
})

const calculatedCount = computed(() => products.value.filter(p => p.total_footprint).length)
const avgFootprint = computed(() => {
  const calculated = products.value.filter(p => p.total_footprint)
  if (calculated.length === 0) return 0
  return calculated.reduce((sum, p) => sum + p.total_footprint, 0) / calculated.length
})
const highFootprintCount = computed(() => products.value.filter(p => p.total_footprint && p.total_footprint > 100).length)

onMounted(() => {
  loadProducts()
  loadStages()
})

async function loadProducts() {
  loading.value = true
  try {
    const res = await authFetch(`${API_BASE}/products`)
    const data = await res.json()
    products.value = data.data || []
  } catch (e) {
    console.error('加载产品失败', e)
  } finally {
    loading.value = false
  }
}

async function loadStages() {
  try {
    const res = await authFetch(`${API_BASE}/stages`)
    const data = await res.json()
    stages.value = data.data || {}
  } catch (e) {
    console.error('加载阶段定义失败', e)
  }
}

function showAddProductDialog() {
  Object.assign(productForm, {
    product_name: '',
    product_code: '',
    category: '',
    functional_unit: '件',
    lifespan_years: 1,
    description: ''
  })
  productDialogVisible.value = true
}

async function submitProduct() {
  if (!productForm.product_name) {
    ElMessage.warning('请输入产品名称')
    return
  }
  try {
    const res = await authFetch(`${API_BASE}/products`, {
      method: 'POST',
      body: JSON.stringify(productForm)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('产品创建成功')
      productDialogVisible.value = false
      loadProducts()
    }
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

async function viewProduct(product) {
  try {
    const res = await authFetch(`${API_BASE}/products/${product.id}`)
    const data = await res.json()
    currentProduct.value = data.data
    detailDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

async function calculateFootprint(product) {
  try {
    const res = await authFetch(`${API_BASE}/products/${product.id}/calculate`, {
      method: 'POST'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`计算完成：${data.data.total_footprint.toFixed(2)} kgCO2`)
      loadProducts()
    }
  } catch (e) {
    ElMessage.error('计算失败')
  }
}

async function deleteProduct(product) {
  try {
    await ElMessageBox.confirm(`确定删除产品"${product.product_name}"？`, '提示', { type: 'warning' })
    const res = await authFetch(`${API_BASE}/products/${product.id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadProducts()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function showAddStageDialog() {
  Object.assign(stageForm, {
    stage: 'raw_material',
    material_name: '',
    quantity: 1,
    unit: 'kg',
    emission_factor: 0,
    source: ''
  })
  stageDialogVisible.value = true
}

async function submitStage() {
  if (!currentProduct.value) return
  try {
    const res = await authFetch(`${API_BASE}/products/${currentProduct.value.id}/stages`, {
      method: 'POST',
      body: JSON.stringify(stageForm)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('阶段添加成功')
      stageDialogVisible.value = false
      viewProduct(currentProduct.value)
    }
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

async function runComparison() {
  if (selectedProducts.value.length < 2) {
    ElMessage.warning('请至少选择2个产品')
    return
  }
  try {
    const res = await authFetch(`${API_BASE}/products/compare`, {
      method: 'POST',
      body: JSON.stringify({ product_ids: selectedProducts.value })
    })
    const data = await res.json()
    comparisonResult.value = data.data
  } catch (e) {
    ElMessage.error('对比失败')
  }
}
</script>

<style scoped>
.carbon-trace {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
