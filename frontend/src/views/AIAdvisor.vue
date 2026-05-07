<template>
  <div class="ai-advisor">
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>🤖 AI碳顾问</span>
          <el-tag :type="aiStatus.available ? 'success' : 'warning'" size="small">
            {{ aiStatus.available ? '在线' : '离线' }}
          </el-tag>
        </div>
      </template>
      <div v-if="!aiStatus.available" class="offline-tip">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            AI顾问当前离线，请配置 LLM 服务后使用
          </template>
          <div class="offline-detail">
            支持平台：
            <el-link href="https://platform.deepseek.com" type="primary" :underline="false">DeepSeek</el-link> ·
            <el-link href="https://dashscope.aliyuncs.com" type="primary" :underline="false">通义千问</el-link> ·
            <el-link href="https://cloud.siliconflow.cn" type="primary" :underline="false">硅基流动</el-link>
          </div>
          <div style="margin-top:8px;font-size:13px;color:#909399;">
            请编辑 <code>D:\ai-carbon-system\backend\.env</code> 配置 API Key 后重启后端
          </div>
        </el-alert>
      </div>
      <div v-else class="model-info">
        <span class="info-label">模型：</span>
        <span class="info-value">{{ aiStatus.model }}</span>
        <span class="info-label" style="margin-left:16px">接口：</span>
        <span class="info-value">{{ aiStatus.base_url }}</span>
      </div>
    </el-card>

    <el-card class="chat-card">
      <div class="messages" ref="messagesEl">
        <div v-if="messages.length === 0" class="empty-tip">
          <el-empty description="开始对话吧！" :image-size="80" />
          <div class="quick-questions">
            <div class="quick-title">💡 试试这些问题：</div>
            <el-tag
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              type="info"
              round
              style="cursor:pointer"
              @click="sendQuick(q)"
            >{{ q }}</el-tag>
          </div>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message-item', msg.role === 'user' ? 'user-msg' : 'ai-msg']"
        >
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="bubble">
            <div class="msg-content" v-html="formatMarkdown(msg.content)"></div>
          </div>
        </div>

        <div v-if="loading" class="message-item ai-msg">
          <div class="avatar">🤖</div>
          <div class="bubble">
            <div class="typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="输入您关于碳排放、碳核算、碳中和政策等问题..."
          :disabled="loading"
          @keydown.ctrl.enter="sendMessage"
          resize="none"
        />
        <el-button type="primary" :loading="loading" :disabled="!inputText.trim()" @click="sendMessage" style="margin-top:8px">
          {{ loading ? '思考中...' : '发送' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_BASE as AUTH_BASE } from '../utils/auth'

const API_BASE = AUTH_BASE + '/ai-advisor'

const messagesEl = ref(null)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const aiStatus = ref({ available: false, model: '', base_url: '' })

const quickQuestions = [
  '企业 Scope 1 排放源有哪些？',
  '如何降低 Scope 2 电力碳排放？',
  ' Scope 3 供应链碳排放如何核算？',
  '碳配额不足时有哪些合规策略？',
  '企业碳中和路径规划建议',
  '碳资产如何进行管理？',
]

onMounted(async () => {
  await checkStatus()
})

async function checkStatus() {
  try {
    const res = await axios.get(`${API_BASE}/status`)
    aiStatus.value = res.data
  } catch (e) {
    aiStatus.value = { available: false, model: '', base_url: '' }
  }
}

function sendQuick(q) {
  inputText.value = q
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  await scrollBottom()

  try {
    const res = await axios.post(`${API_BASE}/chat`, {
      messages: messages.value.map(m => ({ role: m.role, content: m.content }))
    })
    if (res.data.success) {
      messages.value.push({ role: 'assistant', content: res.data.reply })
    } else {
      messages.value.push({ role: 'assistant', content: `⚠️ ${res.data.reply}` })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `❌ 网络错误: ${e.message}` })
  } finally {
    loading.value = false
    await scrollBottom()
  }
}

async function scrollBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

function formatMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>').replace(/$/, '</p>')
}
</script>

<style scoped>
.ai-advisor { display: flex; flex-direction: column; gap: 16px; height: 100%; }

.status-card .card-header { display: flex; align-items: center; justify-content: space-between; }
.status-card .offline-detail { margin-top: 4px; font-size: 13px; }
.status-card .model-info { font-size: 14px; color: #606266; }
.status-card .info-label { color: #909399; }
.status-card .info-value { color: #409eff; }

.chat-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.chat-card :deep(.el-card__body) { display: flex; flex-direction: column; height: 100%; padding: 0; }

.messages { flex: 1; overflow-y: auto; padding: 16px; min-height: 300px; }
.messages .empty-tip { text-align: center; padding: 20px 0; }
.messages .quick-questions { margin-top: 16px; }
.messages .quick-title { font-size: 13px; color: #909399; margin-bottom: 8px; }
.messages .quick-tag { margin: 4px; }

.message-item { display: flex; align-items: flex-start; margin-bottom: 16px; gap: 10px; }
.message-item .avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.message-item.user-msg { flex-direction: row-reverse; }
.message-item.user-msg .avatar { background: #ecf5ff; }
.message-item.ai-msg .avatar { background: #f0f9eb; }
.bubble { max-width: 72%; padding: 10px 14px; border-radius: 12px; line-height: 1.6; font-size: 14px; }
.user-msg .bubble { background: #409eff; color: #fff; border-bottom-right-radius: 2px; }
.ai-msg .bubble { background: #fff; color: #303133; border: 1px solid #e8e8e8; border-bottom-left-radius: 2px; }
.msg-content { word-break: break-word; }
.msg-content :deep(p) { margin: 0 0 4px; }
.msg-content :deep(strong) { color: #409eff; }

.typing { display: flex; gap: 4px; padding: 4px 0; }
.typing .dot { width: 8px; height: 8px; border-radius: 50%; background: #409eff; animation: bounce 1.4s infinite; }
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)} }

.input-area { padding: 12px 16px; border-top: 1px solid #f0f0f0; background: #fafafa; }
.input-area :deep(.el-textarea__inner) { border-radius: 8px; }
</style>
