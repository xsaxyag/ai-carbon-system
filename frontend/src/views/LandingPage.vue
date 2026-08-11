<template>
  <div class="landing-page" :class="{ 'loaded': pageLoaded }">
    <!-- 开场动画遮罩 -->
    <div class="intro-overlay" v-if="showIntro">
      <div class="intro-content">
        <div class="intro-logo">
          <el-icon :size="80" color="#00d4ff"><DataBoard /></el-icon>
        </div>
        <h1 class="intro-title">AI碳枢算</h1>
        <p class="intro-subtitle">中小微企业碳中和智能管理系统</p>
        <div class="intro-loading">
          <div class="loading-bar">
            <div class="loading-progress" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <span class="loading-text">{{ loadingText }}</span>
        </div>
      </div>
    </div>

    <!-- 粒子背景画布 -->
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <!-- 导航栏 -->
    <nav class="landing-nav" :class="{ 'scrolled': isScrolled }">
      <div class="nav-brand">
        <el-icon :size="32" color="#00d4ff"><DataBoard /></el-icon>
        <span class="brand-text">AI碳枢算</span>
      </div>
      <div class="nav-links">
        <a href="#features" @click.prevent="scrollToSection('features')">功能特性</a>
        <a href="#demo" @click.prevent="scrollToSection('demo')">产品演示</a>
        <a href="#ai-advisor" @click.prevent="scrollToSection('ai-advisor')">AI顾问</a>
        <a href="#pricing" @click.prevent="scrollToSection('pricing')">价格方案</a>
      </div>
      <div class="nav-actions">
        <el-button text class="nav-btn" @click="goToLogin">登录</el-button>
        <el-button type="primary" class="nav-btn-primary" @click="goToRegister">
          免费试用
        </el-button>
      </div>
    </nav>

    <!-- 英雄区 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge" :class="{ 'animate-in': pageLoaded }">
          <el-icon><StarFilled /></el-icon>
          <span>GB/T 32150 标准合规 · 生态环境部因子库</span>
        </div>
        
        <h1 class="hero-title" :class="{ 'animate-in': pageLoaded }">
          <span class="gradient-text">AI驱动</span>的碳中和
          <br />智能管理平台
        </h1>
        
        <p class="hero-description" :class="{ 'animate-in': pageLoaded }">
          专为中小微企业打造的碳排放核算、碳足迹追踪、减排优化一站式解决方案。
          <br />从数据录入到ISO标准报告生成，AI全程赋能，让碳管理变得简单高效。
        </p>
        
        <div class="hero-stats" :class="{ 'animate-in': pageLoaded }">
          <div class="stat-item">
            <div class="stat-number">
              <span class="counter" data-target="500">0</span>+
            </div>
            <div class="stat-label">服务企业</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              <span class="counter" data-target="10000">0</span>+
            </div>
            <div class="stat-label">碳核算次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              <span class="counter" data-target="30">0</span>%
            </div>
            <div class="stat-label">平均减排率</div>
          </div>
        </div>
        
        <div class="hero-cta" :class="{ 'animate-in': pageLoaded }">
          <el-button type="primary" size="large" class="cta-primary" @click="goToRegister">
            <el-icon><User /></el-icon>
            免费注册，开启碳中和之旅
          </el-button>
          <el-button size="large" class="cta-secondary" @click="scrollToSection('demo')">
            <el-icon><VideoPlay /></el-icon>
            观看产品演示
          </el-button>
        </div>
      </div>

      <!-- 3D预览卡片 -->
      <div class="hero-preview" :class="{ 'animate-in': pageLoaded }">
        <div class="preview-card">
          <div class="preview-header">
            <div class="preview-dots">
              <span></span><span></span><span></span>
            </div>
            <span class="preview-title">碳排放实时监测</span>
          </div>
          <div class="preview-content">
            <div class="chart-mockup">
              <div class="chart-bars">
                <div class="bar" style="height: 60%"><span>Scope 1</span></div>
                <div class="bar" style="height: 80%"><span>Scope 2</span></div>
                <div class="bar highlight" style="height: 45%"><span>Scope 3</span></div>
              </div>
              <div class="chart-line">
                <svg viewBox="0 0 200 80">
                  <path d="M0,60 Q50,40 100,50 T200,20" stroke="#00d4ff" stroke-width="2" fill="none"/>
                  <circle cx="0" cy="60" r="3" fill="#00d4ff"/>
                  <circle cx="100" cy="50" r="3" fill="#00d4ff"/>
                  <circle cx="200" cy="20" r="3" fill="#00d4ff"/>
                </svg>
              </div>
            </div>
            <div class="ai-insight">
              <div class="ai-avatar">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="ai-message">
                <p>AI分析：本月碳排放较上月下降 <strong>12%</strong></p>
                <p class="ai-suggestion">建议：优化能源结构可进一步降低 Scope 2 排放</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 浮动元素 -->
        <div class="float-card card-1">
          <el-icon><TrendCharts /></el-icon>
          <span>实时数据</span>
        </div>
        <div class="float-card card-2">
          <el-icon><CircleCheck /></el-icon>
          <span>ISO合规</span>
        </div>
        <div class="float-card card-3">
          <el-icon><Timer /></el-icon>
          <span>7×24监控</span>
        </div>
      </div>
    </section>

    <!-- 核心功能特性 -->
    <section id="features" class="features-section">
      <div class="section-header scroll-reveal">
        <span class="section-tag">核心功能</span>
        <h2 class="section-title">一站式碳管理解决方案</h2>
        <p class="section-desc">从数据采集到报告生成，从碳核算到减排优化，覆盖碳管理全生命周期</p>
      </div>

      <div class="features-grid">
        <div class="feature-card scroll-reveal" v-for="(feature, index) in features" :key="index" :style="{ animationDelay: index * 0.1 + 's' }">
          <div class="feature-icon" :class="feature.colorClass">
            <el-icon :size="32"><component :is="feature.icon" /></el-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
          <ul class="feature-list">
            <li v-for="item in feature.items" :key="item">
              <el-icon><Check /></el-icon>
              {{ item }}
            </li>
          </ul>
          <div class="feature-hover">
            <el-button type="primary" text @click="goToRegister">
              了解更多 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- 3D可视化展示 -->
    <section id="demo" class="demo-section">
      <div class="demo-container">
        <div class="demo-content scroll-reveal">
          <span class="section-tag">3D可视化</span>
          <h2 class="section-title">沉浸式碳数据体验</h2>
          <p class="section-desc">
            将抽象的碳排放数据转化为直观的3D可视化场景。
            园区地图一键3D化、数字孪生工厂、供应链碳图谱，
            让碳管理从数字走向空间。
          </p>
          <div class="demo-features">
            <div class="demo-feature">
              <el-icon><MapLocation /></el-icon>
              <div>
                <h4>园区地图3D化</h4>
                <p>上传平面图，AI自动生成3D园区模型</p>
              </div>
            </div>
            <div class="demo-feature">
              <el-icon><OfficeBuilding /></el-icon>
              <div>
                <h4>数字孪生工厂</h4>
                <p>实时映射生产流程，碳排放一目了然</p>
              </div>
            </div>
            <div class="demo-feature">
              <el-icon><Share /></el-icon>
              <div>
                <h4>供应链碳图谱</h4>
                <p>全链路碳足迹追踪，识别高排放节点</p>
              </div>
            </div>
          </div>
          <el-button type="primary" size="large" @click="goToRegister">
            立即体验3D功能
          </el-button>
        </div>
        <div class="demo-visual scroll-reveal">
          <div class="demo-3d-scene">
            <div class="building building-1"></div>
            <div class="building building-2"></div>
            <div class="building building-3"></div>
            <div class="building building-4"></div>
            <div class="ground-grid"></div>
            <div class="data-particles">
              <span v-for="n in 20" :key="n" :style="{ animationDelay: n * 0.2 + 's' }"></span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI碳顾问 -->
    <section id="ai-advisor" class="ai-section">
      <div class="ai-container">
        <div class="ai-visual scroll-reveal">
          <div class="ai-avatar-large">
            <div class="ai-pulse"></div>
            <div class="ai-core">
              <el-icon :size="64"><Cpu /></el-icon>
            </div>
          </div>
          <div class="ai-chat-preview">
            <div class="chat-bubble user">
              <p>如何降低我们工厂的碳排放？</p>
            </div>
            <div class="chat-bubble ai">
              <p>根据您的数据分析，建议从以下3个方面入手：</p>
              <ol>
                <li>优化能源结构，增加绿电比例</li>
                <li>改进生产工艺，提高能效</li>
                <li>建立碳资产管理体系</li>
              </ol>
              <p>预计可实现减排 <strong>15-25%</strong></p>
            </div>
          </div>
        </div>
        <div class="ai-content scroll-reveal">
          <span class="section-tag">AI智能顾问</span>
          <h2 class="section-title">24小时碳管理专家</h2>
          <p class="section-desc">
            基于GLM-5.1大模型，深度融合碳核算专业知识。
            无论是ISO标准解读、碳足迹计算，还是减排方案制定，
            AI顾问都能给出专业、可执行的建议。
          </p>
          <div class="ai-capabilities">
            <div class="capability">
              <el-icon><ChatDotRound /></el-icon>
              <span>自然语言问答</span>
            </div>
            <div class="capability">
              <el-icon><Document /></el-icon>
              <span>ISO标准解读</span>
            </div>
            <div class="capability">
              <el-icon><TrendCharts /></el-icon>
              <span>减排方案推荐</span>
            </div>
            <div class="capability">
              <el-icon><Money /></el-icon>
              <span>碳资产交易咨询</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 价格方案 -->
    <section id="pricing" class="pricing-section">
      <div class="section-header scroll-reveal">
        <span class="section-tag">价格方案</span>
        <h2 class="section-title">灵活选择，按需升级</h2>
        <p class="section-desc">从免费试用到企业级定制，满足不同规模企业的碳管理需求</p>
      </div>

      <div class="pricing-grid">
        <div class="pricing-card scroll-reveal">
          <div class="pricing-header">
            <h3>免费版</h3>
            <div class="pricing-price">
              <span class="currency">¥</span>
              <span class="amount">0</span>
              <span class="period">/月</span>
            </div>
          </div>
          <ul class="pricing-features">
            <li><el-icon><Check /></el-icon>基础碳核算（Scope 1/2）</li>
            <li><el-icon><Check /></el-icon>标准数据报表</li>
            <li><el-icon><Check /></el-icon>AI顾问基础问答</li>
            <li><el-icon><Check /></el-icon>1个企业管理</li>
            <li class="disabled"><el-icon><Close /></el-icon>3D可视化</li>
            <li class="disabled"><el-icon><Close /></el-icon>ISO报告生成</li>
          </ul>
          <el-button class="pricing-btn" @click="goToRegister">免费开始</el-button>
        </div>

        <div class="pricing-card popular scroll-reveal">
          <div class="popular-badge">最受欢迎</div>
          <div class="pricing-header">
            <h3>专业版</h3>
            <div class="pricing-price">
              <span class="currency">¥</span>
              <span class="amount">299</span>
              <span class="period">/月</span>
            </div>
          </div>
          <ul class="pricing-features">
            <li><el-icon><Check /></el-icon>全功能碳核算（Scope 1/2/3）</li>
            <li><el-icon><Check /></el-icon>3D可视化大屏</li>
            <li><el-icon><Check /></el-icon>AI顾问高级功能</li>
            <li><el-icon><Check /></el-icon>ISO 14064/14067报告</li>
            <li><el-icon><Check /></el-icon>10个企业管理</li>
            <li><el-icon><Check /></el-icon>碳资产管理</li>
          </ul>
          <el-button type="primary" class="pricing-btn" @click="goToRegister">立即升级</el-button>
        </div>

        <div class="pricing-card scroll-reveal">
          <div class="pricing-header">
            <h3>企业版</h3>
            <div class="pricing-price">
              <span class="currency">¥</span>
              <span class="amount">定制</span>
            </div>
          </div>
          <ul class="pricing-features">
            <li><el-icon><Check /></el-icon>专业版全部功能</li>
            <li><el-icon><Check /></el-icon>私有化部署</li>
            <li><el-icon><Check /></el-icon>API接口开放</li>
            <li><el-icon><Check /></el-icon>专属客户成功经理</li>
            <li><el-icon><Check /></el-icon>定制化开发</li>
            <li><el-icon><Check /></el-icon>SLA服务保障</li>
          </ul>
          <el-button class="pricing-btn" @click="goToRegister">联系销售</el-button>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="cta-section">
      <div class="cta-content scroll-reveal">
        <h2>开启您的碳中和之旅</h2>
        <p>加入500+企业，用AI赋能碳管理，共创绿色未来</p>
        <div class="cta-buttons">
          <el-button type="primary" size="large" @click="goToRegister">
            <el-icon><User /></el-icon>
            免费注册使用
          </el-button>
          <el-button size="large" @click="goToLogin">
            已有账号？立即登录
          </el-button>
        </div>
        <div class="trust-badges">
          <div class="badge">
            <el-icon><Lock /></el-icon>
            <span>数据安全加密</span>
          </div>
          <div class="badge">
            <el-icon><CircleCheck /></el-icon>
            <span>国标合规</span>
          </div>
          <div class="badge">
            <el-icon><Timer /></el-icon>
            <span>7×24小时服务</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <el-icon :size="32" color="#00d4ff"><DataBoard /></el-icon>
          <span>AI碳枢算</span>
          <p>中小微企业碳中和智能管理系统</p>
        </div>
        <div class="footer-links">
          <div class="footer-column">
            <h4>产品</h4>
            <a href="#features">功能特性</a>
            <a href="#pricing">价格方案</a>
            <a href="#demo">产品演示</a>
          </div>
          <div class="footer-column">
            <h4>支持</h4>
            <a href="#">帮助中心</a>
            <a href="#">API文档</a>
            <a href="#">联系我们</a>
          </div>
          <div class="footer-column">
            <h4>关于</h4>
            <a href="#">关于我们</a>
            <a href="#">隐私政策</a>
            <a href="#">服务条款</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2024 AI碳枢算 · 基于 GB/T 32150 标准 · 生态环境部排放因子库</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataBoard, User, VideoPlay, TrendCharts, CircleCheck, Timer,
  Check, ArrowRight, MapLocation, OfficeBuilding, Share,
  Cpu, ChatDotRound, Document, Money, Lock, Close,
  StarFilled, Coin, Camera, ScaleToOriginal, Bell,
  Wallet, Box, Guide, FolderOpened, Promotion, Lightning
} from '@element-plus/icons-vue'

