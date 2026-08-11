<template>
  <div class="landing-page">
    <!-- 动态粒子背景 -->
    <div class="particles-bg" ref="particlesRef"></div>
    
    <!-- 导航栏 -->
    <nav class="landing-nav">
      <div class="nav-brand">
        <el-icon :size="32" class="brand-icon"><DataBoard /></el-icon>
        <span class="brand-text">AI碳枢算</span>
      </div>
      <div class="nav-actions">
        <el-button type="primary" size="large" @click="goToRegister" class="nav-btn">
          立即注册
        </el-button>
        <el-button size="large" @click="goToLogin" class="nav-btn secondary">
          登录
        </el-button>
      </div>
    </nav>

    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><TrendCharts /></el-icon>
          中小微企业碳中和首选方案
        </div>
        <h1 class="hero-title">
          <span class="gradient-text">AI驱动</span>的碳管理
          <br />让减碳变得<span class="highlight">简单可及</span>
        </h1>
        <p class="hero-subtitle">
          基于 GB/T 32150 标准 · 生态环境部排放因子库 · AI智能分析
          <br />一站式碳核算、减排优化、碳资产管理平台
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">500+</div>
            <div class="stat-label">企业用户</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10万+</div>
            <div class="stat-label">吨碳减排</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">98%</div>
            <div class="stat-label">核算准确率</div>
          </div>
        </div>
        <div class="hero-cta">
          <el-button type="primary" size="large" @click="goToRegister" class="cta-btn primary">
            <el-icon><User /></el-icon>
            免费注册使用
          </el-button>
          <el-button size="large" @click="scrollToFeatures" class="cta-btn secondary">
            了解更多
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </el-button>
        </div>
      </div>
      
      <!-- 3D预览卡片 -->
      <div class="hero-visual">
        <div class="visual-card main">
          <div class="card-header">
            <div class="card-dots">
              <span></span><span></span><span></span>
            </div>
            <span class="card-title">碳排放实时监测</span>
          </div>
          <div class="chart-preview">
            <div class="chart-bar" v-for="(h, i) in chartBars" :key="i" :style="{ height: h + '%' }"></div>
          </div>
          <div class="metric-row">
            <div class="metric">
              <span class="metric-value">2,847</span>
              <span class="metric-unit">tCO₂</span>
            </div>
            <div class="metric-trend down">
              <el-icon><ArrowDown /></el-icon>
              12.5%
            </div>
          </div>
        </div>
        
        <div class="visual-card floating" style="--delay: 0.2s">
          <div class="ai-badge">
            <el-icon><Cpu /></el-icon>
            AI 分析中
          </div>
          <div class="ai-content">
            <div class="ai-line"></div>
            <div class="ai-line short"></div>
            <div class="ai-dots">
              <span v-for="i in 3" :key="i" :style="{ animationDelay: i * 0.2 + 's' }"></span>
            </div>
          </div>
        </div>
        
        <div class="visual-card floating" style="--delay: 0.4s; --offset-x: -30px; --offset-y: 60px">
          <div class="scope-badge scope-1">Scope 1</div>
          <div class="scope-value">856 t</div>
          <div class="scope-bar">
            <div class="scope-fill" style="width: 35%"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能特性 -->
    <section class="features-section" id="features">
      <div class="section-header">
        <span class="section-tag">核心功能</span>
        <h2 class="section-title">全方位碳管理解决方案</h2>
        <p class="section-desc">从碳核算到减排优化，从数据可视化到碳资产管理，一站式满足企业碳中和需求</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card" v-for="(feature, index) in features" :key="index" :class="{ 'large': index === 0 }">
          <div class="feature-icon" :style="{ background: feature.gradient }">
            <el-icon :size="28"><component :is="feature.icon" /></el-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
          <div class="feature-tags">
            <el-tag v-for="tag in feature.tags" :key="tag" size="small" effect="plain" :type="tag.type">
              {{ tag.label }}
            </el-tag>
          </div>
        </div>
      </div>
    </section>

    <!-- 3D可视化展示 -->
    <section class="showcase-section">
      <div class="showcase-content">
        <div class="showcase-text">
          <span class="section-tag">3D可视化</span>
          <h2 class="section-title">园区碳排放一目了然</h2>
          <p class="section-desc">
            上传园区平面图，一键生成3D模型。建筑高度代表碳排放强度，
            颜色区分排放类型，让碳数据变得直观可见。
          </p>
          <ul class="showcase-list">
            <li v-for="item in showcaseItems" :key="item">
              <el-icon class="check-icon"><Check /></el-icon>
              {{ item }}
            </li>
          </ul>
          <el-button type="primary" size="large" @click="goToRegister" class="cta-btn">
            立即体验
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="showcase-visual">
          <div class="mockup-3d">
            <div class="building b1"></div>
            <div class="building b2"></div>
            <div class="building b3"></div>
            <div class="building b4"></div>
            <div class="ground"></div>
            <div class="particles">
              <span v-for="i in 8" :key="i" :style="{ 
                left: Math.random() * 100 + '%', 
                animationDelay: Math.random() * 3 + 's',
                animationDuration: (2 + Math.random() * 2) + 's'
              }"></span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI顾问 -->
    <section class="ai-section">
      <div class="ai-content-wrapper">
        <div class="ai-visual">
          <div class="ai-avatar">
            <el-icon :size="48"><ChatDotRound /></el-icon>
            <div class="ai-ring"></div>
            <div class="ai-ring" style="animation-delay: 0.5s"></div>
          </div>
        </div>
        <div class="ai-text">
          <span class="section-tag">AI碳顾问</span>
          <h2 class="section-title">7×24小时智能问答</h2>
          <p class="section-desc">
            基于 GLM-5.1 大模型，专业解答碳排放核算、减排策略、碳交易等各类问题。
            无需专业知识，也能轻松上手碳管理。
          </p>
          <div class="ai-examples">
            <div class="example-bubble" v-for="(ex, i) in aiExamples" :key="i" :style="{ animationDelay: i * 0.3 + 's' }">
              "{{ ex }}"
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">开启您的碳中和之旅</h2>
        <p class="cta-desc">免费注册，即刻体验 AI碳枢算 的强大功能</p>
        <div class="cta-buttons">
          <el-button type="primary" size="large" @click="goToRegister" class="cta-btn large">
            <el-icon><User /></el-icon>
            免费注册
          </el-button>
          <el-button size="large" @click="goToLogin" class="cta-btn secondary large">
            已有账号？立即登录
          </el-button>
        </div>
        <div class="trust-badges">
          <div class="badge">
            <el-icon><Lock /></el-icon>
            数据安全加密
          </div>
          <div class="badge">
            <el-icon><CircleCheck /></el-icon>
            国标合规
          </div>
          <div class="badge">
            <el-icon><Timer /></el-icon>
            7×24小时服务
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <el-icon :size="24"><DataBoard /></el-icon>
          <span>AI碳枢算</span>
        </div>
        <div class="footer-links">
          <a href="#features">功能介绍</a>
          <a @click="goToLogin">登录</a>
          <a @click="goToRegister">注册</a>
        </div>
        <div class="footer-copy">
          © 2024 AI碳枢算 · 基于 GB/T 32150 标准
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  DataBoard, TrendCharts, User, ArrowDown, ArrowRight,
  Cpu, Check, ChatDotRound, Lock, CircleCheck, Timer
} from '@element-plus/icons-vue'

