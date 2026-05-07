<template>
  <div class="backup-page">
    <h2>数据备份管理</h2>
    
    <!-- 数据库统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><Database /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dbStats.table_count || 0 }}</div>
              <div class="stat-label">数据表</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dbStats.total_records || 0 }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ backups.length }}</div>
              <div class="stat-label">备份数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ latestBackupTime }}</div>
              <div class="stat-label">最近备份</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <!-- 备份管理 -->
      <el-tab-pane label="备份列表" name="backups">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>备份文件列表</span>
              <div>
                <el-button type="primary" @click="createBackup">
                  <el-icon><Plus /></el-icon>
                  创建备份
                </el-button>
                <el-button @click="cleanupBackups" :disabled="backups.length <= 10">
                  清理旧备份
                </el-button>
              </div>
            </div>
          </template>

          <el-table :data="backups" stripe v-loading="loading">
            <el-table-column prop="filename" label="文件名" min-width="250" />
            <el-table-column prop="size_mb" label="大小(MB)" width="120">
              <template #default="{ row }">{{ (row.size / 1024 / 1024).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="note" label="备注" width="150">
              <template #default="{ row }">{{ row.note || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="success" size="small" @click="restoreBackup(row)">恢复</el-button>
                <el-button type="info" size="small" @click="downloadBackup(row)">下载</el-button>
                <el-button type="danger" size="small" @click="deleteBackup(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 数据导出导入 -->
      <el-tab-pane label="数据导入导出" name="export">
        <el-card>
          <template #header>
            <span>JSON数据导出/导入</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover" style="text-align: center; padding: 30px;">
                <el-icon :size="48" style="color: #409eff;"><Download /></el-icon>
                <h3 style="margin: 15px 0;">导出全部数据</h3>
                <p style="color: #909399; margin-bottom: 20px;">将数据库全部数据导出为JSON文件</p>
                <el-button type="primary" @click="exportData" :loading="exporting">
                  <el-icon><Download /></el-icon>
                  导出JSON
                </el-button>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover" style="text-align: center; padding: 30px;">
                <el-icon :size="48" style="color: #67c23a;"><Upload /></el-icon>
                <h3 style="margin: 15px 0;">导入数据</h3>
                <p style="color: #909399; margin-bottom: 20px;">从JSON文件导入数据到数据库</p>
                <el-upload
                  ref="uploadRef"
                  :auto-upload="false"
                  :show-file-list="false"
                  accept=".json"
                  :on-change="handleFileSelect"
                >
                  <el-button type="success">
                    <el-icon><Upload /></el-icon>
                    选择JSON文件
                  </el-button>
                </el-upload>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <!-- 数据库详情 -->
      <el-tab-pane label="数据库详情" name="details">
        <el-card>
          <template #header>
            <span>各表记录统计</span>
          </template>

          <el-table :data="tableDetails" stripe>
            <el-table-column prop="table" label="表名" min-width="200" />
            <el-table-column prop="count" label="记录数" width="120">
              <template #default="{ row }">
                <el-tag :type="row.count > 0 ? 'success' : 'info'">{{ row.count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建备份备注对话框 -->
    <el-dialog v-model="noteDialogVisible" title="创建备份" width="400px">
      <el-form label-width="80px">
        <el-form-item label="备注">
          <el-input v-model="backupNote" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doCreateBackup" :loading="creating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authFetch, API_BASE as AUTH_BASE } from '../utils/auth'
import { Document, Folder, Timer, Plus, Download, Upload } from '@element-plus/icons-vue'
import { Collection as Database } from '@element-plus/icons-vue'

const API_BASE = AUTH_BASE + '/backup'

const activeTab = ref('backups')
const loading = ref(false)
const creating = ref(false)
const exporting = ref(false)
const backups = ref([])
const dbStats = ref({})
const noteDialogVisible = ref(false)
const backupNote = ref('')
const uploadRef = ref(null)

const tableDescriptions = {
  companies: '企业信息',
  carbon_records: '碳排放记录',
  carbon_measures: '降碳措施库',
  emission_factors: '排放因子',
  industry_benchmarks: '行业基准',
  alert_history: '预警历史',
  alert_thresholds: '预警阈值',
  carbon_quota: '碳配额',
  carbon_trade: '碳交易记录',
  ocr_records: 'OCR识别记录',
  product_footprints: '产品碳足迹',
  footprint_stages: '生命周期阶段',
  users: '用户'
}

const latestBackupTime = computed(() => {
  if (backups.value.length === 0) return '无'
  const latest = backups.value[0]
  return formatTime(latest.created_at)
})

const tableDetails = computed(() => {
  const details = dbStats.value.tables || {}
  return Object.entries(details).map(([table, count]) => ({
    table,
    count,
    description: tableDescriptions[table] || ''
  }))
})

onMounted(() => {
  loadBackups()
  loadStats()
})

async function loadBackups() {
  loading.value = true
  try {
    const res = await authFetch(`${API_BASE}/list`)
    const data = await res.json()
    backups.value = data.data || []
  } catch (e) {
    console.error('加载备份列表失败', e)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res = await authFetch(`${API_BASE}/stats`)
    const data = await res.json()
    dbStats.value = data.data || {}
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

function formatTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function createBackup() {
  backupNote.value = ''
  noteDialogVisible.value = true
}

async function doCreateBackup() {
  creating.value = true
  try {
    const res = await authFetch(`${API_BASE}/create?note=${encodeURIComponent(backupNote.value)}`, {
      method: 'POST'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`备份创建成功：${data.data.filename}`)
      noteDialogVisible.value = false
      loadBackups()
    }
  } catch (e) {
    ElMessage.error('创建备份失败')
  } finally {
    creating.value = false
  }
}

async function restoreBackup(backup) {
  try {
    await ElMessageBox.confirm(
      `确定从备份"${backup.filename}"恢复？当前数据将被覆盖！`,
      '警告',
      { type: 'warning', confirmButtonText: '确定恢复', cancelButtonText: '取消' }
    )
    const res = await authFetch(`${API_BASE}/restore`, {
      method: 'POST',
      body: JSON.stringify({ filename: backup.filename })
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('恢复成功，请刷新页面')
      loadStats()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('恢复失败')
  }
}

async function deleteBackup(backup) {
  try {
    await ElMessageBox.confirm(`确定删除备份"${backup.filename}"？`, '提示', { type: 'warning' })
    const res = await authFetch(`${API_BASE}/${encodeURIComponent(backup.filename)}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadBackups()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function downloadBackup(backup) {
  // 备份文件在backend/backups目录，需要通过后端下载
  ElMessage.info('请从服务器 backups 目录下载文件：' + backup.filename)
}

async function cleanupBackups() {
  try {
    await ElMessageBox.confirm('保留最近10个备份，删除其他旧备份？', '提示', { type: 'warning' })
    const res = await authFetch(`${API_BASE}/cleanup`, {
      method: 'POST',
      body: JSON.stringify({ keep_count: 10 })
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`清理完成，删除了 ${data.data.deleted} 个旧备份`)
      loadBackups()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清理失败')
  }
}

async function exportData() {
  exporting.value = true
  try {
    const res = await authFetch(`${API_BASE}/export`)
    const data = await res.json()
    // 创建下载
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `carbon-data-export-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

async function handleFileSelect(file) {
  try {
    const text = await file.raw.text()
    const data = JSON.parse(text)
    
    await ElMessageBox.confirm('确定导入数据？当前数据将被覆盖！', '警告', { type: 'warning' })
    
    const res = await authFetch(`${API_BASE}/import`, {
      method: 'POST',
      body: JSON.stringify({ data })
    })
    const result = await res.json()
    if (result.success) {
      ElMessage.success(`导入成功：${result.data.imported_tables} 张表`)
      loadStats()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('导入失败，请检查文件格式')
    }
  }
}
</script>

<style scoped>
.backup-page {
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