const router = useRouter()
const particleCanvas = ref(null)
const isScrolled = ref(false)
const pageLoaded = ref(false)
const showIntro = ref(true)
const loadingProgress = ref(0)
const loadingText = ref('初始化系统...')

// 功能特性数据
const features = [
  {
    icon: 'Coin',
    title: '智能碳核算',
    description: '基于GB/T 32150标准，自动识别排放源，智能匹配排放因子，一键生成符合规范的碳排放报告。',
    items: ['Scope 1/2/3全覆盖', '生态环境部因子库', 'OCR智能识别票据', '多维度数据校验'],
    colorClass: 'blue'
  },
  {
    icon: 'TrendCharts',
    title: '3D可视化大屏',
    description: '将碳数据转化为沉浸式3D场景，园区地图一键3D化、数字孪生工厂、供应链碳图谱，直观呈现碳排放分布。',
    items: ['园区地图3D化', '数字孪生工厂', '供应链碳图谱', '源网荷储协同'],
    colorClass: 'purple'
  },
  {
    icon: 'Promotion',
    title: 'AI智能顾问',
    description: '7×24小时在线的碳管理专家，基于大模型深度理解ISO标准，提供专业问答、减排建议、政策解读。',
    items: ['自然语言交互', 'ISO标准解读', '减排方案推荐', '碳交易咨询'],
    colorClass: 'cyan'
  },
  {
    icon: 'TrendCharts',
    title: '减排优化',
    description: 'AI分析碳排放数据，识别减排潜力点，生成定制化减排方案，追踪减排效果，助力企业实现碳中和目标。',
    items: ['减排潜力分析', '优化方案生成', '效果追踪评估', '碳中和路径规划'],
    colorClass: 'green'
  },
  {
    icon: 'Wallet',
    title: '碳资产管理',
    description: '支持CCER、VCS、GS、I-REC等主流碳资产类型，实现资产登记、估值、交易全流程管理。',
    items: ['多类型碳资产', '实时估值监控', '交易记录管理', '资产健康分析'],
    colorClass: 'orange'
  },
  {
    icon: 'Document',
    title: 'ISO标准报告',
    description: '一键生成ISO 14064-1组织碳盘查报告、ISO 14067产品碳足迹报告，满足国际认证需求。',
    items: ['ISO 14064-1报告', 'ISO 14067报告', '自动格式排版', '多语言导出'],
    colorClass: 'pink'
  }
]