const router = useRouter()
const particlesRef = ref(null)

// 动态图表数据
const chartBars = ref([65, 45, 80, 55, 70, 40, 85, 60, 75, 50, 90, 55])

// 功能特性
const features = [
  {
    icon: 'TrendCharts',
    title: '智能碳核算',
    desc: '基于 GB/T 32150 标准，自动计算 Scope 1/2/3 碳排放，支持多行业模板快速导入',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    tags: [{ label: '国标合规', type: 'success' }, { label: '自动化', type: 'primary' }]
  },
  {
    icon: 'DataAnalysis',
    title: '3D可视化',
    desc: '园区地图一键3D化，建筑高度映射排放强度，直观展示碳热点',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    tags: [{ label: 'Three.js', type: 'warning' }, { label: '实时渲染', type: 'info' }]
  },
  {
    icon: 'ChatDotRound',
    title: 'AI碳顾问',
    desc: '大模型驱动的智能问答，解答碳核算、减排策略、政策解读等各类问题',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    tags: [{ label: 'GLM-5.1', type: 'danger' }, { label: '7×24h', type: 'success' }]
  },
  {
    icon: 'FirstAidKit',
    title: '减排优化',
    desc: 'AI分析减排潜力，生成个性化优化方案，预估投资回报周期',
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    tags: [{ label: '智能推荐', type: 'primary' }, { label: 'ROI分析', type: 'warning' }]
  },
  {
    icon: 'Money',
    title: '碳资产管理',
    desc: 'CCER/VCS/GS/I-REC 碳资产一站式管理，交易记录、健康监控',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    tags: [{ label: '多标准', type: 'info' }, { label: '资产追踪', type: 'success' }]
  },
  {
    icon: 'Document',
    title: 'ISO报告',
    desc: '一键生成 ISO 14064-1/14067 标准报告，满足审计与披露需求',
    gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    tags: [{ label: 'ISO标准', type: 'danger' }, { label: '自动导出', type: 'primary' }]
  }
]

