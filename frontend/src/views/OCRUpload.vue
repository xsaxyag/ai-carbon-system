<template>
  <div class="ocr-upload">
    <h2>OCR发票识别</h2>
    
    <!-- 上传区域 -->
    <el-card class="upload-card">
      <div 
        class="upload-area"
        :class="{ 'drag-over': isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
      >
        <el-icon :size="48"><UploadFilled /></el-icon>
        <p>拖拽图片到此处或点击上传</p>
        <p class="tip">支持 PNG、JPG、BMP、WebP 格式</p>
        <input 
          type="file" 
          ref="fileInput"
          accept=".png,.jpg,.jpeg,.bmp,.webp"
          @change="handleFileSelect"
          style="display:none"
        />
        <el-button type="primary" @click="$refs.fileInput.click()">
          选择图片
        </el-button>
      </div>
    </el-card>
    
    <!-- 识别结果 -->
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="result-header">
          <span>识别结果</span>
          <el-tag :type="result.success ? 'success' : 'danger'">
            {{ result.message }}
          </el-tag>
        </div>
      </template>
      
      <div v-if="result.extracted_data" class="extracted-data">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="发票代码">
            {{ result.extracted_data.fields?.invoice_code || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="发票号码">
            {{ result.extracted_data.fields?.invoice_no || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="金额">
            {{ result.extracted_data.fields?.amount || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="税额">
            {{ result.extracted_data.fields?.tax || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="价税合计">
            {{ result.extracted_data.fields?.total || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开票日期">
            {{ result.extracted_data.fields?.date || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="销售方">
            {{ result.extracted_data.fields?.seller || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="购买方">
            {{ result.extracted_data.fields?.buyer || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="confidence">
          识别置信度: {{ (result.confidence * 100).toFixed(1) }}%
        </div>
        
        <!-- 原始文本 -->
        <div v-if="result.raw_texts" class="raw-texts">
          <h4>识别文本:</h4>
          <ul>
            <li v-for="(text, i) in result.raw_texts" :key="i">
              {{ text.text }} <span class="conf">({{ (text.confidence * 100).toFixed(0) }}%)</span>
            </li>
          </ul>
        </div>
        
        <el-button 
          v-if="result.extracted_data.fields?.amount"
          type="success" 
          @click="createCarbonRecord"
        >
          创建碳记录
        </el-button>
        <el-divider direction="vertical" v-if="result.extracted_data.fields?.amount" />
        <el-button 
          v-if="result.extracted_data.fields?.amount"
          type="primary" 
          plain
          @click="viewReport"
        >
          查看碳报告
        </el-button>
      </div>
    </el-card>
    
    <!-- 历史记录 -->
    <el-card class="history-card">
      <template #header>
        <span>识别历史</span>
      </template>
      <el-table :data="history" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="image_name" label="图片" width="150" />
        <el-table-column prop="message" label="状态" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { API_BASE } from '../utils/auth'

const router = useRouter()

const fileInput = ref(null)
const isDragOver = ref(false)
const isLoading = ref(false)
const result = ref(null)
const history = ref([])

const handleFileSelect = async (e) => {
  const file = e.target.files[0]
  if (file) await uploadFile(file)
}

const handleDrop = async (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file) await uploadFile(file)
}

const uploadFile = async (file) => {
  isLoading.value = true
  result.value = null
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await fetch(`${API_BASE}/ocr/recognize`, {
      method: 'POST',
      body: formData
    })
    result.value = await response.json()
  } catch (e) {
    result.value = {
      success: false,
      message: '上传失败: ' + e.message
    }
  }
  
  isLoading.value = false
}

const createCarbonRecord = async () => {
  const fields = result.value.extracted_data.fields
  const amount = fields.amount || fields.total || 0
  if (!amount) {
    ElMessage.warning('未识别到有效金额')
    return
  }
  try {
    // 将发票金额映射为电力消耗（假设发票为电费）
    // 电价约0.6-0.8元/kWh，这里用0.685估算
    const electricityKwh = Math.round(amount / 0.685)
    const res = await fetch(`${API_BASE}/carbon/records/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: 1,
        record_date: fields.date || new Date().toISOString().slice(0, 7),
        scope: 'scope2',
        emission_source: 'electricity',
        quantity: electricityKwh,
        unit: 'kWh',
        notes: `OCR识别-发票${fields.invoice_no || ''}`
      })
    })
    const data = await res.json()
    ElMessage.success(`碳记录已创建: ${data.co2_emission} kgCO2`)
  } catch (e) {
    ElMessage.error('创建失败: ' + e.message)
  }
}

const viewReport = () => {
  router.push('/report')
}
</script>

<style scoped>
.ocr-upload {
  padding: 20px;
}
h2 {
  margin-bottom: 20px;
  color: #303133;
}
.upload-card {
  margin-bottom: 20px;
}
.upload-area {
  padding: 40px;
  text-align: center;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
}
.upload-area.drag-over {
  border-color: #409eff;
  background: #ecf5ff;
}
.upload-area .tip {
  color: #909399;
  font-size: 12px;
  margin: 8px 0;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.extracted-data {
  margin-top: 16px;
}
.confidence {
  margin: 16px 0;
  color: #409eff;
  font-weight: bold;
}
.raw-texts {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.raw-texts h4 {
  margin: 0 0 8px;
}
.raw-texts ul {
  margin: 0;
  padding-left: 20px;
}
.raw-texts .conf {
  color: #909399;
  font-size: 12px;
}
</style>