// 开场动画
const runIntroAnimation = async () => {
  const steps = [
    { progress: 20, text: '加载碳核算引擎...' },
    { progress: 45, text: '连接排放因子库...' },
    { progress: 70, text: '初始化AI顾问...' },
    { progress: 90, text: '准备3D可视化...' },
    { progress: 100, text: '系统就绪' }
  ]
  
  for (const step of steps) {
    loadingProgress.value = step.progress
    loadingText.value = step.text
    await new Promise(r => setTimeout(r, 400))
  }
  
  await new Promise(r => setTimeout(r, 300))
  showIntro.value = false
  pageLoaded.value = true
  
  // 启动数字动画
  nextTick(() => {
    startCounters()
    initScrollReveal()
  })
}

// 数字增长动画
const startCounters = () => {
  const counters = document.querySelectorAll('.counter')
  counters.forEach(counter => {
    const target = parseInt(counter.dataset.target)
    const duration = 2000
    const step = target / (duration / 16)
    let current = 0
    
    const updateCounter = () => {
      current += step
      if (current < target) {
        counter.textContent = Math.floor(current)
        requestAnimationFrame(updateCounter)
      } else {
        counter.textContent = target
      }
    }
    updateCounter()
  })
}

// 滚动显示动画
const initScrollReveal = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed')
      }
    })
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' })
  
  document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el))
}

