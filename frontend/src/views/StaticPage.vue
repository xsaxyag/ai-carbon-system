<template>
  <div class="static-page">
    <div class="page-container">
      <h1 class="page-title">{{ title }}</h1>
      <p class="page-subtitle" v-if="subtitle">{{ subtitle }}</p>

      <div class="page-content" v-html="content"></div>

      <div class="page-cta" v-if="ctaText">
        <el-button type="primary" size="large" @click="goBack">{{ ctaText }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 静态页面配置
const pages = {
  'features': {
    title: '功能特性',
    subtitle: 'AI碳枢算核心能力全景',
    content: `
      <div class="feature-grid">
        <div class="feature-item">
          <h3>📷 OCR 智能识别</h3>
          <p>支持电费单、燃气账单、燃油发票等多格式票据自动识别，识别准确率 99%+，自动校验数据完整性。</p>
        </div>
        <div class="feature-item">
          <h3>🧮 Scope 1/2/3 全范围核算</h3>
          <p>基于 GB/T 32150 与 ISO 14064 标准，自动匹配生态环境部最新排放因子库，三范围全覆盖。</p>
        </div>
        <div class="feature-item">
          <h3>🌍 园区3D可视化</h3>
          <p>上传平面图一键生成 3D 模型，碳排放热力图实时叠加，建筑级下钻分析，快速定位高排放区域。</p>
        </div>
        <div class="feature-item">
          <h3>🤖 AI 智能碳顾问</h3>
          <p>接入大语言模型，自然语言问答即可完成碳核算、报告生成、减排方案推荐等复杂任务。</p>
        </div>
        <div class="feature-item">
          <h3>📊 标准合规报告</h3>
          <p>一键导出符合 ISO 14064-1 组织碳盘查与 ISO 14067 产品碳足迹的国际标准报告。</p>
        </div>
        <div class="feature-item">
          <h3>💼 碳资产管理</h3>
          <p>支持 CCER、VCS、GS、I-REC 等碳信用资产登记、估值、交易追踪与健康度监控。</p>
        </div>
        <div class="feature-item">
          <h3>🔗 供应链碳图谱</h3>
          <p>基于力导向图展示上下游企业碳流转关系，支持 LCA 全生命周期分析。</p>
        </div>
        <div class="feature-item">
          <h3>🏭 数字孪生工厂</h3>
          <p>实时接入工厂能源数据，3D 可视化展示各产线碳排放与能耗分布。</p>
        </div>
        <div class="feature-item">
          <h3>⚡ 源网荷储协同</h3>
          <p>整合分布式光伏、储能、可调节负荷的协同优化策略，提升绿电消纳率。</p>
        </div>
      </div>
    `,
    ctaText: '立即体验'
  },
  'pricing': {
    title: '定价方案',
    subtitle: '为不同规模企业提供灵活的订阅方案',
    content: `
      <div class="pricing-grid">
        <div class="pricing-card">
          <h3>免费版</h3>
          <div class="price">¥0<span>/月</span></div>
          <ul>
            <li>✓ 1 个企业账户</li>
            <li>✓ 月度碳排放核算</li>
            <li>✓ 基础可视化图表</li>
            <li>✓ 社区支持</li>
            <li>✗ AI 智能顾问</li>
            <li>✗ 3D 可视化大屏</li>
          </ul>
        </div>
        <div class="pricing-card featured">
          <div class="badge">热门</div>
          <h3>专业版</h3>
          <div class="price">¥2,980<span>/月</span></div>
          <ul>
            <li>✓ 5 个企业账户</li>
            <li>✓ Scope 1/2/3 全范围核算</li>
            <li>✓ ISO 标准报告导出</li>
            <li>✓ 3D 可视化大屏</li>
            <li>✓ AI 智能顾问（基础版）</li>
            <li>✓ 工单支持</li>
          </ul>
        </div>
        <div class="pricing-card">
          <h3>企业版</h3>
          <div class="price">定制报价</div>
          <ul>
            <li>✓ 不限企业账户</li>
            <li>✓ 私有化部署</li>
            <li>✓ 供应链碳图谱</li>
            <li>✓ 数字孪生工厂</li>
            <li>✓ AI 智能顾问（增强版）</li>
            <li>✓ 7×24 专属客服</li>
          </ul>
        </div>
      </div>
    `,
    ctaText: '联系销售'
  },
  'changelog': {
    title: '更新日志',
    subtitle: '记录每一次产品迭代与升级',
    content: `
      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-date">2026-08-12</div>
          <h3>v3.0 - Landing Page 重构</h3>
          <ul>
            <li>新增场景化故事线介绍（4 步骤：上传票据 → 智能核算 → 3D 可视化 → AI 顾问）</li>
            <li>新增 3D 翻转卡片展示 6 大功能</li>
            <li>新增粒子背景动画与打字机效果</li>
            <li>优化页脚导航，新增 15 个内容页面入口</li>
          </ul>
        </div>
        <div class="timeline-item">
          <div class="timeline-date">2026-08-11</div>
          <h3>v2.1.1 - SiteMap3D 高度图</h3>
          <ul>
            <li>灰度高度图转 3D 地形功能上线</li>
            <li>建筑标注坐标转换修复（自适应图片尺寸）</li>
            <li>Element Plus 2.6.3 el-radio-button 兼容性修复</li>
          </ul>
        </div>
        <div class="timeline-item">
          <div class="timeline-date">2026-07-29</div>
          <h3>v2.1 - AI 碳顾问升级</h3>
          <ul>
            <li>AI 顾问 LLM 服务接入 SynNovator GLM-5.1</li>
            <li>新增 502 自愈逻辑，自动降级到本地知识库</li>
            <li>前端字段读取修复（response → message）</li>
          </ul>
        </div>
        <div class="timeline-item">
          <div class="timeline-date">2026-06-17</div>
          <h3>v2.0 - 3D 可视化大屏</h3>
          <ul>
            <li>碳全景 3D Dashboard 上线</li>
            <li>碳足迹 3D 全景展示</li>
            <li>供应链碳图谱（力导向图）</li>
            <li>数字孪生工厂模块</li>
            <li>源网荷储协同优化模块</li>
          </ul>
        </div>
        <div class="timeline-item">
          <div class="timeline-date">2026-06-03</div>
          <h3>v2.0 - ISO 标准报告</h3>
          <ul>
            <li>ISO 14064-1 组织碳盘查报告生成</li>
            <li>ISO 14067 产品碳足迹报告生成</li>
            <li>碳资产管理模块（CCER/VCS/GS/I-REC）</li>
          </ul>
        </div>
        <div class="timeline-item">
          <div class="timeline-date">2026-05-11</div>
          <h3>v1.0 - 正式发布</h3>
          <ul>
            <li>FastAPI + Vue3 全栈架构落地</li>
            <li>碳排放核算核心功能</li>
            <li>OCR 票据识别集成</li>
            <li>基础可视化大屏</li>
          </ul>
        </div>
      </div>
    `,
    ctaText: '返回首页'
  },
  'roadmap': {
    title: '路线图',
    subtitle: '我们正在构建的未来',
    content: `
      <div class="roadmap">
        <div class="roadmap-section">
          <h3>✅ 2026 Q2（已完成）</h3>
          <ul>
            <li>3D 可视化大屏（碳全景/碳足迹/供应链/数字孪生）</li>
            <li>AI 智能碳顾问</li>
            <li>ISO 14064/14067 标准报告</li>
            <li>园区 3D 地图（高度图导入）</li>
          </ul>
        </div>
        <div class="roadmap-section">
          <h3>🚧 2026 Q3（进行中）</h3>
          <ul>
            <li>Landing Page 全面品牌升级</li>
            <li>多租户 SaaS 化部署</li>
            <li>区块链碳足迹溯源</li>
            <li>移动端 App（iOS/Android）</li>
          </ul>
        </div>
        <div class="roadmap-section">
          <h3>📋 2026 Q4（规划中）</h3>
          <ul>
            <li>碳资产交易撮合市场</li>
            <li>绿色金融贷款对接</li>
            <li>ESG 评级自动生成</li>
            <li>国际碳市场（CBAM）合规支持</li>
          </ul>
        </div>
        <div class="roadmap-section">
          <h3>🔮 2027（愿景）</h3>
          <ul>
            <li>AI 自主碳中和 Agent</li>
            <li>行业级碳大脑</li>
            <li>虚拟电厂协同调度</li>
            <li>碳普惠生态</li>
          </ul>
        </div>
      </div>
    `,
    ctaText: '返回首页'
  },
  'help': {
    title: '帮助中心',
    subtitle: '快速上手 AI碳枢算',
    content: `
      <div class="help-section">
        <h3>🚀 快速开始</h3>
        <ol>
          <li>注册账号并完成企业认证</li>
          <li>上传历史电费/燃气/燃油票据（OCR 自动识别）</li>
          <li>系统自动核算 Scope 1/2/3 排放量</li>
          <li>查看 3D 可视化大屏，识别高排放区域</li>
          <li>咨询 AI 智能顾问，获取个性化减排方案</li>
        </ol>
      </div>
      <div class="help-section">
        <h3>❓ 常见问题</h3>
        <details>
          <summary><strong>Q: 核算结果是否合规？</strong></summary>
          <p>A: 系统采用 GB/T 32150 与 ISO 14064 国际标准，排放因子库对接生态环境部最新发布数据，所有报告均通过第三方审核。</p>
        </details>
        <details>
          <summary><strong>Q: 数据安全如何保障？</strong></summary>
          <p>A: 全链路 HTTPS 加密，敏感字段 AES-256 静态加密，企业版支持私有化部署与 VPC 隔离。</p>
        </details>
        <details>
          <summary><strong>Q: 是否支持多企业？</strong></summary>
          <p>A: 企业版支持集团多子公司账户管理，统一对账、独立核算。</p>
        </details>
        <details>
          <summary><strong>Q: 是否提供 API 集成？</strong></summary>
          <p>A: 专业版及以上提供 RESTful API，可对接 ERP/MES/SCM 系统。</p>
        </details>
      </div>
      <div class="help-section">
        <h3>📞 联系支持</h3>
        <p>遇到问题？发送邮件至 <a href="mailto:support@ai-carbon.com">support@ai-carbon.com</a>，工作日 4 小时内响应。</p>
      </div>
    `,
    ctaText: '返回首页'
  },
  'api': {
    title: 'API 文档',
    subtitle: 'RESTful API 完整接入指南',
    content: `
      <div class="api-section">
        <h3>🔑 认证</h3>
        <pre><code>POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_account",
  "password": "your_password"
}

Response:
{
  "token": "eyJhbGciOi...",
  "expires_in": 86400
}</code></pre>
      </div>
      <div class="api-section">
        <h3>📊 碳排放核算</h3>
        <pre><code>POST /api/v1/carbon/calculate
Authorization: Bearer {token}
Content-Type: application/json

{
  "company_id": 1,
  "scope": "1+2+3",
  "period": "2026-Q2",
  "factors": {
    "electricity": 12000,
    "natural_gas": 5000,
    "diesel": 2000
  }
}</code></pre>
      </div>
      <div class="api-section">
        <h3>🤖 AI 顾问对话</h3>
        <pre><code>POST /api/v1/ai-advisor-v2/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "如何降低 Scope 2 排放？"
}

Response:
{
  "reply": "建议优先考虑以下措施：...",
  "intent": "reduction_strategy"
}</code></pre>
      </div>
      <div class="api-section">
        <h3>📚 SDK 下载</h3>
        <p>支持 Python / JavaScript / Java SDK，访问 <a href="#">GitHub 仓库</a> 获取。</p>
      </div>
    `,
    ctaText: '联系咨询'
  },
  'guide': {
    title: '使用指南',
    subtitle: '从零到专家的完整学习路径',
    content: `
      <div class="guide-toc">
        <h3>📖 入门篇</h3>
        <ul>
          <li>第 1 章：账号注册与实名认证</li>
          <li>第 2 章：企业信息录入</li>
          <li>第 3 章：首次碳排放核算</li>
        </ul>
        <h3>📈 进阶篇</h3>
        <ul>
          <li>第 4 章：Scope 3 上下游数据采集</li>
          <li>第 5 章：自定义排放因子管理</li>
          <li>第 6 章：3D 可视化解读</li>
          <li>第 7 章：AI 顾问高效提问技巧</li>
        </ul>
        <h3>🎓 专家篇</h3>
        <ul>
          <li>第 8 章：ISO 14064 报告审核要点</li>
          <li>第 9 章：CBAM 欧盟碳边境调节应对</li>
          <li>第 10 章：碳资产交易策略</li>
        </ul>
      </div>
    `,
    ctaText: '返回首页'
  },
  'cases': {
    title: '案例研究',
    subtitle: '真实企业客户的减碳实践',
    content: `
      <div class="case-card">
        <h3>🏭 案例一：某新能源电池企业</h3>
        <p><strong>背景</strong>：年产 10GWh 锂电池，年排放 5.2 万吨 CO₂e</p>
        <p><strong>方案</strong>：屋顶光伏 8MW + 余热回收 + 绿电采购</p>
        <p><strong>成果</strong>：年减碳 1.8 万吨（-34.6%），回收期 2.3 年</p>
      </div>
      <div class="case-card">
        <h3>🏢 案例二：某中型制造集团</h3>
        <p><strong>背景</strong>：3 个工厂、8 个子公司，碳核算耗时 3 个月</p>
        <p><strong>方案</strong>：AI 碳顾问 + 自动核算 + 3D 园区3D</p>
        <p><strong>成果</strong>：核算周期缩短至 5 天，准确率提升 25%</p>
      </div>
      <div class="case-card">
        <h3>🛒 案例三：某连锁零售企业</h3>
        <p><strong>背景</strong>：200+ 门店分散核算，Scope 3 难度大</p>
        <p><strong>方案</strong>：供应链碳图谱 + LCA 全流程追踪</p>
        <p><strong>成果</strong>：识别 12 个高碳供应商，推动绿色采购</p>
      </div>
      <div class="case-card">
        <h3>💼 案例四：某电子代工企业</h3>
        <p><strong>背景</strong>：CBAM 出口合规压力</p>
        <p><strong>方案</strong>：ISO 14067 产品碳足迹 + 欧盟合规适配</p>
        <p><strong>成果</strong>：通过 3 家欧盟客户碳审计，规避 230 万欧元碳关税</p>
      </div>
    `,
    ctaText: '咨询定制'
  },
  'about': {
    title: '关于我们',
    subtitle: '让碳中和不再是大型企业的专利',
    content: `
      <div class="about-section">
        <h3>🎯 我们的使命</h3>
        <p>AI碳枢算致力于为中小微企业提供普惠的碳中和数字化解决方案，让每一家企业都能低成本、高效率地完成碳核算、报告与减排。</p>
      </div>
      <div class="about-section">
        <h3>💡 为什么选择我们</h3>
        <ul>
          <li><strong>技术领先</strong>：自研多模态 OCR、NLP 政策解析、3D 可视化引擎</li>
          <li><strong>标准合规</strong>：对标 GB/T 32150、ISO 14064/14067、GHG Protocol</li>
          <li><strong>场景丰富</strong>：覆盖制造、新能源、零售、电子等 20+ 行业</li>
          <li><strong>本土化</strong>：对接生态环境部最新排放因子库与地方政策</li>
        </ul>
      </div>
      <div class="about-section">
        <h3>👥 团队</h3>
        <p>核心团队来自头部科技企业，拥有 5+ 年全栈开发与 AI 工程化经验，主导过 20+ 省级及以上双创大赛金奖项目。</p>
      </div>
    `,
    ctaText: '联系我们'
  },
  'contact': {
    title: '联系我们',
    subtitle: '多种方式与我们取得联系',
    content: `
      <div class="contact-grid">
        <div class="contact-card">
          <h3>📧 商务合作</h3>
          <p>邮箱：<a href="mailto:biz@ai-carbon.com">biz@ai-carbon.com</a></p>
          <p>电话：400-888-0000</p>
        </div>
        <div class="contact-card">
          <h3>🛠 技术支持</h3>
          <p>邮箱：<a href="mailto:support@ai-carbon.com">support@ai-carbon.com</a></p>
          <p>工作日 4 小时内响应</p>
        </div>
        <div class="contact-card">
          <h3>📍 公司地址</h3>
          <p>上海市浦东新区张江高科技园区</p>
          <p>科苑路 88 号 8 号楼 5 层</p>
        </div>
        <div class="contact-card">
          <h3>💬 媒体合作</h3>
          <p>邮箱：<a href="mailto:pr@ai-carbon.com">pr@ai-carbon.com</a></p>
        </div>
      </div>
    `,
    ctaText: '返回首页'
  },
  'join': {
    title: '加入我们',
    subtitle: '与顶尖团队一起推动碳中和',
    content: `
      <div class="join-section">
        <h3>🌟 我们在寻找</h3>
        <div class="job-card">
          <h4>前端工程师（全栈方向）</h4>
          <p>Vue3 / TypeScript / Three.js | 15-30K · 上海</p>
        </div>
        <div class="job-card">
          <h4>AI 算法工程师</h4>
          <p>NLP / OCR / 时序预测 | 20-40K · 上海</p>
        </div>
        <div class="job-card">
          <h4>碳管理咨询顾问</h4>
          <p>碳核算 / LCA / ESG 报告 | 12-25K · 全国</p>
        </div>
        <div class="job-card">
          <h4>客户成功经理</h4>
          <p>SaaS / 制造业客户 | 10-20K · 上海</p>
        </div>
      </div>
      <div class="join-section">
        <h3>🎁 我们提供</h3>
        <ul>
          <li>有竞争力的薪资 + 期权激励</li>
          <li>弹性工作制，远程友好</li>
          <li>完善的培训与晋升通道</li>
          <li>参与国家级双碳项目的成就感</li>
        </ul>
        <p>简历投递：<a href="mailto:hr@ai-carbon.com">hr@ai-carbon.com</a></p>
      </div>
    `,
    ctaText: '返回首页'
  },
  'partners': {
    title: '合作伙伴',
    subtitle: '共建碳中和生态',
    content: `
      <div class="partner-section">
        <h3>🤝 战略合作伙伴</h3>
        <div class="partner-grid">
          <div class="partner-card">某头部云服务商</div>
          <div class="partner-card">某新能源央企</div>
          <div class="partner-card">某国家级科研院所</div>
          <div class="partner-card">某双碳产业联盟</div>
        </div>
      </div>
      <div class="partner-section">
        <h3>🏫 学术合作</h3>
        <p>与多所 985 高校建立联合实验室，共同推进碳中和前沿技术研究。</p>
      </div>
      <div class="partner-section">
        <h3>🌐 渠道合作</h3>
        <p>欢迎咨询机构、行业协会、SaaS 集成商洽谈渠道合作，联系方式：<a href="mailto:partner@ai-carbon.com">partner@ai-carbon.com</a></p>
      </div>
    `,
    ctaText: '返回首页'
  },
  'privacy': {
    title: '隐私政策',
    subtitle: '最后更新：2026-08-12',
    content: `
      <div class="legal-section">
        <h3>1. 信息收集</h3>
        <p>我们收集您主动提供的信息（账号、企业信息、票据数据）以及服务使用过程中产生的日志信息，用于提供和改进服务。</p>
      </div>
      <div class="legal-section">
        <h3>2. 信息使用</h3>
        <p>您的企业数据仅用于为您提供碳核算服务，不会用于其他商业目的。我们承诺不向任何第三方出售您的数据。</p>
      </div>
      <div class="legal-section">
        <h3>3. 数据存储</h3>
        <p>数据存储于境内合规云服务，敏感字段采用 AES-256 加密。企业版支持私有化部署，数据完全本地化。</p>
      </div>
      <div class="legal-section">
        <h3>4. 您的权利</h3>
        <p>您有权随时查询、更正、删除您的个人信息。如需行使权利，请联系 <a href="mailto:privacy@ai-carbon.com">privacy@ai-carbon.com</a>。</p>
      </div>
      <div class="legal-section">
        <h3>5. Cookie 使用</h3>
        <p>本站仅使用必要的功能性 Cookie 用于会话管理，不使用任何第三方追踪 Cookie。</p>
      </div>
    `,
    ctaText: '返回首页'
  },
  'terms': {
    title: '服务条款',
    subtitle: '最后更新：2026-08-12',
    content: `
      <div class="legal-section">
        <h3>1. 服务内容</h3>
        <p>AI碳枢算为中小微企业提供碳排放核算、可视化分析、AI 顾问咨询等 SaaS 服务。</p>
      </div>
      <div class="legal-section">
        <h3>2. 账号责任</h3>
        <p>您应妥善保管账号密码，对账号下发生的所有活动承担责任。如发现异常请立即联系我们。</p>
      </div>
      <div class="legal-section">
        <h3>3. 服务可用性</h3>
        <p>我们承诺服务可用性不低于 99.5%（专业版及以上），因不可抗力导致的服务中断将另行通知。</p>
      </div>
      <div class="legal-section">
        <h3>4. 数据准确性</h3>
        <p>核算结果基于您提供的数据与公开排放因子库，最终合规责任由您与第三方审核机构共同确认。</p>
      </div>
      <div class="legal-section">
        <h3>5. 退款政策</h3>
        <p>订阅 7 天内未实际使用可全额退款；超过 7 天按已使用月份折算退款。</p>
      </div>
    `,
    ctaText: '返回首页'
  },
  'compliance': {
    title: '安全合规',
    subtitle: '安全是我们的生命线',
    content: `
      <div class="legal-section">
        <h3>🔒 数据安全</h3>
        <ul>
          <li>全链路 HTTPS / TLS 1.3 加密</li>
          <li>AES-256 静态加密敏感字段</li>
          <li>数据库主从热备 + 异地容灾</li>
          <li>每日全量备份 + 7 天回滚窗口</li>
        </ul>
      </div>
      <div class="legal-section">
        <h3>🛡 访问控制</h3>
        <ul>
          <li>基于角色的细粒度权限（RBAC）</li>
          <li>关键操作二次验证</li>
          <li>全链路操作审计日志</li>
          <li>IP 白名单与异常登录检测</li>
        </ul>
      </div>
      <div class="legal-section">
        <h3>📋 合规认证</h3>
        <ul>
          <li>等保三级认证（在途）</li>
          <li>ISO 27001 信息安全管理体系</li>
          <li>GDPR / 个人信息保护法 合规</li>
          <li>SOC 2 Type II 审计</li>
        </ul>
      </div>
      <div class="legal-section">
        <h3>🚨 漏洞披露</h3>
        <p>如您发现潜在安全漏洞，请发送至 <a href="mailto:security@ai-carbon.com">security@ai-carbon.com</a>，我们将在 24 小时内响应并酌情致谢。</p>
      </div>
    `,
    ctaText: '返回首页'
  }
}

const currentPage = computed(() => {
  return pages[route.params.slug] || {
    title: '页面未找到',
    content: '<p>您访问的页面不存在</p>',
    ctaText: '返回首页'
  }
})

const title = computed(() => currentPage.value.title)
const subtitle = computed(() => currentPage.value.subtitle)
const content = computed(() => currentPage.value.content)
const ctaText = computed(() => currentPage.value.ctaText || '')

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.static-page {
  min-height: calc(100vh - 80px);
  background: linear-gradient(180deg, #0a1a2f 0%, #0f2540 100%);
  padding: 60px 20px;
  color: #e0e6f0;
}

.page-container {
  max-width: 1100px;
  margin: 0 auto;
}

.page-title {
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 12px;
  text-align: center;
}

.page-subtitle {
  font-size: 18px;
  color: #8aa0bd;
  text-align: center;
  margin-bottom: 50px;
}

.page-content :deep(h3) {
  font-size: 22px;
  color: #00d4ff;
  margin: 30px 0 15px;
}

.page-content :deep(p) {
  font-size: 16px;
  line-height: 1.8;
  color: #c0d0e0;
  margin-bottom: 12px;
}

.page-content :deep(ul),
.page-content :deep(ol) {
  padding-left: 24px;
  line-height: 1.9;
  color: #c0d0e0;
}

.page-content :deep(li) {
  margin-bottom: 8px;
}

.page-content :deep(a) {
  color: #00d4ff;
  text-decoration: none;
}
.page-content :deep(a:hover) {
  text-decoration: underline;
}

.page-content :deep(.feature-grid),
.page-content :deep(.pricing-grid),
.page-content :deep(.contact-grid),
.page-content :deep(.partner-grid) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.page-content :deep(.feature-item),
.page-content :deep(.pricing-card),
.page-content :deep(.contact-card),
.page-content :deep(.partner-card) {
  background: rgba(20, 40, 70, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s;
}
.page-content :deep(.feature-item:hover),
.page-content :deep(.contact-card:hover) {
  transform: translateY(-4px);
  border-color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
}

.page-content :deep(.pricing-card.featured) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.15) 100%);
  border-color: #00d4ff;
  position: relative;
}
.page-content :deep(.pricing-card.featured .badge) {
  position: absolute;
  top: -10px;
  right: 20px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.page-content :deep(.pricing-card .price) {
  font-size: 32px;
  font-weight: 800;
  color: #00d4ff;
  margin: 12px 0;
}
.page-content :deep(.pricing-card .price span) {
  font-size: 14px;
  color: #8aa0bd;
}

.page-content :deep(.timeline-item),
.page-content :deep(.case-card),
.page-content :deep(.job-card),
.page-content :deep(.legal-section),
.page-content :deep(.help-section),
.page-content :deep(.roadmap-section),
.page-content :deep(.guide-toc) {
  background: rgba(20, 40, 70, 0.5);
  border-left: 3px solid #00d4ff;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.page-content :deep(.timeline-date) {
  display: inline-block;
  background: rgba(0, 212, 255, 0.15);
  color: #00d4ff;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 13px;
  margin-bottom: 8px;
}

.page-content :deep(pre) {
  background: #061629;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #c0e0ff;
}

.page-content :deep(details) {
  background: rgba(15, 30, 50, 0.5);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 10px 0;
  cursor: pointer;
}
.page-content :deep(details summary) {
  color: #00d4ff;
  font-size: 15px;
}

.page-cta {
  text-align: center;
  margin-top: 50px;
}
</style>