// 3D展示特性
const showcaseItems = [
  '上传园区平面图，AI自动识别建筑轮廓',
  '建筑高度映射碳排放强度，直观定位高排放源',
  '支持热力图、高度、颜色三种可视化模式',
  '日夜模式切换，粒子特效增强视觉体验'
]

// AI示例
const aiExamples = [
  '如何计算我们工厂的Scope 2排放？',
  '有哪些适合制造业的减排措施？',
  'CCER和VCS有什么区别？'
]

// 粒子动画
let particleInterval
onMounted(() => {
  if (!particlesRef.value) return
  
  const createParticle = () => {
    const particle = document.createElement('div')
    particle.className = 'particle'
    particle.style.left = Math.random() * 100 + '%'
    particle.style.animationDuration = (15 + Math.random() * 10) + 's'
    particle.style.animationDelay = Math.random() * 5 + 's'
    particle.style.opacity = 0.1 + Math.random() * 0.3
    particlesRef.value.appendChild(particle)
    
    setTimeout(() => particle.remove(), 25000)
  }
  
  // 初始创建一批粒子
  for (let i = 0; i < 30; i++) {
    setTimeout(createParticle, i * 200)
  }
  
  // 持续创建
  particleInterval = setInterval(createParticle, 800)
})

onUnmounted(() => {
  clearInterval(particleInterval)
})

// 导航
const goToRegister = () => router.push({ path: '/login', query: { tab: 'register' } })
const goToLogin = () => router.push('/login')
const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3e 50%, #0f0f2d 100%);
  color: #fff;
  overflow-x: hidden;
}

/* 粒子背景 */
.particles-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(100, 200, 255, 0.6);
  border-radius: 50%;
  animation: float-up linear infinite;
  box-shadow: 0 0 10px rgba(100, 200, 255, 0.5);
}

@keyframes float-up {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 0.5;
  }
  100% {
    transform: translateY(-100px) scale(1);
    opacity: 0;
  }
}

/* 导航栏 */
.landing-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 48px;
  background: rgba(10, 10, 26, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  color: #00d4aa;
}

.brand-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 12px 24px;
  font-weight: 500;
}

.nav-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* 英雄区域 */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 120px 80px 80px;
  gap: 60px;
}