// 粒子系统
const initParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let particles = []
  let animationId
  let mouseX = 0
  let mouseY = 0
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  const createParticle = () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.5,
    vy: (Math.random() - 0.5) * 0.5,
    size: Math.random() * 2 + 1,
    opacity: Math.random() * 0.5 + 0.2,
    color: Math.random() > 0.5 ? '#00d4ff' : '#0099ff'
  })
  
  // 创建更多粒子
  for (let i = 0; i < 100; i++) {
    particles.push(createParticle())
  }
  
  const drawParticles = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach((p, i) => {
      // 更新位置
      p.x += p.vx
      p.y += p.vy
      
      // 鼠标交互
      const dx = mouseX - p.x
      const dy = mouseY - p.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 150) {
        p.x -= dx * 0.02
        p.y -= dy * 0.02
      }
      
      // 边界处理
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1
      
      // 绘制粒子
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx.fillStyle = p.color
      ctx.globalAlpha = p.opacity
      ctx.fill()
      
      // 连线
      particles.slice(i + 1).forEach(p2 => {
        const dx2 = p.x - p2.x
        const dy2 = p.y - p2.y
        const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)
        
        if (dist2 < 120) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = '#00d4ff'
          ctx.globalAlpha = (1 - dist2 / 120) * 0.2
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      })
    })
    
    ctx.globalAlpha = 1
    animationId = requestAnimationFrame(drawParticles)
  }
  
  const handleMouseMove = (e) => {
    mouseX = e.clientX
    mouseY = e.clientY
  }
  
  resize()
  drawParticles()
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', handleMouseMove)
  
  return () => {
    cancelAnimationFrame(animationId)
    window.removeEventListener('resize', resize)
    window.removeEventListener('mousemove', handleMouseMove)
  }
}

