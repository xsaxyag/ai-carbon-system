<template>
  <div class="ai-carbon-advisor">
    <!-- Header -->
    <div class="advisor-header">
      <h2>🤖 AI智能碳顾问</h2>
      <p class="subtitle">一句话完成碳管理任务</p>
    </div>

    <!-- Quick Commands Panel -->
    <div class="quick-commands">
      <h3>快捷指令</h3>
      <div class="command-grid">
        <el-button
          v-for="cmd in quickCommands"
          :key="cmd.id"
          :type="cmd.type"
          @click="executeQuickCommand(cmd)"
          class="command-btn"
        >
          <span class="cmd-icon">{{ cmd.icon }}</span>
          <span class="cmd-text">{{ cmd.name }}</span>
        </el-button>
      </div>
    </div>

    <!-- Chat Interface -->
    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message', msg.role]"
        >
          <div class="message-content">
            <div class="role-label">{{ msg.role === 'user' ? '👤 用户' : '🤖 AI顾问' }}</div>
            <div class="text" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>
        <div v-if="loading" class="message assistant loading">
          <div class="message-content">
            <div class="role-label">🤖 AI顾问</div>
            <div class="text">思考中...</div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <el-input
          v-model="userInput"
          placeholder="输入您的问题或指令，如：帮我建模电动汽车电池的LCA"
          @keyup.enter="sendMessage"
          :disabled="loading"
          class="chat-input"
        >
          <template #append>
            <el-button @click="sendMessage" :loading="loading" type="primary">
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- One Command Dialog -->
    <el-dialog v-model="showCommandDialog" :title="currentCommand?.name" width="600px">
      <el-form :model="commandForm" label-width="120px">
        <el-form-item
          v-for="field in currentCommand?.fields || []"
          :key="field.key"
          :label="field.label"
        >
          <el-input
            v-if="field.type === 'text'"
            v-model="commandForm[field.key]"
            :placeholder="field.placeholder"
          />
          <el-select
            v-else-if="field.type === 'select'"
            v-model="commandForm[field.key]"
            :placeholder="field.placeholder"
          >
            <el-option
              v-for="opt in field.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCommandDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCommand" :loading="loading">
          执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = '/api/v1/ai-advisor-v2'

const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是AI智能碳顾问。我可以帮助您：\n\n• 📊 **LCA建模** - 一句话创建产品碳足迹模型\n• 📑 **碳报告生成** - 自动生成ISO标准报告\n• 📈 **排放分析** - 深度分析企业碳排放\n• 💡 **减排建议** - 智能推荐减排方案\n• 💰 **碳资产查询** - 管理碳信用资产\n\n请输入您的问题或点击上方快捷指令开始！'
  }
])
const userInput = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const showCommandDialog = ref(false)
const currentCommand = ref(null)
const commandForm = ref({})

const quickCommands = ref([
  { id: 'lca', name: 'LCA建模', icon: '📊', type: 'primary', fields: [
    { key: 'product_name', label: '产品名称', type: 'text', placeholder: '如：电动汽车电池' },
    { key: 'functional_unit', label: '功能单位', type: 'text', placeholder: '如：1组电池包' }
  ]},
  { id: 'report', name: '生成报告', icon: '📑', type: 'success', fields: [
    { key: 'report_type', label: '报告类型', type: 'select', options: [
      { label: 'ISO 14064-1 组织碳报告', value: 'iso14064' },
      { label: 'ISO 14067 产品碳足迹报告', value: 'iso14067' }
    ]},
    { key: 'period', label: '报告周期', type: 'text', placeholder: '如：2025年度' }
  ]},
  { id: 'analysis', name: '排放分析', icon: '📈', type: 'warning', fields: [
    { key: 'company_id', label: '企业ID', type: 'text', placeholder: '输入企业ID' }
  ]},
  { id: 'reduction', name: '减排建议', icon: '💡', type: 'info', fields: [
    { key: 'target', label: '减排目标', type: 'text', placeholder: '如：降低20%碳排放' }
  ]},
  { id: 'asset', name: '碳资产', icon: '💰', type: 'default', fields: []}
])

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return

  const query = userInput.value.trim()
  messages.value.push({ role: 'user', content: query })
  userInput.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await axios.post(`${API_BASE}/chat`, {
      message: query,
      context: { company_id: localStorage.getItem('companyId') }
    })

    messages.value.push({
      role: 'assistant',
      content: res.data.reply || '抱歉，我无法理解您的问题。'
    })
  } catch (error) {
    ElMessage.error('请求失败: ' + (error.response?.data?.detail || error.message))
    messages.value.push({
      role: 'assistant',
      content: '抱歉，服务暂时不可用，请稍后重试。'
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const executeQuickCommand = (cmd) => {
  currentCommand.value = cmd
  commandForm.value = {}
  if (cmd.fields && cmd.fields.length > 0) {
    showCommandDialog.value = true
  } else {
    submitCommand()
  }
}

const submitCommand = async () => {
  showCommandDialog.value = false
  loading.value = true

  const cmd = currentCommand.value
  let query = ''

  switch (cmd.id) {
    case 'lca':
      query = `帮我建模${commandForm.value.product_name || '产品'}的LCA`
      break
    case 'report':
      query = `生成${commandForm.value.period || '本年度'}的${commandForm.value.report_type === 'iso14067' ? '产品碳足迹' : '组织碳'}报告`
      break
    case 'analysis':
      query = `分析企业${commandForm.value.company_id || ''}的碳排放情况`
      break
    case 'reduction':
      query = `如何实现${commandForm.value.target || '降低碳排放'}`
      break
    case 'asset':
      query = '查询我的碳资产信息'
      break
  }

  messages.value.push({ role: 'user', content: query })
  await scrollToBottom()

  try {
    const res = await axios.post(`${API_BASE}/one-command`, {
      command: cmd.id,
      params: commandForm.value
    })

    messages.value.push({
      role: 'assistant',
      content: res.data.result || res.data.message || '执行成功'
    })
  } catch (error) {
    ElMessage.error('执行失败: ' + (error.response?.data?.detail || error.message))
    messages.value.push({
      role: 'assistant',
      content: '抱歉，指令执行失败，请稍后重试。'
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.ai-carbon-advisor {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

.advisor-header {
  text-align: center;
  margin-bottom: 20px;
  color: white;
}

.advisor-header h2 {
  margin: 0;
  font-size: 24px;
}

.subtitle {
  margin: 8px 0 0;
  opacity: 0.9;
}

.quick-commands {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.quick-commands h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #333;
}

.command-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.command-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  height: auto;
}

.cmd-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.cmd-text {
  font-size: 12px;
}

.chat-container {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
}

.message-content {
  display: inline-block;
  max-width: 70%;
  text-align: left;
}

.message.user .message-content {
  background: #409eff;
  color: white;
  border-radius: 12px 12px 0 12px;
  padding: 12px 16px;
}

.message.assistant .message-content {
  background: #f5f7fa;
  color: #333;
  border-radius: 12px 12px 12px 0;
  padding: 12px 16px;
}

.role-label {
  font-size: 12px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.text {
  line-height: 1.6;
  word-break: break-word;
}

.input-area {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.chat-input {
  width: 100%;
}

.loading .text {
  color: #909399;
}
</style>