.hero-content {
  flex: 1;
  max-width: 600px;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 212, 170, 0.1);
  border: 1px solid rgba(0, 212, 170, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #00d4aa;
  margin-bottom: 24px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 24px;
}

.gradient-text {
  background: linear-gradient(135deg, #00d4aa 0%, #00a8ff 50%, #667eea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.highlight {
  color: #00d4aa;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 8px;
  background: linear-gradient(90deg, #00d4aa, transparent);
  opacity: 0.3;
  border-radius: 4px;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.8;
  margin-bottom: 40px;
}

.hero-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4aa, #00a8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.hero-cta {
  display: flex;
  gap: 16px;
}

.cta-btn {
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cta-btn.primary {
  background: linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%);
  border: none;
}

.cta-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.arrow-icon {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

/* 英雄视觉 */
.hero-visual {
  flex: 1;
  max-width: 500px;
  position: relative;
  height: 500px;
}

.visual-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  position: absolute;
}

.visual-card.main {
  width: 320px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.visual-card.floating {
  width: 200px;
  animation: float 6s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

.visual-card.floating:nth-child(2) {
  top: 10%;
  right: 0;
}

.visual-card.floating:nth-child(3) {
  bottom: 15%;
  left: 0;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(var(--offset-x, 10px), var(--offset-y, -10px)); }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.card-dots {
  display: flex;
  gap: 6px;
}

.card-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff5f57;
}

.card-dots span:nth-child(2) { background: #febc2e; }
.card-dots span:nth-child(3) { background: #28c840; }

.card-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.chart-preview {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 120px;
  gap: 8px;
  margin-bottom: 20px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, #00d4aa 0%, #00a8ff 100%);
  border-radius: 4px 4px 0 0;
  animation: grow 1s ease-out;
  min-height: 20%;
}

@keyframes grow {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.metric-unit {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
}

.metric-trend.down {
  color: #67c23a;
}

/* AI卡片 */
.ai-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #00d4aa;
  margin-bottom: 12px;
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-line {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  width: 100%;
}

.ai-line.short {
  width: 60%;
}

.ai-dots {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.ai-dots span {
  width: 6px;
  height: 6px;
  background: #00d4aa;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

/* Scope卡片 */
.scope-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 12px;
}

.scope-badge.scope-1 {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.scope-value {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.scope-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.scope-fill {
  height: 100%;
  background: linear-gradient(90deg, #e74c3c, #f39c12);
  border-radius: 3px;
}

/* 功能特性 */
.features-section {
  padding: 120px 80px;
  position: relative;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-tag {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(0, 212, 170, 0.1);
  border: 1px solid rgba(0, 212, 170, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #00d4aa;
  margin-bottom: 20px;
}

.section-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 32px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(0, 212, 170, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-card.large {
  grid-column: span 2;
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.7;
  margin-bottom: 16px;
}

.feature-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 展示区域 */
.showcase-section {
  padding: 120px 80px;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 212, 170, 0.03) 50%, transparent 100%);
}

.showcase-content {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1200px;
  margin: 0 auto;
}

.showcase-text {
  flex: 1;
}

.showcase-text .section-tag,
.showcase-text .section-title,
.showcase-text .section-desc {
  text-align: left;
}

.showcase-text .section-desc {
  margin: 0 0 24px;
}

.showcase-list {
  list-style: none;
  padding: 0;
  margin-bottom: 32px;
}

.showcase-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.check-icon {
  color: #00d4aa;
  font-size: 20px;
}

.showcase-visual {
  flex: 1;
  display: flex;
  justify-content: center;
}

.mockup-3d {
  width: 400px;
  height: 300px;
  position: relative;
  perspective: 1000px;
}

.ground {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) rotateX(60deg);
  width: 350px;
  height: 250px;
  background: linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 168, 255, 0.2) 100%);
  border: 2px solid rgba(0, 212, 170, 0.3);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 212, 170, 0.2);
}

.building {
  position: absolute;
  background: linear-gradient(180deg, rgba(0, 212, 170, 0.8) 0%, rgba(0, 168, 255, 0.6) 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  transform-style: preserve-3d;
  animation: building-glow 3s ease-in-out infinite;
}

.building::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}

@keyframes building-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 170, 0.3); }
  50% { box-shadow: 0 0 40px rgba(0, 212, 170, 0.6); }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.building.b1 {
  width: 60px;
  height: 100px;
  bottom: 80px;
  left: 80px;
  animation-delay: 0s;
}

.building.b2 {
  width: 50px;
  height: 140px;
  bottom: 60px;
  left: 160px;
  animation-delay: 0.5s;
}

.building.b3 {
  width: 70px;
  height: 80px;
  bottom: 100px;
  left: 230px;
  animation-delay: 1s;
}

.building.b4 {
  width: 45px;
  height: 120px;
  bottom: 70px;
  left: 320px;
  animation-delay: 1.5s;
}

.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particles span {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #00d4aa;
  border-radius: 50%;
  animation: particle-float linear infinite;
  box-shadow: 0 0 10px #00d4aa;
}

@keyframes particle-float {
  0% {
    transform: translateY(0) scale(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  100% {
    transform: translateY(-200px) scale(1);
    opacity: 0;
  }
}

/* AI区域 */
.ai-section {
  padding: 120px 80px;
}

.ai-content-wrapper {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1000px;
  margin: 0 auto;
}

.ai-visual {
  flex: 0 0 200px;
  display: flex;
  justify-content: center;
}

.ai-avatar {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #00d4aa 0%, #00a8ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  position: relative;
}

.ai-ring {
  position: absolute;
  inset: -10px;
  border: 2px solid rgba(0, 212, 170, 0.3);
  border-radius: 50%;
  animation: ring-expand 2s ease-out infinite;
}

@keyframes ring-expand {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

.ai-text {
  flex: 1;
}

.ai-text .section-tag,
.ai-text .section-title,
.ai-text .section-desc {
  text-align: left;
}

.ai-text .section-desc {
  margin: 0 0 24px;
}

.ai-examples {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-bubble {
  display: inline-block;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  animation: fade-in-up 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes fade-in-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* CTA区域 */
.cta-section {
  padding: 120px 80px;
  background: linear-gradient(135deg, rgba(0, 212, 170, 0.1) 0%, rgba(0, 168, 255, 0.1) 100%);
  text-align: center;
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
}

.cta-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 40px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 40px;
}

.cta-btn.large {
  padding: 18px 40px;
  font-size: 18px;
}

.trust-badges {
  display: flex;
  gap: 32px;
  justify-content: center;
}

.badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.badge .el-icon {
  color: #00d4aa;
}

/* 页脚 */
.landing-footer {
  padding: 40px 80px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #00d4aa;
}

.footer-links {
  display: flex;
  gap: 32px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #00d4aa;
}

.footer-copy {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
}

/* 响应式 */
@media (max-width: 1024px) {
  .hero-section {
    flex-direction: column;
    padding: 100px 40px 60px;
  }
  
  .hero-title {
    font-size: 40px;
  }
  
  .hero-visual {
    width: 100%;
    height: 400px;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .feature-card.large {
    grid-column: span 2;
  }
  
  .showcase-content,
  .ai-content-wrapper {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .landing-nav {
    padding: 12px 20px;
  }
  
  .hero-section,
  .features-section,
  .showcase-section,
  .ai-section,
  .cta-section {
    padding: 80px 20px;
  }
  
  .hero-title {
    font-size: 32px;
  }
  
  .hero-stats {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .hero-cta {
    flex-direction: column;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card.large {
    grid-column: span 1;
  }
  
  .section-title {
    font-size: 28px;
  }
  
  .cta-buttons {
    flex-direction: column;
  }
  
  .trust-badges {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}
</style>