// 滚动处理
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

// 平滑滚动
const scrollToSection = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

// 路由跳转
const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')

onMounted(() => {
  runIntroAnimation()
  const cleanupParticles = initParticles()
  window.addEventListener('scroll', handleScroll)
  
  onUnmounted(() => {
    cleanupParticles()
    window.removeEventListener('scroll', handleScroll)
  })
})
</script>

<style scoped>
/* 基础样式 */
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
  overflow-x: hidden;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.landing-page.loaded {
  opacity: 1;
}

/* 开场动画 */
.intro-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeOut 0.5s ease 2.5s forwards;
}

@keyframes fadeOut {
  to { opacity: 0; visibility: hidden; }
}

.intro-content {
  text-align: center;
  animation: scaleIn 0.6s ease;
}

@keyframes scaleIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.intro-logo {
  margin-bottom: 24px;
  animation: pulse 2s ease infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.intro-title {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.intro-subtitle {
  font-size: 18px;
  color: #a0a0b0;
  margin-bottom: 40px;
}

.intro-loading {
  width: 300px;
  margin: 0 auto;
}

.loading-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
}

.loading-progress {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0099ff);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.loading-text {
  font-size: 14px;
  color: #00d4ff;
}

/* 粒子画布 */
.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

/* 导航栏 */
.landing-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 60px;
  z-index: 1000;
  transition: all 0.3s ease;
  background: transparent;
}

