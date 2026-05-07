<template>
  <div class="carbon-asset">
    <h2>碳资产管理</h2>
    
    <!-- 资产概览卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.total_quota.toFixed(1) }}</div>
              <div class="stat-label">配额总量 (吨)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.total_emission.toFixed(1) }}</div>
              <div class="stat-label">排放总量 (吨)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{background: summary.quota_balance >= 0 ? '#67c23a' : '#f56c6c'}">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.quota_balance.toFixed(1) }}</div>
              <div class="stat-label">配额余额 (吨)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ (summary.asset_value / 10000).toFixed(2) }}万</div>
              <div class="stat-label">资产价值</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 风险提示 -->
    <el-alert
      v-if="summary.risk_level === 'deficit'"
      title="配额缺口预警"
      type="error"
      description="当前配额不足以覆盖排放量，建议购买配额或实施降碳措施"
      show-icon
      style="margin-bottom: 20px;"
    />
    <el-alert
      v-else-if="summary.risk_level === 'surplus'"
      title="配额盈余提示"
      type="success"
      description="当前配额有盈余，可考虑出售获利或用于抵消未来排放"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <el-tabs v-model="activeTab">
      <!-- 配额管理 -->
      <el-tab-pane label="配额管理" name="quota">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>碳配额台账</span>
              <el-button type="primary" @click="showAddQuotaDialog">新增配额</el-button>
            </div>
          </template>
          
          <el-table :data="quotas" stripe>
            <el-table-column prop="year" label="年度" width="100" />
            <el-table-column prop="quota_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.quota_type === 'free' ? 'success' : 'warning'">
                  {{ row.quota_type === 'free' ? '免费配额' : '拍卖配额' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quota_amount" label="配额量(吨)" width="120">
              <template #default="{ row }">{{ row.quota_amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="used_amount" label="已使用(吨)" width="120">
              <template #default="{ row }">{{ row.used_amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="remaining_amount" label="剩余(吨)" width="120">
              <template #default="{ row }">
                <span :style="{color: row.remaining_amount < 0 ? '#f56c6c' : '#67c23a'}">
                  {{ row.remaining_amount.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '有效' : row.status === 'expired' ? '已过期' : '已履约' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" />
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <!-- 碳交易 -->
      <el-tab-pane label="碳交易" name="trade">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>交易记录</span>
              <el-button type="primary" @click="showAddTradeDialog">新建交易</el-button>
            </div>
          </template>
          
          <!-- 实时碳价 -->
          <el-alert type="info" style="margin-bottom: 15px;">
            <template #title>
              <span>实时碳价：{{ marketPrice.price }} 元/吨</span>
              <span :style="{color: marketPrice.change >= 0 ? '#67c23a' : '#f56c6c', marginLeft: '20px'}">
                {{ marketPrice.change >= 0 ? '+' : '' }}{{ marketPrice.change }} ({{ marketPrice.change_percent }}%)
              </span>
            </template>
          </el-alert>
          
          <el-table :data="trades" stripe>
            <el-table-column prop="trade_date" label="交易日期" width="120" />
            <el-table-column prop="trade_type" label="交易类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.trade_type === 'buy' ? 'danger' : 'success'">
                  {{ row.trade_type === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="数量(吨)" width="100" />
            <el-table-column prop="price" label="单价(元/吨)" width="120" />
            <el-table-column prop="total_price" label="总价(元)" width="120">
              <template #default="{ row }">¥{{ row.total_price.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="market" label="交易市场" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                  {{ row.status === 'completed' ? '已成交' : '待成交' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 新增配额对话框 -->
    <el-dialog v-model="quotaDialogVisible" title="新增碳配额" width="500px">
      <el-form :model="quotaForm" label-width="100px">
        <el-form-item label="年度">
          <el-date-picker v-model="quotaForm.year" type="year" placeholder="选择年度" value-format="YYYY" />
        </el-form-item>
        <el-form-item label="配额量">
          <el-input-number v-model="quotaForm.quota_amount" :min="0" :precision="2" /> 吨
        </el-form-item>
        <el-form-item label="配额类型">
          <el-radio-group v-model="quotaForm.quota_type">
            <el-radio label="free">免费配额</el-radio>
            <el-radio label="auction">拍卖配额</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quotaDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuota">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 新增交易对话框 -->
    <el-dialog v-model="tradeDialogVisible" title="新建碳交易" width="500px">
      <el-form :model="tradeForm" label-width="100px">
        <el-form-item label="交易类型">
          <el-radio-group v-model="tradeForm.trade_type">
            <el-radio label="buy">买入</el-radio>
            <el-radio label="sell">卖出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="tradeForm.amount" :min="0" :precision="2" /> 吨
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="tradeForm.price" :min="0" :precision="2" /> 元/吨
        </el-form-item>
        <el-form-item label="交易日期">
          <el-date-picker v-model="tradeForm.trade_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTrade">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Coin, TrendCharts, DataAnalysis, Money } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'

const activeTab = ref('quota')
const companyId = ref(1)

const summary = reactive({
  total_quota: 0,
  total_emission: 0,
  quota_balance: 0,
  asset_value: 0,
  risk_level: 'balanced'
})

const quotas = ref([])
const trades = ref([])
const marketPrice = ref({
  price: 60.5,
  change: 0.3,
  change_percent: 0.5
})

const quotaDialogVisible = ref(false)
const tradeDialogVisible = ref(false)

const quotaForm = reactive({
  year: new Date().getFullYear(),
  quota_amount: 1000,
  quota_type: 'free'
})

const tradeForm = reactive({
  trade_type: 'buy',
  amount: 100,
  price: 60,
  trade_date: new Date().toISOString().split('T')[0]
})

onMounted(() => {
  loadSummary()
  loadQuotas()
  loadTrades()
  loadMarketPrice()
})

async function loadSummary() {
  try {
    const year = new Date().getFullYear()
    const res = await fetch(`${API_BASE}/carbon-asset/summary/${companyId.value}/${year}`)
    const data = await res.json()
    Object.assign(summary, data)
  } catch (e) {
    console.error('加载资产汇总失败', e)
  }
}

async function loadQuotas() {
  try {
    const res = await fetch(`${API_BASE}/carbon-asset/quota/${companyId.value}`)
    quotas.value = await res.json()
  } catch (e) {
    console.error('加载配额失败', e)
  }
}

async function loadTrades() {
  try {
    const res = await fetch(`${API_BASE}/carbon-asset/trades/${companyId.value}`)
    trades.value = await res.json()
  } catch (e) {
    console.error('加载交易记录失败', e)
  }
}

async function loadMarketPrice() {
  try {
    const res = await fetch(`${API_BASE}/carbon-asset/market-price`)
    marketPrice.value = await res.json()
  } catch (e) {
    console.error('加载碳价失败', e)
  }
}

function showAddQuotaDialog() {
  quotaDialogVisible.value = true
}

function showAddTradeDialog() {
  tradeDialogVisible.value = true
}

async function submitQuota() {
  try {
    const res = await fetch(`${API_BASE}/carbon-asset/quota`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId.value,
        ...quotaForm
      })
    })
    if (res.ok) {
      ElMessage.success('配额创建成功')
      quotaDialogVisible.value = false
      loadQuotas()
      loadSummary()
    }
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

async function submitTrade() {
  try {
    const res = await fetch(`${API_BASE}/carbon-asset/trade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId.value,
        ...tradeForm
      })
    })
    if (res.ok) {
      ElMessage.success('交易创建成功')
      tradeDialogVisible.value = false
      loadTrades()
    }
  } catch (e) {
    ElMessage.error('创建失败')
  }
}
</script>

<style scoped>
.carbon-asset {
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
