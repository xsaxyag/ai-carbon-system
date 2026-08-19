<template>
  <div class="landing-page" ref="landingRef">
    <!-- 动态背景层 -->
    <div class="bg-layers">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <canvas ref="particleCanvas" class="particle-canvas"></canvas>
      <div class="bg-glow"></div>
    </div>

    <!-- 导航栏 -->
    <nav class="nav-bar" :class="{ 'nav-visible': navVisible }">
      <div class="nav-logo" @click="scrollToTop">
        <div class="logo-icon">
          <el-icon :size="28"><DataBoard /></el-icon>
        </div>
        <span class="logo-text">AI碳枢算</span>
      </div>
      
      <div class="nav-menu">
        <a v-for="item in navItems" :key="item.id" 
           :href="'#' + item.id"
           @click.prevent="scrollToSection(item.id)"
           :class="{ active: activeSection === item.id }">
          {{ item.label }}
          <span class="nav-dot"></span>
        </a>
      </div>
      
      <div class="nav-actions">
        <button class="btn-ghost" @click="goToLogin">登录</button>
        <button class="btn-primary" @click="goToRegister">
          <span>免费试用</span>
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
    </nav>

    <!-- 英雄区 -->
    <section class="hero" id="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-pulse"></span>
          <el-icon><StarFilled /></el-icon>
          <span>GB/T 32150 标准合规</span>
        </div>
        
        <h1 class="hero-title">
          <span class="title-line" v-for="(line, i) in titleLines" :key="i" :style="{ animationDelay: i * 0.2 + 's' }">
            <span v-html="line"></span>
          </span>
        </h1>
        
        <p class="hero-desc" :class="{ 'typing-done': typingDone }">
          <span class="typing-text">{{ typedText }}</span>
          <span class="typing-cursor" v-if="!typingDone"></span>
        </p>
        
        <div class="hero-stats">
          <div class="stat-card" v-for="(stat, i) in stats" :key="i" :style="{ animationDelay: 1.5 + i * 0.15 + 's' }">
            <div class="stat-icon">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-number">
              <span class="counter" ref="counters">{{ stat.value }}</span>
              <span class="stat-unit">{{ stat.unit }}</span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
        
        <div class="hero-cta">
          <button class="btn-magic" @click="goToRegister">
            <span class="btn-bg"></span>
            <span class="btn-text">
              <el-icon><Promotion /></el-icon>
              立即开启碳中和之旅
            </span>
          </button>
          <button class="btn-video" @click="showVideo = true">
            <span class="play-icon">
              <el-icon><VideoPlay /></el-icon>
            </span>
            <span>观看演示</span>
          </button>
        </div>
      </div>

      <!-- 3D场景预览 -->
      <div class="hero-visual">
        <div class="scene-container" :style="sceneStyle">
          <div class="scene-card" v-for="(card, i) in sceneCards" :key="i" :class="card.class" :style="card.style">
            <div class="card-content">
              <el-icon :size="32"><component :is="card.icon" /></el-icon>
              <span>{{ card.text }}</span>
            </div>
          </div>
          
          <div class="floating-island">
            <div class="island-base"></div>
            <div class="island-buildings">
              <div class="bldg bldg-1"></div>
              <div class="bldg bldg-2"></div>
              <div class="bldg bldg-3"></div>
            </div>
            <div class="island-trees">
              <div class="tree" v-for="n in 5" :key="n"></div>
            </div>
            <div class="carbon-rings">
              <div class="ring" v-for="n in 3" :key="n" :style="{ animationDelay: n * 0.5 + 's' }"></div>
            </div>
          </div>
          
          <div class="orbit-particles">
            <div class="orbit-particle" v-for="n in 8" :key="n" :style="{ animationDelay: n * 0.3 + 's' }"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 场景化功能展示 -->
    <section class="story-section" id="features">
      <div class="section-header">
        <span class="section-tag">场景化体验</span>
        <h2>碳管理，从未如此简单</h2>
        <p>跟随小明的碳中和之旅，看看 AI碳枢算 如何助力企业实现绿色转型</p>
      </div>

      <div class="story-timeline">
        <div class="story-card" v-for="(story, i) in stories" :key="i" :class="{ 'story-left': i % 2 === 0, 'story-right': i % 2 === 1 }">
          <div class="story-visual" :class="story.theme">
            <div class="story-screenshot" v-if="story.screenshot">
              <img :src="story.screenshot" :alt="story.title" />
            </div>
            <div class="story-anim" v-else>
              <div class="anim-element" v-for="(el, j) in story.animElements" :key="j" :class="el.class" :style="el.style"></div>
            </div>
          </div>
          <div class="story-content">
            <div class="story-step">步骤 {{ i + 1 }}</div>
            <h3>{{ story.title }}</h3>
            <p>{{ story.desc }}</p>
            <ul class="story-features">
              <li v-for="feat in story.features" :key="feat">
                <el-icon><Check /></el-icon>
                {{ feat }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- 互动功能卡片 -->
    <section class="features-grid-section" id="capabilities">
      <div class="section-header">
        <span class="section-tag">核心能力</span>
        <h2>全方位碳管理工具箱</h2>
      </div>
      
      <div class="features-grid">
        <div class="feature-flip-card" v-for="(feature, i) in features" :key="i" @mouseenter="feature.hovered = true" @mouseleave="feature.hovered = false">
          <div class="flip-inner" :class="{ flipped: feature.hovered }">
            <div class="flip-front" :class="feature.theme">
              <div class="feature-icon-wrap">
                <el-icon :size="48"><component :is="feature.icon" /></el-icon>
              </div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.brief }}</p>
              <div class="flip-hint">
                <el-icon><ArrowRight /></el-icon>
                了解更多
              </div>
            </div>
            <div class="flip-back" :class="feature.theme">
              <h4>{{ feature.title }}</h4>
              <p>{{ feature.detail }}</p>
              <ul>
                <li v-for="item in feature.items" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI顾问互动演示 -->
    <section class="ai-demo-section" id="ai">
      <div class="ai-container">
        <div class="ai-intro">
          <span class="section-tag">AI智能顾问</span>
          <h2>24小时在线的碳管理专家</h2>
          <p>基于大模型技术，深度融合碳核算专业知识，为您提供专业、可执行的碳管理建议</p>
        </div>
        
        <div class="ai-chat-demo">
          <div class="chat-window">
            <div class="chat-header">
              <div class="ai-avatar">
                <div class="avatar-pulse"></div>
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="ai-info">
                <span class="ai-name">碳小智</span>
                <span class="ai-status">
                  <span class="status-dot"></span>
                  在线
                </span>
              </div>
            </div>
            <div class="chat-messages" ref="chatMessages">
              <div v-for="(msg, i) in chatMessages" :key="i" :class="['message', msg.type]">
                <div class="message-content" v-html="msg.content"></div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </div>
            <div class="chat-input">
              <input type="text" placeholder="输入您的问题..." readonly />
              <button>
                <el-icon><Promotion /></el-icon>
              </button>
            </div>
          </div>
          
          <div class="ai-capabilities">
            <div class="capability-tag" v-for="cap in aiCapabilities" :key="cap">
              <el-icon><Check /></el-icon>
              {{ cap }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据可视化展示 -->
    <section class="viz-section" id="viz">
      <div class="viz-container">
        <div class="viz-content">
          <span class="section-tag">3D可视化</span>
          <h2>让碳数据"活"起来</h2>
          <p>告别枯燥的表格和图表，用沉浸式的3D场景直观呈现碳排放数据，一眼洞察问题所在</p>
          
          <div class="viz-features">
            <div class="viz-feature" v-for="(viz, i) in vizFeatures" :key="i">
              <div class="viz-icon" :class="viz.color">
                <el-icon :size="28"><component :is="viz.icon" /></el-icon>
              </div>
              <div class="viz-text">
                <h4>{{ viz.title }}</h4>
                <p>{{ viz.desc }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="viz-showcase">
          <div class="viz-tabs">
            <button v-for="(tab, i) in vizTabs" :key="i" 
                    :class="{ active: activeVizTab === i }"
                    @click="activeVizTab = i">
              {{ tab.label }}
            </button>
          </div>
          <div class="viz-display">
            <div class="viz-scene" :class="vizTabs[activeVizTab].scene">
              <img v-if="vizTabs[activeVizTab].screenshot" 
                   :src="vizTabs[activeVizTab].screenshot" 
                   :alt="vizTabs[activeVizTab].label"
                   class="viz-screenshot-img" />
              <template v-else>
                <div class="scene-element" v-for="(el, j) in vizTabs[activeVizTab].elements" :key="j" :class="el.class" :style="el.style"></div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 价格方案 -->
    <section class="pricing-section" id="pricing">
      <div class="section-header">
        <span class="section-tag">灵活定价</span>
        <h2>选择适合您的方案</h2>
      </div>
      
      <div class="pricing-cards">
        <div class="pricing-card" v-for="(plan, i) in pricingPlans" :key="i" :class="{ popular: plan.popular }">
          <div class="plan-header">
            <h3>{{ plan.name }}</h3>
            <div class="plan-price">
              <span class="currency">¥</span>
              <span class="amount">{{ plan.price }}</span>
              <span class="period">/月</span>
            </div>
          </div>
          <ul class="plan-features">
            <li v-for="feat in plan.features" :key="feat.text" :class="{ disabled: !feat.included }">
              <el-icon>{{ feat.included ? 'Check' : 'Close' }}</el-icon>
              {{ feat.text }}
            </li>
          </ul>
          <button :class="plan.popular ? 'btn-primary' : 'btn-ghost'" @click="goToRegister">
            {{ plan.cta }}
          </button>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="final-cta">
      <div class="cta-particles"></div>
      <div class="cta-content">
        <h2>准备好开启碳中和之旅了吗？</h2>
        <p>加入 500+ 企业，用 AI 赋能碳管理</p>
        <div class="cta-buttons">
          <button class="btn-magic btn-large" @click="goToRegister">
            <el-icon><Promotion /></el-icon>
            免费开始使用
          </button>
          <button class="btn-ghost btn-large" @click="goToLogin">
            已有账号？登录
          </button>
        </div>
        <div class="trust-signals">
          <span><el-icon><Lock /></el-icon> 数据安全加密</span>
          <span><el-icon><CircleCheck /></el-icon> 国标合规</span>
          <span><el-icon><Timer /></el-icon> 7×24小时服务</span>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <div class="logo-icon">
            <el-icon :size="32"><DataBoard /></el-icon>
          </div>
          <div>
            <span class="brand-name">AI碳枢算</span>
            <p>中小微企业碳中和智能管理系统</p>
          </div>
        </div>
        <div class="footer-links">
          <div class="link-group" v-for="group in footerLinks" :key="group.title">
            <h4>{{ group.title }}</h4>
            <router-link v-for="link in group.links" :key="link.slug" :to="`/static/${link.slug}`" class="footer-link">
              {{ link.label }}
            </router-link>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2024 AI碳枢算 · 基于 GB/T 32150 标准 · 生态环境部排放因子库</p>
      </div>
    </footer>

    <!-- 视频弹窗 -->
    <div class="video-modal" v-if="showVideo" @click.self="showVideo = false">
      <div class="video-container">
        <button class="close-btn" @click="showVideo = false">
          <el-icon><Close /></el-icon>
        </button>
        <div class="video-placeholder">
          <el-icon :size="64" class="video-icon"><VideoPlay /></el-icon>
          <h3>产品演示视频</h3>
          <p>即将上线，敬请期待</p>
          <div class="video-features">
            <span><el-icon><Check /></el-icon> 2分钟快速了解</span>
            <span><el-icon><Check /></el-icon> 真实用户案例</span>
            <span><el-icon><Check /></el-icon> 功能全景展示</span>
          </div>
          <button class="btn-primary" @click="showVideo = false" style="margin-top: 24px;">
            先体验产品
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataBoard, ArrowRight, StarFilled, VideoPlay,
  Check, Close, Cpu, Promotion, Lock, CircleCheck, Timer,
  OfficeBuilding, TrendCharts, Wallet, Document, MapLocation,
  Share, Lightning, Guide, FirstAidKit, Money, Bell
} from '@element-plus/icons-vue'

const router = useRouter()
const landingRef = ref(null)
const particleCanvas = ref(null)
const navVisible = ref(false)
const activeSection = ref('hero')
const showVideo = ref(false)
const activeVizTab = ref(0)

// 打字机效果
const fullText = '专为中小微企业打造的一站式碳管理平台，从数据采集到减排优化，AI 全程赋能，让碳中和变得简单高效。'
const typedText = ref('')
const typingDone = ref(false)

// 导航项
const navItems = [
  { id: 'hero', label: '首页' },
  { id: 'features', label: '场景体验' },
  { id: 'capabilities', label: '核心能力' },
  { id: 'ai', label: 'AI顾问' },
  { id: 'viz', label: '可视化' },
  { id: 'pricing', label: '定价' }
]

// 标题行
const titleLines = [
  '让碳管理',
  '<span class="gradient-text">更智能</span>',
  '更简单'
]

// 统计数据
const stats = [
  { value: '500', unit: '+', label: '服务企业', icon: 'OfficeBuilding' },
  { value: '10000', unit: '+', label: '核算次数', icon: 'TrendCharts' },
  { value: '30', unit: '%', label: '平均减排', icon: 'TrendCharts' }
]

// 场景卡片
const sceneCards = [
  { icon: 'Check', text: 'GB/T 32150', class: 'card-cert', style: { top: '10%', left: '5%' } },
  { icon: 'StarFilled', text: 'AI 驱动', class: 'card-ai', style: { top: '20%', right: '10%' } },
  { icon: 'CircleCheck', text: 'ISO 合规', class: 'card-iso', style: { bottom: '30%', left: '0%' } }
]

// 场景化故事
const stories = [
  {
    title: '上传票据，自动识别',
    desc: '小明上传了电费单、燃气账单，OCR 智能识别自动提取关键数据，无需手动录入。',
    features: ['多格式票据支持', '99%+ 识别准确率', '自动数据校验'],
    theme: 'ocr',
    screenshot: './screenshots/step1-ocr.png',
    animElements: [
      { class: 'doc doc-1', style: {} },
      { class: 'doc doc-2', style: {} },
      { class: 'scan-line', style: {} }
    ]
  },
  {
    title: '智能核算，一键生成',
    desc: '系统自动匹配排放因子，完成 Scope 1/2/3 全范围核算，生成符合 GB/T 32150 标准的报告。',
    features: ['生态环境部因子库', '三范围全覆盖', '标准合规报告'],
    theme: 'calc',
    screenshot: './screenshots/step2-report.png',
    animElements: [
      { class: 'calc-screen', style: {} },
      { class: 'data-bar', style: {} },
      { class: 'progress-ring', style: {} }
    ]
  },
  {
    title: '3D可视化，一目了然',
    desc: '通过园区3D地图，小明直观看到各建筑碳排放分布，快速定位高排放区域。',
    features: ['园区地图3D化', '实时数据叠加', '多维度钻取分析'],
    theme: 'viz',
    screenshot: './screenshots/step3-3d.png',
    animElements: [
      { class: 'building-3d', style: {} },
      { class: 'heatmap', style: {} },
      { class: 'data-point', style: {} }
    ]
  },
  {
    title: 'AI顾问，专业建议',
    desc: 'AI 分析数据后，为小明提供了具体的减排方案，预计可降低 20% 碳排放。',
    features: ['自然语言交互', '个性化方案', '效果预测评估'],
    theme: 'ai',
    screenshot: './screenshots/step4-ai.png',
    animElements: [
      { class: 'ai-orb', style: {} },
      { class: 'chat-bubble', style: {} },
      { class: 'suggestion-card', style: {} }
    ]
  }
]

// 功能特性
const features = [
  {
    icon: 'TrendCharts',
    title: '智能碳核算',
    brief: '自动识别排放源，一键生成合规报告',
    detail: '基于 GB/T 32150 标准，支持 Scope 1/2/3 全范围核算，自动匹配生态环境部排放因子库。',
    items: ['OCR票据识别', '智能数据校验', '多维度分析', '标准报告导出'],
    theme: 'blue',
    hovered: false
  },
  {
    icon: 'MapLocation',
    title: '3D园区可视化',
    brief: '上传平面图，一键生成3D场景',
    detail: '将园区地图转化为沉浸式3D场景，直观展示碳排放分布，支持热力图、高度图等多种可视化方式。',
    items: ['平面图3D化', '实时数据叠加', '建筑级钻取', '导出分享'],
    theme: 'purple',
    hovered: false
  },
  {
    icon: 'Cpu',
    title: 'AI智能顾问',
    brief: '24小时在线的碳管理专家',
    detail: '基于大模型技术，提供专业的碳核算咨询、减排方案建议、政策解读等服务。',
    items: ['自然语言问答', '减排方案推荐', '政策标准解读', '碳交易咨询'],
    theme: 'cyan',
    hovered: false
  },
  {
    icon: 'FirstAidKit',
    title: '减排优化',
    brief: '识别减排潜力，制定优化方案',
    detail: 'AI分析碳排放数据，识别减排机会点，生成可执行的减排优化方案并追踪效果。',
    items: ['潜力分析', '方案生成', '效果追踪', '路径规划'],
    theme: 'green',
    hovered: false
  },
  {
    icon: 'Wallet',
    title: '碳资产管理',
    brief: '全生命周期碳资产管理',
    detail: '支持 CCER、VCS、GS、I-REC 等主流碳资产类型，实现资产登记、估值、交易全流程管理。',
    items: ['多类型支持', '实时估值', '交易管理', '资产分析'],
    theme: 'orange',
    hovered: false
  },
  {
    icon: 'Document',
    title: 'ISO标准报告',
    brief: '一键生成国际认证报告',
    detail: '支持 ISO 14064-1 组织碳盘查报告、ISO 14067 产品碳足迹报告，满足国际认证需求。',
    items: ['ISO 14064-1', 'ISO 14067', '自动排版', '多语言导出'],
    theme: 'pink',
    hovered: false
  }
]

// AI对话消息
const chatMessages = ref([
  { type: 'ai', content: '您好！我是碳小智，您的专属碳管理顾问。有什么可以帮助您的吗？', time: '10:00' },
  { type: 'user', content: '我们工厂想降低碳排放，有什么建议？', time: '10:01' },
  { type: 'ai', content: '根据您上月的用电数据，我建议从以下3个方面入手：<br><br>1. <strong>优化能源结构</strong>：增加绿电采购比例，预计可降低 15% Scope 2 排放<br>2. <strong>设备升级</strong>：更换高效电机，投资回收期约 2 年<br>3. <strong>工艺改进</strong>：优化生产排程，减少设备空转时间<br><br>需要我为您生成详细的减排方案吗？', time: '10:02' }
])

// AI能力
const aiCapabilities = ['自然语言交互', 'ISO标准解读', '减排方案推荐', '碳交易咨询', '政策实时更新', '个性化报告']

// 可视化功能
const vizFeatures = [
  { icon: 'MapLocation', title: '园区地图3D化', desc: '上传平面图，AI自动生成3D园区模型', color: 'blue' },
  { icon: 'OfficeBuilding', title: '数字孪生工厂', desc: '实时映射生产流程，碳排放一目了然', color: 'purple' },
  { icon: 'Share', title: '供应链碳图谱', desc: '全链路碳足迹追踪，识别高排放节点', color: 'cyan' },
  { icon: 'Lightning', title: '源网荷储协同', desc: '能源系统优化，提升清洁能源占比', color: 'green' }
]

// 可视化标签
const vizTabs = [
  {
    label: '园区3D',
    scene: 'park',
    screenshot: './screenshots/viz-park.png',
    elements: [
      { class: 'bldg-main', style: {} },
      { class: 'bldg-sub', style: {} },
      { class: 'heatmap-overlay', style: {} }
    ]
  },
  {
    label: '数字孪生',
    scene: 'factory',
    screenshot: './screenshots/viz-factory.png',
    elements: [
      { class: 'factory-line', style: {} },
      { class: 'machine', style: {} },
      { class: 'data-flow', style: {} }
    ]
  },
  {
    label: '供应链',
    scene: 'chain',
    screenshot: './screenshots/viz-chain.png',
    elements: [
      { class: 'node', style: {} },
      { class: 'connection', style: {} },
      { class: 'carbon-label', style: {} }
    ]
  }
]

// 定价方案
const pricingPlans = [
  {
    name: '免费版',
    price: '0',
    cta: '免费开始',
    popular: false,
    features: [
      { text: '基础碳核算（Scope 1/2）', included: true },
      { text: '标准数据报表', included: true },
      { text: 'AI顾问基础问答', included: true },
      { text: '1个企业管理', included: true },
      { text: '3D可视化', included: false },
      { text: 'ISO报告生成', included: false }
    ]
  },
  {
    name: '专业版',
    price: '299',
    cta: '立即升级',
    popular: true,
    features: [
      { text: '全功能碳核算（Scope 1/2/3）', included: true },
      { text: '3D可视化大屏', included: true },
      { text: 'AI顾问高级功能', included: true },
      { text: 'ISO 14064/14067报告', included: true },
      { text: '10个企业管理', included: true },
      { text: '碳资产管理', included: true }
    ]
  },
  {
    name: '企业版',
    price: '定制',
    cta: '联系销售',
    popular: false,
    features: [
      { text: '专业版全部功能', included: true },
      { text: '私有化部署', included: true },
      { text: 'API接口开放', included: true },
      { text: '专属客户成功经理', included: true },
      { text: '定制化开发', included: true },
      { text: 'SLA服务保障', included: true }
    ]
  }
]

// 页脚链接
const footerLinks = [
  { title: '产品', links: [
    { label: '功能特性', slug: 'features' },
    { label: '定价方案', slug: 'pricing' },
    { label: '更新日志', slug: 'changelog' },
    { label: '路线图', slug: 'roadmap' }
  ]},
  { title: '资源', links: [
    { label: '帮助中心', slug: 'help' },
    { label: 'API文档', slug: 'api' },
    { label: '使用指南', slug: 'guide' },
    { label: '案例研究', slug: 'cases' }
  ]},
  { title: '公司', links: [
    { label: '关于我们', slug: 'about' },
    { label: '联系我们', slug: 'contact' },
    { label: '加入我们', slug: 'join' },
    { label: '合作伙伴', slug: 'partners' }
  ]},
  { title: '法律', links: [
    { label: '隐私政策', slug: 'privacy' },
    { label: '服务条款', slug: 'terms' },
    { label: '安全合规', slug: 'compliance' }
  ]}
]

// 3D场景鼠标跟随
const mouseX = ref(0)
const mouseY = ref(0)
const sceneStyle = computed(() => ({
  transform: `perspective(1000px) rotateY(${mouseX.value * 5}deg) rotateX(${-mouseY.value * 5}deg)`
}))

// 打字机效果
const startTyping = () => {
  let i = 0
  const type = () => {
    if (i < fullText.length) {
      typedText.value += fullText.charAt(i)
      i++
      setTimeout(type, 50)
    } else {
      typingDone.value = true
    }
  }
  setTimeout(type, 800)
}

// 粒子系统
const initParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let particles = []
  let animationId
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  class Particle {
    constructor() {
      this.reset()
    }
    reset() {
      this.x = Math.random() * canvas.width
      this.y = Math.random() * canvas.height
      this.size = Math.random() * 3 + 1
      this.speedX = (Math.random() - 0.5) * 0.5
      this.speedY = (Math.random() - 0.5) * 0.5
      this.opacity = Math.random() * 0.5 + 0.2
      this.color = Math.random() > 0.5 ? '#00d4ff' : '#0099ff'
    }
    update() {
      this.x += this.speedX
      this.y += this.speedY
      if (this.x < 0 || this.x > canvas.width) this.speedX *= -1
      if (this.y < 0 || this.y > canvas.height) this.speedY *= -1
    }
    draw() {
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.fillStyle = this.color
      ctx.globalAlpha = this.opacity
      ctx.fill()
    }
  }
  
  for (let i = 0; i < 80; i++) {
    particles.push(new Particle())
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach((p, i) => {
      p.update()
      p.draw()
      
      particles.slice(i + 1).forEach(p2 => {
        const dx = p.x - p2.x
        const dy = p.y - p2.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 100) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = '#00d4ff'
          ctx.globalAlpha = (1 - dist / 100) * 0.15
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      })
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  resize()
  animate()
  window.addEventListener('resize', resize)
  
  return () => {
    cancelAnimationFrame(animationId)
    window.removeEventListener('resize', resize)
  }
}

// 滚动处理
const handleScroll = () => {
  const scrollY = window.scrollY
  navVisible.value = scrollY > 100
  
  // 更新活跃区块
  const sections = ['hero', 'features', 'capabilities', 'ai', 'viz', 'pricing']
  for (const id of sections) {
    const el = document.getElementById(id)
    if (el) {
      const rect = el.getBoundingClientRect()
      if (rect.top < 300 && rect.bottom > 300) {
        activeSection.value = id
        break
      }
    }
  }
}

// 鼠标移动
const handleMouseMove = (e) => {
  mouseX.value = (e.clientX / window.innerWidth - 0.5) * 2
  mouseY.value = (e.clientY / window.innerHeight - 0.5) * 2
}

// 平滑滚动
const scrollToSection = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 路由跳转
const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')

onMounted(() => {
  startTyping()
  const cleanup = initParticles()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('mousemove', handleMouseMove)
  
  onUnmounted(() => {
    cleanup()
    window.removeEventListener('scroll', handleScroll)
    window.removeEventListener('mousemove', handleMouseMove)
  })
})
</script>

<style scoped>
/* ===== 基础样式 ===== */
.landing-page {
  min-height: 100vh;
  background: #0a0a1a;
  color: #fff;
  overflow-x: hidden;
  position: relative;
}

/* ===== 动态背景 ===== */
.bg-layers {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(0, 212, 255, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(0, 153, 255, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(0, 255, 136, 0.05) 0%, transparent 70%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.particle-canvas {
  position: absolute;
  inset: 0;
}

.bg-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%);
  animation: glowPulse 4s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

/* ===== 导航栏 ===== */
.nav-bar {
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
  transform: translateY(-100%);
  transition: all 0.4s ease;
  background: transparent;
}

.nav-bar.nav-visible {
  transform: translateY(0);
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-menu a {
  position: relative;
  padding: 8px 16px;
  color: #a0a0b0;
  text-decoration: none;
  font-size: 14px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-menu a:hover,
.nav-menu a.active {
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
}

.nav-menu a.active .nav-dot {
  opacity: 1;
}

.nav-dot {
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #00d4ff;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.btn-ghost {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-ghost:hover {
  border-color: #00d4ff;
  color: #00d4ff;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
}

/* ===== 英雄区 ===== */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 120px 80px 80px;
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
  font-size: 13px;
  color: #00d4ff;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}

.badge-pulse {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.5); opacity: 0; }
}

.hero-badge .el-icon {
  position: relative;
  z-index: 1;
}

.hero-badge span:last-child {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 24px;
}

.title-line {
  display: block;
  opacity: 0;
  transform: translateY(30px);
  animation: titleSlide 0.8s ease forwards;
}

@keyframes titleSlide {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.gradient-text {
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% 200%;
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-desc {
  font-size: 18px;
  color: #808090;
  line-height: 1.8;
  margin-bottom: 32px;
  min-height: 64px;
}

.typing-text {
  position: relative;
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background: #00d4ff;
  margin-left: 4px;
  animation: cursorBlink 1s step-end infinite;
  vertical-align: middle;
}

@keyframes cursorBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.hero-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  opacity: 0;
  transform: translateY(20px);
  animation: statSlide 0.6s ease forwards;
}

@keyframes statSlide {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: #fff;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.stat-unit {
  font-size: 18px;
  color: #00d4ff;
}

.stat-label {
  font-size: 13px;
  color: #808090;
  margin-top: 4px;
}

.hero-cta {
  display: flex;
  gap: 16px;
}

.btn-magic {
  position: relative;
  padding: 16px 32px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
}

.btn-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 12px;
  transition: all 0.3s;
}

.btn-magic:hover .btn-bg {
  transform: scale(1.05);
  box-shadow: 0 20px 40px rgba(0, 212, 255, 0.4);
}

.btn-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-video {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-video:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.play-icon {
  width: 40px;
  height: 40px;
  background: rgba(0, 212, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00d4ff;
}

/* ===== 3D场景预览 ===== */
.hero-visual {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 1000px;
}

.scene-container {
  position: relative;
  width: 500px;
  height: 500px;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}

.scene-card {
  position: absolute;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  animation: floatCard 4s ease-in-out infinite;
}

.scene-card .card-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #fff;
}

.card-cert { animation-delay: 0s; }
.card-ai { animation-delay: 1s; }
.card-iso { animation-delay: 2s; }

@keyframes floatCard {
  0%, 100% { transform: translateY(0) rotateZ(-2deg); }
  50% { transform: translateY(-15px) rotateZ(2deg); }
}

.floating-island {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 280px;
  height: 280px;
}

.island-base {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 60px;
  background: linear-gradient(180deg, #1a3a4a 0%, #0d1f26 100%);
  border-radius: 50%;
  box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3);
}

.island-buildings {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
}

.bldg {
  position: absolute;
  bottom: 0;
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.4), rgba(0, 153, 255, 0.2));
  border: 1px solid rgba(0, 212, 255, 0.5);
  animation: buildingGlow 3s ease-in-out infinite;
}

.bldg-1 { width: 40px; height: 80px; left: -60px; animation-delay: 0s; }
.bldg-2 { width: 50px; height: 100px; left: -10px; animation-delay: 0.5s; }
.bldg-3 { width: 35px; height: 70px; left: 50px; animation-delay: 1s; }

@keyframes buildingGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
  50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
}

.island-trees {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
}

.tree {
  position: absolute;
  width: 8px;
  height: 20px;
  background: #00ff88;
  border-radius: 4px;
  animation: treeSway 3s ease-in-out infinite;
}

.tree:nth-child(1) { left: -80px; animation-delay: 0s; }
.tree:nth-child(2) { left: 80px; animation-delay: 0.3s; }
.tree:nth-child(3) { left: -40px; height: 15px; animation-delay: 0.6s; }
.tree:nth-child(4) { left: 40px; height: 15px; animation-delay: 0.9s; }
.tree:nth-child(5) { left: 0; height: 12px; animation-delay: 1.2s; }

@keyframes treeSway {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}

.carbon-rings {
  position: absolute;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
}

.ring {
  position: absolute;
  border: 2px solid rgba(0, 255, 136, 0.3);
  border-radius: 50%;
  animation: ringExpand 3s ease-out infinite;
}

.ring:nth-child(1) { width: 60px; height: 60px; left: -30px; top: -30px; }
.ring:nth-child(2) { width: 100px; height: 100px; left: -50px; top: -50px; }
.ring:nth-child(3) { width: 140px; height: 140px; left: -70px; top: -70px; }

@keyframes ringExpand {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.orbit-particles {
  position: absolute;
  inset: 0;
}

.orbit-particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #00d4ff;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  animation: orbit 8s linear infinite;
}

.orbit-particle:nth-child(1) { animation-delay: 0s; }
.orbit-particle:nth-child(2) { animation-delay: 1s; }
.orbit-particle:nth-child(3) { animation-delay: 2s; }
.orbit-particle:nth-child(4) { animation-delay: 3s; }
.orbit-particle:nth-child(5) { animation-delay: 4s; }
.orbit-particle:nth-child(6) { animation-delay: 5s; }
.orbit-particle:nth-child(7) { animation-delay: 6s; }
.orbit-particle:nth-child(8) { animation-delay: 7s; }

@keyframes orbit {
  0% { transform: rotate(0deg) translateX(180px) rotate(0deg); }
  100% { transform: rotate(360deg) translateX(180px) rotate(-360deg); }
}

/* ===== 通用区块标题 ===== */
.section-header {
  text-align: center;
  margin-bottom: 60px;
  padding-top: 80px;
}

.section-tag {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #00d4ff;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 12px;
}

.section-header p {
  font-size: 18px;
  color: #808090;
  max-width: 600px;
  margin: 0 auto;
}

/* ===== 场景化故事区 ===== */
.story-section {
  padding: 60px 80px;
  position: relative;
  z-index: 10;
}

.story-timeline {
  max-width: 1200px;
  margin: 0 auto;
}

.story-card {
  display: flex;
  align-items: center;
  gap: 60px;
  margin-bottom: 100px;
  opacity: 0;
  transform: translateY(40px);
  animation: storySlide 0.8s ease forwards;
}

.story-card:nth-child(1) { animation-delay: 0.1s; }
.story-card:nth-child(2) { animation-delay: 0.2s; }
.story-card:nth-child(3) { animation-delay: 0.3s; }
.story-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes storySlide {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.story-left .story-visual { order: 1; }
.story-left .story-content { order: 2; }
.story-right .story-visual { order: 2; }
.story-right .story-content { order: 1; }

.story-visual {
  flex: 1;
  height: 300px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  position: relative;
  overflow: hidden;
}

.story-screenshot {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.story-screenshot img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.story-content {
  flex: 1;
}

.story-step {
  display: inline-block;
  padding: 6px 14px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}

.story-content h3 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 16px;
}

.story-content > p {
  font-size: 16px;
  color: #a0a0b0;
  line-height: 1.7;
  margin-bottom: 20px;
}

.story-features {
  list-style: none;
  padding: 0;
}

.story-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #c0c0d0;
  margin-bottom: 10px;
}

.story-features li .el-icon {
  color: #00ff88;
}

/* ===== 3D翻转卡片 ===== */
.features-grid-section {
  padding: 60px 80px;
  position: relative;
  z-index: 10;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-flip-card {
  height: 320px;
  perspective: 1000px;
  cursor: pointer;
}

.flip-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-inner.flipped {
  transform: rotateY(180deg);
}

.flip-front,
.flip-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 20px;
  padding: 40px 30px;
  display: flex;
  flex-direction: column;
}

.flip-front {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  align-items: center;
  text-align: center;
}

.flip-back {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 153, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.3);
  transform: rotateY(180deg);
}

.flip-front.blue { --accent: #00d4ff; }
.flip-front.purple { --accent: #a855f7; }
.flip-front.cyan { --accent: #22d3ee; }
.flip-front.green { --accent: #4ade80; }
.flip-front.orange { --accent: #fb923c; }
.flip-front.pink { --accent: #f472b6; }

.feature-icon-wrap {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--accent), transparent);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  color: var(--accent);
}

.flip-front h3 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 12px;
}

.flip-front > p {
  font-size: 14px;
  color: #808090;
  line-height: 1.6;
  margin-bottom: 20px;
}

.flip-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--accent);
  margin-top: auto;
}

.flip-back h4 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #fff;
}

.flip-back > p {
  font-size: 14px;
  color: #a0a0b0;
  line-height: 1.6;
  margin-bottom: 16px;
}

.flip-back ul {
  list-style: none;
  padding: 0;
  margin-top: auto;
}

.flip-back li {
  font-size: 13px;
  color: #c0c0d0;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.flip-back li:last-child {
  border-bottom: none;
}

/* ===== AI顾问区 ===== */
.ai-demo-section {
  padding: 60px 80px;
  position: relative;
  z-index: 10;
}

.ai-container {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1200px;
  margin: 0 auto;
}

.ai-intro {
  flex: 1;
}

.ai-intro h2 {
  font-size: 36px;
  font-weight: 700;
  margin: 16px 0;
}

.ai-intro > p {
  font-size: 16px;
  color: #808090;
  line-height: 1.7;
}

.ai-chat-demo {
  flex: 1;
}

.chat-window {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 24px;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.ai-avatar {
  position: relative;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-pulse {
  position: absolute;
  inset: -4px;
  border: 2px solid rgba(0, 212, 255, 0.3);
  border-radius: 50%;
  animation: avatarPulse 2s ease-in-out infinite;
}

@keyframes avatarPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.ai-info {
  display: flex;
  flex-direction: column;
}

.ai-name {
  font-weight: 600;
}

.ai-status {
  font-size: 12px;
  color: #808090;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #00ff88;
  border-radius: 50%;
  animation: statusBlink 2s ease-in-out infinite;
}

@keyframes statusBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.chat-messages {
  padding: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.message {
  margin-bottom: 16px;
  animation: messageSlide 0.4s ease;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
}

.message.user {
  display: flex;
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.message.ai .message-content {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.message.user .message-content {
  background: rgba(255, 255, 255, 0.1);
}

.message-content strong {
  color: #00ff88;
}

.message-time {
  font-size: 11px;
  color: #505060;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.chat-input input::placeholder {
  color: #505060;
}

.chat-input button {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  border: none;
  border-radius: 12px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.capability-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: #a0a0b0;
}

.capability-tag .el-icon {
  color: #00ff88;
  font-size: 12px;
}

/* ===== 可视化区 ===== */
.viz-section {
  padding: 60px 80px;
  position: relative;
  z-index: 10;
}

.viz-container {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1200px;
  margin: 0 auto;
}

.viz-content {
  flex: 1;
}

.viz-content h2 {
  font-size: 36px;
  font-weight: 700;
  margin: 16px 0;
}

.viz-content > p {
  font-size: 16px;
  color: #808090;
  line-height: 1.7;
  margin-bottom: 32px;
}

.viz-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.viz-feature {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.viz-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.viz-icon.blue { background: rgba(0, 212, 255, 0.1); color: #00d4ff; }
.viz-icon.purple { background: rgba(168, 85, 247, 0.1); color: #a855f7; }
.viz-icon.cyan { background: rgba(34, 211, 238, 0.1); color: #22d3ee; }
.viz-icon.green { background: rgba(74, 222, 128, 0.1); color: #4ade80; }

.viz-text h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.viz-text p {
  font-size: 14px;
  color: #808090;
}

.viz-showcase {
  flex: 1;
}

.viz-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.viz-tabs button {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #808090;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.viz-tabs button.active,
.viz-tabs button:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

.viz-display {
  height: 350px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

.viz-scene {
  position: absolute;
  inset: 0;
}

.viz-screenshot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 20px;
}

/* ===== 定价区 ===== */
.pricing-section {
  padding: 60px 80px;
  position: relative;
  z-index: 10;
}

.pricing-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1100px;
  margin: 0 auto;
}

.pricing-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 40px 30px;
  position: relative;
  transition: all 0.4s;
}

.pricing-card:hover {
  transform: translateY(-10px);
  border-color: rgba(255, 255, 255, 0.15);
}

.pricing-card.popular {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 153, 255, 0.05));
  border-color: rgba(0, 212, 255, 0.3);
  transform: scale(1.05);
}

.pricing-card.popular:hover {
  transform: scale(1.05) translateY(-10px);
}

.pricing-card.popular::before {
  content: '最受欢迎';
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

.plan-header {
  text-align: center;
  margin-bottom: 30px;
}

.plan-header h3 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 16px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.currency {
  font-size: 20px;
  color: #808090;
}

.amount {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.period {
  font-size: 16px;
  color: #808090;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
}

.plan-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  font-size: 14px;
  color: #c0c0d0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.plan-features li.disabled {
  color: #505060;
}

.plan-features li .el-icon {
  font-size: 16px;
}

.plan-features li:not(.disabled) .el-icon {
  color: #00ff88;
}

.pricing-card button {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

/* ===== CTA区 ===== */
.final-cta {
  padding: 120px 80px;
  position: relative;
  z-index: 10;
  text-align: center;
  overflow: hidden;
}

.cta-particles {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%);
}

.cta-content {
  position: relative;
  z-index: 1;
}

.cta-content h2 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-content > p {
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

.btn-large {
  padding: 18px 36px;
  font-size: 17px;
}

.trust-signals {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.trust-signals span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #808090;
}

.trust-signals .el-icon {
  color: #00d4ff;
}

/* ===== 页脚 ===== */
.landing-footer {
  padding: 60px 80px 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 10;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto 40px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-brand .logo-icon {
  width: 48px;
  height: 48px;
}

.brand-name {
  display: block;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #0099ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.footer-brand p {
  font-size: 14px;
  color: #808090;
  margin-top: 4px;
}

.footer-links {
  display: flex;
  gap: 80px;
}

.link-group h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
}

.link-group a {
  display: block;
  font-size: 14px;
  color: #808090;
  text-decoration: none;
  margin-bottom: 10px;
  transition: color 0.3s;
}

.link-group a:hover,
.link-group .footer-link:hover {
  color: #00d4ff;
}

.footer-link {
  display: block;
  font-size: 14px;
  color: #808090;
  text-decoration: none;
  margin-bottom: 10px;
  transition: color 0.3s;
  cursor: pointer;
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-bottom p {
  font-size: 13px;
  color: #505060;
}

/* ===== 视频弹窗 ===== */
.video-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
}

.video-container {
  position: relative;
  width: 80%;
  max-width: 900px;
  aspect-ratio: 16/9;
  background: #1a1a2e;
  border-radius: 20px;
  overflow: hidden;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #808090;
}

.video-placeholder p {
  margin-top: 8px;
  font-size: 14px;
  color: #808090;
}

.video-placeholder h3 {
  margin-top: 16px;
  font-size: 24px;
  font-weight: 600;
  color: #fff;
}

.video-icon {
  color: #00d4ff;
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.video-features {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.video-features span {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #a0a0b0;
}

.video-features .el-icon {
  color: #00ff88;
  font-size: 14px;
}

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .hero {
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
  
  .hero-visual {
    margin-top: 60px;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .pricing-cards {
    grid-template-columns: 1fr;
    max-width: 400px;
  }
  
  .pricing-card.popular {
    transform: none;
  }
  
  .pricing-card.popular:hover {
    transform: translateY(-10px);
  }
  
  .story-card,
  .viz-container,
  .ai-container {
    flex-direction: column;
  }
  
  .story-left .story-visual,
  .story-right .story-visual {
    order: 1;
  }
  
  .story-left .story-content,
  .story-right .story-content {
    order: 2;
  }
}

@media (max-width: 768px) {
  .nav-bar {
    padding: 0 20px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header h2 {
    font-size: 28px;
  }
  
  .trust-signals {
    flex-direction: column;
    gap: 16px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 30px;
  }
}
</style>