.landing-nav.scrolled {
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 40px;
}

.nav-links a {
  color: #c0c0d0;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
  position: relative;
}

.nav-links a:hover {
  color: #00d4ff;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #00d4ff, #0099ff);
  transition: width 0.3s;
}

.nav-links a:hover::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  gap: 16px;
}

.nav-btn {
  color: #fff;
}

.nav-btn-primary {
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border: none;
}

/* 英雄区 */
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 120px 60px 80px;
  position: relative;
  z-index: 10;
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #00d4ff;
  margin-bottom: 24px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.hero-badge.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease 0.1s;
}

.hero-title.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.gradient-text {
  background: linear-gradient(135deg, #00d4ff, #0099ff, #00ff88);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-description {
  font-size: 18px;
  color: #a0a0b0;
  line-height: 1.8;
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease 0.2s;
}

.hero-description.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.hero-stats {
  display: flex;
  gap: 48px;
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease 0.3s;
}

.hero-stats.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #00d4ff;
}

.stat-label {
  font-size: 14px;
  color: #808090;
  margin-top: 4px;
}

.hero-cta {
  display: flex;
  gap: 16px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease 0.4s;
}

.hero-cta.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.cta-primary {
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border: none;
  padding: 16px 32px;
  font-size: 16px;
}

.cta-secondary {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 16px 32px;
  font-size: 16px;
}

/* 预览卡片 */
.hero-preview {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  opacity: 0;
  transform: translateX(50px);
  transition: all 0.8s ease 0.3s;
}

.hero-preview.animate-in {
  opacity: 1;
  transform: translateX(0);
}

.preview-card {
  width: 420px;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.preview-dots {
  display: flex;
  gap: 6px;
}

.preview-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff5f57;
}

