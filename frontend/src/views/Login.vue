<template>
  <div class="login-container">
    <!-- 动态背景气泡 -->
    <div class="bg-bubbles">
      <div v-for="i in 10" :key="i" class="bubble" :style="bubbleStyle(i)"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 品牌头部 -->
      <div class="login-header">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <el-icon :size="40"><DataBoard /></el-icon>
          </div>
        </div>
        <h1>AI碳枢算</h1>
        <p class="subtitle">中小微企业碳中和智能管理系统</p>
        <div class="header-tags">
          <el-tag type="info" size="small" effect="plain" round>GB/T 32150 标准</el-tag>
          <el-tag type="success" size="small" effect="plain" round>生态环境部因子库</el-tag>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <!-- 登录 -->
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" @submit.prevent="handleLogin" size="large">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" @keyup.enter="handleLogin" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" style="width:100%;" @click="handleLogin" class="submit-btn">
                <template #default>
                  <span v-if="!loading">登 录</span>
                  <span v-else>登录中...</span>
                </template>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" @submit.prevent="handleRegister" size="large">
            <el-form-item prop="username">
              <el-input v-model="registerForm.username" placeholder="用户名（字母数字下划线）" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item prop="company_name">
              <el-input v-model="registerForm.company_name" placeholder="企业名称" prefix-icon="OfficeBuilding" size="large" />
            </el-form-item>
            <el-form-item prop="industry">
              <el-select v-model="registerForm.industry" placeholder="所属行业（选填）" size="large" style="width:100%" clearable>
                <el-option label="制造业" value="制造业" />
                <el-option label="纺织业" value="纺织业" />
                <el-option label="零售业" value="零售业" />
                <el-option label="科技" value="科技" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" style="width:100%;" @click="handleRegister" class="submit-btn">
                <template #default>
                  <span v-if="!loading">注 册</span>
                  <span v-else>注册中...</span>
                </template>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <el-text type="info" size="small">
          <el-icon><InfoFilled /></el-icon>
          GB/T 32150 碳核算标准 · 生态环境部排放因子
        </el-text>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { API_BASE } from '../utils/auth'
const router = useRouter()

const activeTab = ref('login')
const loading = ref(false)

// 登录表单
const loginFormRef = ref(null)
const loginForm = reactive({ username: '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 注册表单
const registerFormRef = ref(null)
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  company_name: '',
  industry: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名3-50位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母数字下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
}

// 气泡样式生成
function bubbleStyle(i) {
  const size = 40 + Math.random() * 120
  return {
    width: size + 'px',
    height: size + 'px',
    left: Math.random() * 100 + '%',
    animationDuration: (15 + Math.random() * 20) + 's',
    animationDelay: (Math.random() * 10) + 's',
    opacity: 0.1 + Math.random() * 0.2
  }
}

async function handleLogin() {
  const form = loginFormRef.value
  if (!form) return
  await form.validate()
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: loginForm.username, password: loginForm.password })
    })
    const data = await res.json()
    if (data.success || data.access_token) {
      const token = data.access_token || (data.data && data.data.access_token)
      const user = data.user || (data.data && data.data.user)
      localStorage.setItem('token', token)
      if (user) localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error(data.detail || '登录失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const form = registerFormRef.value
  if (!form) return
  await form.validate()
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: registerForm.username,
        password: registerForm.password,
        company_name: registerForm.company_name,
        industry: registerForm.industry || null
      })
    })
    const data = await res.json()
    if (data.success || data.access_token) {
      const token = data.access_token || (data.data && data.data.access_token)
      const user = data.user || (data.data && data.data.user)
      localStorage.setItem('token', token)
      if (user) localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('注册成功')
      router.push('/')
    } else {
      ElMessage.error(data.detail || '注册失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 30%, #16213e 60%, #0f3460 100%);
  position: relative;
  overflow: hidden;
}

/* === 动态背景气泡 === */
.bg-bubbles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
.bubble {
  position: absolute;
  bottom: -200px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
  animation: floatUp linear infinite;
}
@keyframes floatUp {
  0% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: 0.15; }
  90% { opacity: 0.15; }
  100% { transform: translateY(-110vh) rotate(720deg); opacity: 0; }
}

/* === 登录卡片（毛玻璃效果） === */
.login-card {
  width: 440px;
  padding: 48px 40px 32px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  z-index: 1;
  animation: cardFadeIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
}
@keyframes cardFadeIn {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* === 品牌头部 === */
.login-header { text-align: center; margin-bottom: 28px; }
.logo-wrapper { margin-bottom: 16px; }
.logo-icon {
  width: 72px; height: 72px; margin: 0 auto;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
  animation: logoFloat 3s ease-in-out infinite;
}
@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.login-header h1 {
  margin: 16px 0 6px;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #303133 0%, #409eff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.subtitle { color: #909399; font-size: 14px; margin: 0; }
.header-tags { margin-top: 12px; display: flex; justify-content: center; gap: 8px; }

/* === Tabs === */
.login-tabs { margin-top: 8px; }
.login-tabs :deep(.el-tabs__nav) { width: 100%; }
.login-tabs :deep(.el-tabs__item) {
  width: 50%; text-align: center; font-size: 15px; font-weight: 600;
  transition: all 0.3s;
}
.login-tabs :deep(.el-tabs__item.is-active) { color: #409eff; }
.login-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 3px; border-radius: 2px;
}

/* === 表单 === */
.login-tabs :deep(.el-input__wrapper) {
  border-radius: 10px;
  transition: all 0.3s;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}
.login-tabs :deep(.el-input__wrapper:hover) { box-shadow: 0 0 0 1px #409eff inset; }
.login-tabs :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset, 0 4px 12px rgba(64, 158, 255, 0.15);
}

/* === 提交按钮（微光动画） === */
.submit-btn {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #409eff 0%, #3a7bd5 50%, #667eea 100%);
  border: none; border-radius: 10px;
  font-size: 16px; font-weight: 600; letter-spacing: 4px;
  height: 44px;
  transition: all 0.3s;
}
.submit-btn::before {
  content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}
.submit-btn:hover::before { left: 100%; }
.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.35);
}
.submit-btn:active { transform: translateY(0); }

/* === 页脚 === */
.login-footer {
  text-align: center; margin-top: 20px; padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex; align-items: center; justify-content: center; gap: 4px;
}
.login-footer .el-icon { font-size: 12px; }

/* === 响应式 === */
@media (max-width: 480px) {
  .login-card { width: 92vw; padding: 36px 24px 24px; }
  .login-header h1 { font-size: 24px; }
}
</style>