.preview-dots span:nth-child(2) { background: #ffbd2e; }
.preview-dots span:nth-child(3) { background: #28c840; }

.preview-title {
  font-size: 14px;
  color: #808090;
}

.chart-mockup {
  background: rgba(0,0,0,0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 120px;
  margin-bottom: 16px;
}

.bar {
  width: 60px;
  background: linear-gradient(to top, #00d4ff, #0099ff);
  border-radius: 4px 4px 0 0;
  position: relative;
  animation: growBar 1s ease forwards;
  transform-origin: bottom;
}

@keyframes growBar {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}

.bar.highlight {
  background: linear-gradient(to top, #00ff88, #00cc66);
}

.bar span {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #808090;
}

.chart-line {
  height: 80px;
}

.ai-insight {
  display: flex;
  gap: 12px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-message {
  font-size: 13px;
  color: #c0c0d0;
}

.ai-message strong {
  color: #00ff88;
}

.ai-suggestion {
  margin-top: 4px;
  color: #808090;
  font-size: 12px;
}

/* 浮动卡片 */
.float-card {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  font-size: 13px;
  color: #fff;
  animation: floatCard 4s ease-in-out infinite;
}

.float-card.card-1 {
  top: 10%;
  right: 10%;
  animation-delay: 0s;
}

.float-card.card-2 {
  bottom: 20%;
  left: -10%;
  animation-delay: 1s;
}

.float-card.card-3 {
  bottom: 10%;
  right: 0%;
  animation-delay: 2s;
}

@keyframes floatCard {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 功能特性区 */
.features-section {
  padding: 120px 60px;
  position: relative;
  z-index: 10;
}

.section-header {
  text-align: center;
  margin-bottom: 80px;
}

.section-tag {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #00d4ff;
  margin-bottom: 20px;
}

.section-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-desc {
  font-size: 18px;
  color: #808090;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.feature-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 40px 30px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-card:hover {
  transform: translateY(-10px);
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.15);
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  color: #fff;
}

.feature-icon.blue {
  background: linear-gradient(135deg, #00d4ff, #0099ff);
}

.feature-icon.purple {
  background: linear-gradient(135deg, #a855f7, #6366f1);
}

.feature-icon.cyan {
  background: linear-gradient(135deg, #22d3ee, #06b6d4);
}

.feature-icon.green {
  background: linear-gradient(135deg, #4ade80, #22c55e);
}

.feature-icon.orange {
  background: linear-gradient(135deg, #fb923c, #f97316);
}

.feature-icon.pink {
  background: linear-gradient(135deg, #f472b6, #ec4899);
}

.feature-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 14px;
  color: #808090;
  line-height: 1.7;
  margin-bottom: 20px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #a0a0b0;
  margin-bottom: 8px;
}

.feature-list li .el-icon {
  color: #00d4ff;
  font-size: 14px;
}

.feature-hover {
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.feature-card:hover .feature-hover {
  opacity: 1;
  transform: translateY(0);
}

/* 3D演示区 */
.demo-section {
  padding: 120px 60px;
  background: linear-gradient(180deg, transparent 0%, rgba(0,212,255,0.03) 50%, transparent 100%);
}

.demo-container {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-content {
  flex: 1;
}

.demo-content .section-title {
  text-align: left;
}

.demo-content .section-desc {
  text-align: left;
  margin: 0 0 40px;
}

.demo-features {
  margin-bottom: 40px;
}

.demo-feature {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.demo-feature .el-icon {
  font-size: 24px;
  color: #00d4ff;
  margin-top: 4px;
}

.demo-feature h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.demo-feature p {
  font-size: 14px;
  color: #808090;
}

.demo-visual {
  flex: 1;
  display: flex;
  justify-content: center;
}

.demo-3d-scene {
  width: 500px;
  height: 400px;
  position: relative;
  perspective: 1000px;
}

.building {
  position: absolute;
  background: linear-gradient(135deg, rgba(0,212,255,0.3), rgba(0,153,255,0.1));
  border: 1px solid rgba(0,212,255,0.5);
  transform-style: preserve-3d;
  animation: buildingPulse 3s ease-in-out infinite;
}

.building-1 {
  width: 80px;
  height: 200px;
  left: 100px;
  top: 100px;
  animation-delay: 0s;
}

.building-2 {
  width: 100px;
  height: 150px;
  left: 200px;
  top: 150px;
  animation-delay: 0.5s;
}

.building-3 {
  width: 60px;
  height: 180px;
  left: 320px;
  top: 120px;
  animation-delay: 1s;
}

.building-4 {
  width: 120px;
  height: 100px;
  left: 150px;
  top: 50px;
  animation-delay: 1.5s;
}

@keyframes buildingPulse {
  0%, 100% { 
    box-shadow: 0 0 20px rgba(0,212,255,0.3);
    transform: translateZ(0);
  }
  50% { 
    box-shadow: 0 0 40px rgba(0,212,255,0.6);
    transform: translateZ(20px);
  }
}

.ground-grid {
  position: absolute;
  bottom: 0;
  left: 50px;
  right: 50px;
  height: 100px;
  background: 
    linear-gradient(90deg, rgba(0,212,255,0.1) 1px, transparent 1px),
    linear-gradient(rgba(0,212,255,0.1) 1px, transparent 1px);
  background-size: 40px 40px;
  transform: rotateX(60deg);
  transform-origin: bottom;
}

.data-particles span {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #00d4ff;
  border-radius: 50%;
  animation: particleRise 2s ease-in-out infinite;
}

@keyframes particleRise {
  0% { 
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  100% { 
    transform: translateY(-100px) scale(0);
    opacity: 0;
  }
}

/* AI顾问区 */
.ai-section {
  padding: 120px 60px;
}

.ai-container {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1400px;
  margin: 0 auto;
}

.ai-visual {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ai-avatar-large {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 40px;
}

.ai-pulse {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(0,212,255,0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: aiPulse 2s ease-in-out infinite;
}

@keyframes aiPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.ai-core {
  position: absolute;
  inset: 30px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 60px rgba(0,212,255,0.5);
}

.ai-chat-preview {
  width: 100%;
  max-width: 400px;
}

.chat-bubble {
  padding: 16px 20px;
  border-radius: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  line-height: 1.6;
  animation: messageSlide 0.5s ease;
}

@keyframes messageSlide {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-bubble.user {
  background: rgba(0,212,255,0.1);
  border: 1px solid rgba(0,212,255,0.3);
  margin-left: 20%;
}

.chat-bubble.ai {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  margin-right: 20%;
}

.chat-bubble.ai ol {
  margin: 12px 0;
  padding-left: 20px;
}

.chat-bubble.ai li {
  margin-bottom: 8px;
  color: #c0c0d0;
}

.chat-bubble.ai strong {
  color: #00ff88;
}

.ai-content {
  flex: 1;
}

.ai-content .section-title,
.ai-content .section-desc {
  text-align: left;
}

.ai-content .section-desc {
  margin: 0 0 40px;
}

.ai-capabilities {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.capability {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.capability:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(0,212,255,0.3);
  transform: translateX(10px);
}

.capability .el-icon {
  font-size: 24px;
  color: #00d4ff;
}

/* 价格方案 */
.pricing-section {
  padding: 120px 60px;
  background: linear-gradient(180deg, transparent 0%, rgba(0,212,255,0.02) 50%, transparent 100%);
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.pricing-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  padding: 40px 30px;
  position: relative;
  transition: all 0.4s ease;
}

.pricing-card:hover {
  transform: translateY(-10px);
  background: rgba(255,255,255,0.05);
}

.pricing-card.popular {
  background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,153,255,0.05));
  border-color: rgba(0,212,255,0.3);
  transform: scale(1.05);
}

.pricing-card.popular:hover {
  transform: scale(1.05) translateY(-10px);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 16px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.pricing-header {
  text-align: center;
  margin-bottom: 30px;
}

.pricing-header h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
}

.pricing-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.pricing-price .currency {
  font-size: 24px;
  color: #808090;
}

.pricing-price .amount {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.pricing-price .period {
  font-size: 16px;
  color: #808090;
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
}

.pricing-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  font-size: 14px;
  color: #c0c0d0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.pricing-features li.disabled {
  color: #505060;
}

.pricing-features li .el-icon {
  font-size: 16px;
}

.pricing-features li:not(.disabled) .el-icon {
  color: #00ff88;
}

.pricing-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
}

/* CTA区域 */
.cta-section {
  padding: 120px 60px;
  text-align: center;
}

.cta-content h2 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-content p {
  font-size: 18px;
  color: #808090;
  margin-bottom: 40px;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.trust-badges {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #808090;
}

.badge .el-icon {
  color: #00d4ff;
}

/* 页脚 */
.landing-footer {
  padding: 60px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto 40px;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-brand span {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.footer-brand p {
  font-size: 14px;
  color: #808090;
}

.footer-links {
  display: flex;
  gap: 80px;
}

.footer-column h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

.footer-column a {
  display: block;
  font-size: 14px;
  color: #808090;
  text-decoration: none;
  margin-bottom: 12px;
  transition: color 0.3s;
}

.footer-column a:hover {
  color: #00d4ff;
}

.footer-bottom {
  text-align: center;
  padding-top: 40px;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.footer-bottom p {
  font-size: 14px;
  color: #505060;
}

/* 滚动显示动画 */
.scroll-reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: all 0.8s ease;
}

.scroll-reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* 响应式 */
@media (max-width: 1200px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    padding: 100px 40px 60px;
  }
  
  .hero-content {
    max-width: 100%;
  }
  
  .hero-stats {
    justify-content: center;
  }
  
  .hero-cta {
    justify-content: center;
  }
  
  .hero-preview {
    margin-top: 60px;
  }
  
  .features-grid,
  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .demo-container,
  .ai-container {
    flex-direction: column;
  }
  
  .demo-content .section-title,
  .demo-content .section-desc,
  .ai-content .section-title,
  .ai-content .section-desc {
    text-align: center;
  }
}

@media (max-width: 768px) {
  .landing-nav {
    padding: 0 20px;
  }
  
  .nav-links {
    display: none;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .features-grid,
  .pricing-grid {
    grid-template-columns: 1fr;
  }
  
  .pricing-card.popular {
    transform: none;
  }
  
  .trust-badges {
    flex-direction: column;
    gap: 16px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 40px;
  }
}
</style>
