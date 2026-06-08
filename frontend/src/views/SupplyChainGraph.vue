<template>
  <div class="supply-chain-graph">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载供应链数据...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <el-alert :title="error" type="error" show-icon :closable="false" />
    </div>

    <div v-show="!loading" class="main-layout">
      <!-- 左侧：控制面板 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><Setting /></el-icon> 控制面板</span>
        </div>

        <!-- 搜索企业 -->
        <div class="control-section">
          <div class="section-label">搜索企业</div>
          <el-input
            v-model="searchKeyword"
            placeholder="输入企业名称..."
            size="small"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 筛选条件 -->
        <div class="control-section">
          <div class="section-label">筛选条件</div>
          <el-select
            v-model="filterRisk"
            placeholder="风险等级"
            size="small"
            style="width: 100%; margin-bottom: 8px;"
            @change="handleFilter"
          >
            <el-option label="全部" value="" />
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
          <el-select
            v-model="filterCarbonIntensity"
            placeholder="碳强度"
            size="small"
            style="width: 100%;"
            @change="handleFilter"
          >
            <el-option label="全部" value="" />
            <el-option label="低碳(&lt;50)" value="low" />
            <el-option label="中碳(50-100)" value="medium" />
            <el-option label="高碳(&gt;100)" value="high" />
          </el-select>
        </div>

        <!-- 图例说明 -->
        <div class="control-section">
          <div class="section-label">图例说明</div>
          <div class="legend-list">
            <div class="legend-item">
              <div class="legend-dot" style="background: #00d4aa;"></div>
              <span>核心企业</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #1890ff;"></div>
              <span>一级供应商</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #f39c12;"></div>
              <span>二级供应商</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #ff4d4f;"></div>
              <span>高风险节点</span>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="control-section">
          <div class="section-label">网络统计</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ networkStats.totalNodes }}</div>
              <div class="stat-label">节点总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ networkStats.totalLinks }}</div>
              <div class="stat-label">连接数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ networkStats.avgCarbonIntensity }}</div>
              <div class="stat-label">平均碳强度</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ networkStats.highRiskNodes }}</div>
              <div class="stat-label">高风险节点</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央3D力导向图 -->
      <div class="center-3d">
        <div ref="threeContainer" class="three-container"></div>

        <!-- 悬浮信息 -->
        <div v-if="hoveredNode" class="hover-info">
          <div class="hover-title">{{ hoveredNode.name }}</div>
          <div class="hover-data">
            <div>排放量: {{ hoveredNode.emission }} tCO₂e</div>
            <div>碳足迹: {{ hoveredNode.carbonFootprint }} kgCO₂e/万元</div>
            <div>风险等级:
              <span :style="{ color: getRiskColor(hoveredNode.riskLevel) }">
                {{ getRiskLabel(hoveredNode.riskLevel) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 操作提示 -->
        <div class="scene-hint">
          <el-icon><InfoFilled /></el-icon>
          鼠标拖拽旋转 | 滚轮缩放 | 点击节点展开子树 | 拖拽节点调整位置
        </div>
      </div>

      <!-- 右侧：减排路径推荐 -->
      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><Promotion /></el-icon> 碳减排路径推荐</span>
        </div>

        <div class="recommendation-list">
          <div
            v-for="(item, idx) in recommendations"
            :key="idx"
            class="recommendation-item"
            :class="{ expanded: expandedRecommendation === idx }"
            @click="toggleRecommendation(idx)"
          >
            <div class="rec-header">
              <div class="rec-priority" :class="'priority-' + item.priority">{{ item.priority }}</div>
              <div class="rec-title">{{ item.title }}</div>
              <div class="rec-arrow">
                <el-icon><ArrowDown /></el-icon>
              </div>
            </div>
            <div v-if="expandedRecommendation === idx" class="rec-content">
              <div class="rec-description">{{ item.description }}</div>
              <div class="rec-meta">
                <div class="meta-item">
                  <span class="meta-label">预计减碳</span>
                  <span class="meta-value" style="color: #00d4aa;">{{ item.reduction }} tCO₂e</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">投资成本</span>
                  <span class="meta-value">{{ item.cost }} 万元</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">回收期</span>
                  <span class="meta-value">{{ item.payback }} 年</span>
                </div>
              </div>
              <div class="rec-actions">
                <el-button type="primary" size="small" @click.stop="applyRecommendation(item)">
                  应用方案
                </el-button>
                <el-button size="small" @click.stop="saveRecommendation(item)">
                  保存
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 供应商列表 -->
        <div class="panel-header" style="margin-top: 16px;">
          <span class="panel-title"><el-icon><List /></el-icon> 供应商列表</span>
        </div>
        <div class="supplier-list">
          <div
            v-for="supplier in suppliers"
            :key="supplier.id"
            class="supplier-item"
            @click="focusOnNode(supplier.id)"
          >
            <div class="supplier-name">{{ supplier.name }}</div>
            <div class="supplier-meta">
              <span class="supplier-emission">{{ supplier.emission }} tCO₂e</span>
              <span class="supplier-risk" :style="{ color: getRiskColor(supplier.riskLevel) }">
                {{ getRiskLabel(supplier.riskLevel) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import { Setting, Search, InfoFilled, Promotion, List, ArrowDown } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import * as THREE from 'three'
import { createThreeScene } from '../utils/three-scene.js'

// 状态
const loading = ref(true)
const error = ref('')
const searchKeyword = ref('')
const filterRisk = ref('')
const filterCarbonIntensity = ref('')
const hoveredNode = ref(null)
const selectedNode = ref(null)
const expandedRecommendation = ref(-1)

// DOM引用
const threeContainer = ref(null)

// 3D场景
let threeSceneObj = null
let forceGraphGroup = null
let networkData = null  // 存储API数据

// 数据
const networkStats = ref({
  totalNodes: 0,
  totalLinks: 0,
  avgCarbonIntensity: 0,
  highRiskNodes: 0
})

const recommendations = ref([
  {
    priority: 1,
    title: '优化运输路线，优先选择铁路/海运',
    description: '通过优化供应链物流网络，将30%的公路运输转为铁路或海运，可显著降低Scope 3排放。建议与物流服务商重新谈判合同，纳入碳排放条款。',
    reduction: 1250,
    cost: 85,
    payback: 2.5
  },
  {
    priority: 2,
    title: '要求一级供应商使用绿电',
    description: '对碳强度排名前20%的供应商，要求其承诺在12个月内使用50%以上绿电。可提供技术支持或联合采购绿电方案。',
    reduction: 3200,
    cost: 150,
    payback: 1.8
  },
  {
    priority: 3,
    title: '替换高碳原材料供应商',
    description: '识别并替换碳足迹最高的5家原材料供应商，转向提供低碳认证的供应商。预计可增加5-8%的采购成本，但可提升产品ESG评级。',
    reduction: 2100,
    cost: 120,
    payback: 3.2
  },
  {
    priority: 4,
    title: '建立供应商碳管理平台',
    description: '部署数字化碳管理平台，实现供应商碳排放数据自动采集、核算和预警。平台可集成现有ERP系统，减少人工核算工作量80%。',
    reduction: 580,
    cost: 65,
    payback: 1.2
  }
])

const suppliers = ref([
  { id: 1, name: '宝钢股份', emission: 12500, riskLevel: 'medium' },
  { id: 2, name: '中石化', emission: 18200, riskLevel: 'high' },
  { id: 3, name: '比亚迪电池', emission: 8500, riskLevel: 'low' },
  { id: 4, name: '宁德时代', emission: 9200, riskLevel: 'low' },
  { id: 5, name: '万华化学', emission: 15600, riskLevel: 'high' },
  { id: 6, name: '格力电器', emission: 6800, riskLevel: 'medium' },
  { id: 7, name: '华为技术', emission: 4200, riskLevel: 'low' },
  { id: 8, name: '阿里巴巴', emission: 3800, riskLevel: 'low' }
])

// 模拟网络数据
const mockNetworkData = {
  nodes: [
    { id: 0, name: '本企业', type: 'core', emission: 5800, carbonFootprint: 42.5, riskLevel: 'low', x: 0, y: 0, z: 0 },
    { id: 1, name: '宝钢股份', type: 'tier1', emission: 12500, carbonFootprint: 89.2, riskLevel: 'medium', x: -30, y: 10, z: -20 },
    { id: 2, name: '中石化', type: 'tier1', emission: 18200, carbonFootprint: 125.6, riskLevel: 'high', x: 35, y: 5, z: -15 },
    { id: 3, name: '比亚迪电池', type: 'tier1', emission: 8500, carbonFootprint: 38.4, riskLevel: 'low', x: -20, y: -5, z: 25 },
    { id: 4, name: '宁德时代', type: 'tier1', emission: 9200, carbonFootprint: 41.8, riskLevel: 'low', x: 25, y: -10, z: 20 },
    { id: 5, name: '万华化学', type: 'tier2', emission: 15600, carbonFootprint: 98.7, riskLevel: 'high', x: -40, y: 15, z: 30 },
    { id: 6, name: '格力电器', type: 'tier2', emission: 6800, carbonFootprint: 52.3, riskLevel: 'medium', x: 40, y: -15, z: -30 },
    { id: 7, name: '华为技术', type: 'tier2', emission: 4200, carbonFootprint: 28.9, riskLevel: 'low', x: 10, y: 20, z: -40 },
    { id: 8, name: '阿里巴巴', type: 'tier3', emission: 3800, carbonFootprint: 22.5, riskLevel: 'low', x: -15, y: -20, z: 35 }
  ],
  links: [
    { source: 0, target: 1, transfer: 4500 },
    { source: 0, target: 2, transfer: 6200 },
    { source: 0, target: 3, transfer: 3200 },
    { source: 0, target: 4, transfer: 3800 },
    { source: 1, target: 5, transfer: 2800 },
    { source: 2, target: 6, transfer: 3500 },
    { source: 3, target: 7, transfer: 1800 },
    { source: 4, target: 8, transfer: 2100 }
  ]
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    
    console.log('[SupplyChainGraph] 组件挂载，开始初始化...')
    
    // 先获取API数据（如果失败会用mock数据兜底）
    await fetchNetworkData()
    
    // 等待DOM更新，确保threeContainer可用
    await nextTick()
    
    console.log('[SupplyChainGraph] DOM更新完成，检查容器...', {
      container: !!threeContainer.value,
      containerWidth: threeContainer.value?.clientWidth,
      containerHeight: threeContainer.value?.clientHeight
    })
    
    if (!threeContainer.value) {
      throw new Error('3D容器未找到，请确保template中有 ref="threeContainer"')
    }
    
    // 初始化3D场景（无论API是否成功都执行）
    initThreeScene()
    
    // 更新统计信息
    updateNetworkStats()
    
    loading.value = false
    console.log('[SupplyChainGraph] 初始化完成')
  } catch (err) {
    console.error('[SupplyChainGraph] 初始化失败:', err)
    error.value = '初始化失败: ' + err.message
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (threeSceneObj) {
    threeSceneObj.destroy()
    threeSceneObj = null
  }
})

async function fetchNetworkData() {
  try {
    error.value = ''
    loading.value = true

    // 调用真实API
    const [networkRes, suppliersRes] = await Promise.all([
      fetch(`${API_BASE}/supply-chain/network`),
      fetch(`${API_BASE}/supply-chain/suppliers`)
    ])

    if (!networkRes.ok) throw new Error(`供应链网络API请求失败: ${networkRes.status}`)
    if (!suppliersRes.ok) throw new Error(`供应商列表API请求失败: ${suppliersRes.status}`)

    const networkDataRaw = await networkRes.json()
    const suppliersData = await suppliersRes.json()

    // 更新供应链网络数据（映射到mockNetworkData格式）
    const mappedNodes = (networkDataRaw.nodes || []).map(n => ({
      id: n.id || 0,
      name: n.name || 'Unknown',
      type: n.tier === 1 ? 'core' : `tier${n.tier}`,
      emission: n.emissions || 0,
      carbonFootprint: n.carbon_intensity || 0,
      riskLevel: n.risk_level || 'medium',
      x: (n.x || 0) - 50,
      y: (n.y || 0) - 10,
      z: (n.z || 0) - 50
    }))
    const mappedLinks = (networkDataRaw.links || []).map(l => ({
      source: l.source || 0,
      target: l.target || 0,
      value: l.carbon_transfer || 0
    }))
    networkData = { nodes: mappedNodes, links: mappedLinks }
    window.__networkNodes = mappedNodes
    window.__networkLinks = mappedLinks

    // 更新供应商列表
    suppliers.value = (suppliersData.suppliers || []).map(s => ({
      id: s.id || 0,
      name: s.name || 'Unknown',
      emission: s.emission || 0,
      riskLevel: s.risk_level || 'medium'
    }))

    // 更新优化建议
    recommendations.value = (networkData.recommendations || []).map((r, idx) => ({
      priority: r.priority || idx + 1,
      title: r.title || '优化方案',
      description: r.description || '根据AI分析生成的优化建议',
      reduction: r.reduction || 0,
      cost: r.cost || 0,
      payback: r.payback || 0
    }))

    console.log('[API] 供应链数据加载成功', { network: networkData, suppliers: suppliersData })
  } catch (err) {
    error.value = '数据加载失败: ' + err.message
    console.warn('[API] 加载失败，使用mock数据兜底', err)
    // 保持mock数据不变
  }
  // 注意：不在这里设 loading.value = false，由 onMounted 统一控制
}

function initThreeScene() {
  if (!threeContainer.value) {
    console.error('[initThreeScene] threeContainer.value 为空')
    return
  }
  
  // 确保容器有有效尺寸
  const containerWidth = threeContainer.value.clientWidth || threeContainer.value.offsetWidth || 800
  const containerHeight = threeContainer.value.clientHeight || threeContainer.value.offsetHeight || 600
  
  console.log('[initThreeScene] 开始初始化3D场景...', {
    container: !!threeContainer.value,
    width: containerWidth,
    height: containerHeight
  })
  
  try {
    threeSceneObj = createThreeScene(threeContainer.value, {
      background: 0x0a1628,
      enablePostProcessing: true,
      autoRotate: false,
      autoRotateSpeed: 0
    })
    
    console.log('[initThreeScene] createThreeScene 返回对象:', threeSceneObj)
    
    if (!threeSceneObj || !threeSceneObj.scene) {
      throw new Error('createThreeScene 返回的对象无效')
    }
    
    const scene = threeSceneObj.scene
    const camera = threeSceneObj.camera
    const renderer = threeSceneObj.renderer
    
    console.log('[initThreeScene] 场景对象创建成功', {
      scene: scene,
      camera: camera,
      renderer: renderer,
      cameraPosition: camera.position,
      controls: threeSceneObj.controls
    })

    // 地面
    const groundGeometry = new THREE.PlaneGeometry(300, 300)
    const groundMaterial = new THREE.MeshPhongMaterial({ color: 0x111d33, side: THREE.DoubleSide })
    const ground = new THREE.Mesh(groundGeometry, groundMaterial)
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = true
    scene.add(ground)
    console.log('[initThreeScene] 地面已添加')

    // 创建力导向图
    const graphData = networkData || mockNetworkData
    console.log('[initThreeScene] 使用数据创建力导向图:', graphData)
    createForceGraph(graphData)
    console.log('[initThreeScene] 力导向图创建完成')

    // 相机位置
    camera.position.set(0, 80, 100)
    camera.lookAt(0, 0, 0)
    threeSceneObj.controls.target.set(0, 0, 0)
    threeSceneObj.controls.update()
    
    console.log('[initThreeScene] 相机位置已设置:', camera.position)

    // 点击事件
    threeContainer.value.addEventListener('click', onThreeClick)
    console.log('[initThreeScene] 点击事件已绑定')
    
    // 启动渲染循环（关键修复！）
    if (threeSceneObj && threeSceneObj.start) {
      threeSceneObj.start()
      console.log('[initThreeScene] 动画循环已启动')
    } else {
      console.error('[initThreeScene] threeSceneObj.start 方法不存在')
    }
    
  } catch (err) {
    console.error('[initThreeScene] 初始化失败:', err)
    error.value = '3D场景初始化失败: ' + err.message
  }
}

function createForceGraph(data) {
  if (!threeSceneObj || !threeSceneObj.scene) {
    console.error('[createForceGraph] threeSceneObj 或 scene 未初始化')
    return
  }
  
  const scene = threeSceneObj.scene
  console.log('[createForceGraph] 开始创建力导向图', data)

  // 清理旧图形
  if (forceGraphGroup) {
    scene.remove(forceGraphGroup)
    forceGraphGroup.traverse(obj => {
      if (obj.geometry) obj.geometry.dispose()
      if (obj.material) obj.material.dispose()
    })
    forceGraphGroup = null
  }

  forceGraphGroup = new THREE.Group()
  console.log('[createForceGraph] forceGraphGroup 已创建')

  // 创建节点
  const nodeObjects = []

  data.nodes.forEach((node, index) => {
    const radius = 2 + (node.emission / 20000) * 3
    const color = getNodeColor(node.type, node.riskLevel)
    
    console.log(`[createForceGraph] 创建节点 ${index}:`, node.name, { radius, color })

    const geometry = new THREE.SphereGeometry(radius, 32, 32)
    const material = new THREE.MeshPhongMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.3,
      shininess: 100
    })
    const sphere = new THREE.Mesh(geometry, material)
    sphere.position.set(node.x, node.y, node.z)
    sphere.castShadow = true
    sphere.userData = {
      nodeId: node.id,
      nodeData: node,
      isGraphNode: true
    }
    forceGraphGroup.add(sphere)
    nodeObjects.push(sphere)

    // 添加光环
    const ringGeometry = new THREE.RingGeometry(radius * 1.3, radius * 1.5, 32)
    const ringMaterial = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 0.2,
      side: THREE.DoubleSide
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.set(node.x, node.y, node.z)
    ring.rotation.x = -Math.PI / 2
    ring.userData = { isGraphNode: true }
    forceGraphGroup.add(ring)

    // 添加标签精灵
    const canvas = document.createElement('canvas')
    canvas.width = 256
    canvas.height = 64
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = 'rgba(10, 22, 40, 0.8)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 18px Microsoft YaHei'
    ctx.textAlign = 'center'
    ctx.fillText(node.name, 128, 28)
    ctx.font = '14px Microsoft YaHei'
    ctx.fillStyle = '#00d4aa'
    ctx.fillText(`${node.emission} tCO₂e`, 128, 50)

    const texture = new THREE.CanvasTexture(canvas)
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true })
    const sprite = new THREE.Sprite(spriteMaterial)
    sprite.position.set(node.x, node.y + radius + 3, node.z)
    sprite.scale.set(12, 3, 1)
    sprite.userData = { isGraphNode: true }
    forceGraphGroup.add(sprite)
  })
  
  console.log('[createForceGraph] 节点创建完成，共', nodeObjects.length, '个节点')

  // 创建连接线
  let linkCount = 0
  data.links.forEach((link, index) => {
    const sourceNode = data.nodes.find(n => n.id === link.source)
    const targetNode = data.nodes.find(n => n.id === link.target)

    if (sourceNode && targetNode) {
      linkCount++
      console.log(`[createForceGraph] 创建连接线 ${index}:`, sourceNode.name, '->', targetNode.name)

      const startVec = new THREE.Vector3(sourceNode.x, sourceNode.y, sourceNode.z)
      const endVec = new THREE.Vector3(targetNode.x, targetNode.y, targetNode.z)

      // 计算线的粗细（根据碳转移量）
      const lineWidth = 1 + (link.transfer / 7000) * 3

      // 创建曲线路径
      const midPoint = new THREE.Vector3()
        .addVectors(startVec, endVec)
        .multiplyScalar(0.5)
      midPoint.y += 5

      const curve = new THREE.QuadraticBezierCurve3(startVec, midPoint, endVec)
      const points = curve.getPoints(50)

      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points)
      
      // WebGL 只支持 linewidth = 1，>1 会静默失败
      // 使用固定 linewidth: 1，通过 opacity 区分粗细视觉效果
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x1890ff,
        transparent: true,
        opacity: 0.3 + (link.transfer / 7000) * 0.7,  // 用透明度替代线宽
        linewidth: 1
      })
      const line = new THREE.Line(lineGeometry, lineMaterial)
      line.userData = { isGraphNode: true, linkData: link }
      forceGraphGroup.add(line)

      // 添加流动粒子
      const particleCount = 20
      const particlePositions = new Float32Array(particleCount * 3)

      for (let i = 0; i < particleCount; i++) {
        const t = i / particleCount
        const point = curve.getPoint(t)
        particlePositions[i * 3] = point.x
        particlePositions[i * 3 + 1] = point.y
        particlePositions[i * 3 + 2] = point.z
      }

      const particleGeometry = new THREE.BufferGeometry()
      particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))

      const particleMaterial = new THREE.PointsMaterial({
        color: 0x00d4aa,
        size: 0.8,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      })

      const particles = new THREE.Points(particleGeometry, particleMaterial)
      particles.userData = {
        isGraphNode: true,
        curve,
        particleCount,
        update: (time) => {
          const positions = particles.geometry.attributes.position.array
          for (let i = 0; i < particleCount; i++) {
            const t = ((time * 0.0005 + i / particleCount) % 1)
            const point = curve.getPoint(t)
            positions[i * 3] = point.x
            positions[i * 3 + 1] = point.y
            positions[i * 3 + 2] = point.z
          }
          particles.geometry.attributes.position.needsUpdate = true
        }
      }
      forceGraphGroup.add(particles)

      // 添加动画更新
      if (threeSceneObj.addAnimationHandler) {
        threeSceneObj.addAnimationHandler((time) => {
          if (particles.userData.update) {
            particles.userData.update(time)
          }
        })
      }
    }
  })
  
  console.log('[createForceGraph] 连接线创建完成，共', linkCount, '条连接')

  scene.add(forceGraphGroup)
  console.log('[createForceGraph] forceGraphGroup 已添加到场景')
  
  // 强制更新场景
  if (threeSceneObj && threeSceneObj.renderer && threeSceneObj.scene && threeSceneObj.camera) {
    threeSceneObj.renderer.render(threeSceneObj.scene, threeSceneObj.camera)
    console.log('[createForceGraph] 强制渲染完成')
  } else {
    console.warn('[createForceGraph] threeSceneObj 渲染器未就绪，无法强制渲染')
  }
}

function getNodeColor(type, riskLevel) {
  if (riskLevel === 'high') return 0xff4d4f
  switch (type) {
    case 'core': return 0x00d4aa
    case 'tier1': return 0x1890ff
    case 'tier2': return 0xf39c12
    case 'tier3': return 0x909399
    default: return 0x00d4aa
  }
}

function getRiskColor(riskLevel) {
  switch (riskLevel) {
    case 'low': return '#00d4aa'
    case 'medium': return '#f39c12'
    case 'high': return '#ff4d4f'
    default: return '#909399'
  }
}

function getRiskLabel(riskLevel) {
  switch (riskLevel) {
    case 'low': return '低风险'
    case 'medium': return '中风险'
    case 'high': return '高风险'
    default: return '未知'
  }
}

function onThreeClick(event) {
  if (!threeSceneObj || !threeContainer.value) return

  const rect = threeContainer.value.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  const y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  const raycaster = new THREE.Raycaster()
  raycaster.setFromCamera(new THREE.Vector2(x, y), threeSceneObj.camera)

  const intersects = raycaster.intersectObjects(threeSceneObj.scene.children, true)
  if (intersects.length > 0) {
    const obj = intersects[0].object
    if (obj.userData && obj.userData.nodeData) {
      hoveredNode.value = obj.userData.nodeData
      selectedNode.value = obj.userData.nodeData
    }
  }
}

function handleSearch() {
  // 搜索逻辑
  console.log('搜索:', searchKeyword.value)
}

function handleFilter() {
  // 筛选逻辑
  console.log('筛选条件变化:', filterRisk.value, filterCarbonIntensity.value)
}

function focusOnNode(nodeId) {
  if (!threeSceneObj) return
  const nodeData = (networkData?.nodes || mockNetworkData.nodes).find(n => n.id === nodeId)
  if (nodeData) {
    // 将相机对准该节点
    const camera = threeSceneObj.camera
    const controls = threeSceneObj.controls
    controls.target.set(nodeData.x, nodeData.y, nodeData.z)
  }
}

function toggleRecommendation(idx) {
  expandedRecommendation.value = expandedRecommendation.value === idx ? -1 : idx
}

function applyRecommendation(item) {
  console.log('应用方案:', item.title)
  // 实际应用中这里会调用API
  alert(`已应用方案: ${item.title}`)
}

function saveRecommendation(item) {
  console.log('保存方案:', item.title)
  alert(`已保存方案: ${item.title}`)
}

function updateNetworkStats() {
  const nodes = networkData?.nodes || mockNetworkData.nodes
  const links = networkData?.links || mockNetworkData.links
  const highRiskNodes = nodes.filter(n => n.riskLevel === 'high').length
  const avgIntensity = (nodes.reduce((sum, n) => sum + n.carbonFootprint, 0) / nodes.length).toFixed(1)

  networkStats.value = {
    totalNodes: nodes.length,
    totalLinks: links.length,
    avgCarbonIntensity: avgIntensity,
    highRiskNodes
  }
}
</script>

<style scoped>
.supply-chain-graph {
  width: 100%;
  height: 100vh;
  background: #0a1628;
  position: relative;
  overflow: hidden;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 加载状态 */
.loading-wrapper {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(10, 22, 40, 0.95); z-index: 1000;
}
.loading-spinner {
  width: 50px; height: 50px;
  border: 4px solid rgba(0, 212, 170, 0.2);
  border-top: 4px solid #00d4aa;
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: #00d4aa; margin-top: 16px; font-size: 15px; letter-spacing: 1px; }

/* 错误提示 */
.error-banner {
  position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
  z-index: 1001; min-width: 400px;
}

/* 主体布局 */
.main-layout {
  display: flex; width: 100%; height: 100vh;
  padding: 12px; gap: 12px;
}

/* 左侧面板 */
.left-panel {
  width: 280px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px;
  gap: 12px; overflow-y: auto;
}
.panel-header { margin-bottom: 8px; }
.panel-title {
  font-size: 13px; font-weight: 600; color: #c0c4cc;
  display: flex; align-items: center; gap: 6px;
}
.control-section { margin-bottom: 16px; }
.section-label { font-size: 12px; color: #909399; margin-bottom: 8px; font-weight: 500; }

/* 图例 */
.legend-list { display: flex; flex-direction: column; gap: 6px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #c0c4cc; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* 统计网格 */
.stats-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}
.stat-item {
  background: rgba(255, 255, 255, 0.03); border-radius: 6px;
  padding: 8px; text-align: center;
}
.stat-value { font-size: 18px; font-weight: 700; color: #00d4aa; }
.stat-label { font-size: 10px; color: #909399; margin-top: 2px; }

/* 中央3D区域 */
.center-3d {
  flex: 1; position: relative;
  border-radius: 12px; overflow: hidden;
  background: #0a1628; border: 1px solid #111d33;
}
.three-container { width: 100%; height: 100%; }

/* 悬浮信息 */
.hover-info {
  position: absolute; top: 12px; left: 12px;
  background: rgba(17, 29, 51, 0.9); border-radius: 8px;
  padding: 10px 14px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2); font-size: 12px;
  min-width: 200px;
}
.hover-title { font-size: 14px; font-weight: 600; color: #e0e0e0; margin-bottom: 6px; }
.hover-data { color: #c0c4cc; line-height: 1.6; }

/* 操作提示 */
.scene-hint {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  background: rgba(17, 29, 51, 0.85); border-radius: 8px;
  padding: 8px 16px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2);
  font-size: 11px; color: #909399; display: flex; align-items: center; gap: 6px;
  white-space: nowrap;
}

/* 右侧面板 */
.right-panel {
  width: 320px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px;
  overflow-y: auto; gap: 12px;
}

/* 推荐列表 */
.recommendation-list { display: flex; flex-direction: column; gap: 8px; }
.recommendation-item {
  background: rgba(255, 255, 255, 0.03); border-radius: 8px;
  padding: 10px; cursor: pointer; transition: all 0.3s ease;
}
.recommendation-item:hover { background: rgba(0, 212, 170, 0.08); }
.recommendation-item.expanded { background: rgba(0, 212, 170, 0.12); border: 1px solid rgba(0, 212, 170, 0.3); }
.rec-header { display: flex; align-items: center; gap: 8px; }
.rec-priority {
  width: 20px; height: 20px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.priority-1 { background: #ff4d4f; }
.priority-2 { background: #f39c12; }
.priority-3 { background: #1890ff; }
.priority-4 { background: #909399; }
.rec-title { flex: 1; font-size: 12px; color: #e0e0e0; line-height: 1.4; }
.rec-arrow { color: #909399; transition: transform 0.3s; }
.recommendation-item.expanded .rec-arrow { transform: rotate(180deg); }
.rec-content { margin-top: 10px; font-size: 11px; color: #c0c4cc; line-height: 1.6; }
.rec-description { margin-bottom: 10px; }
.rec-meta { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; }
.rec-meta .meta-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 8px; background: rgba(255, 255, 255, 0.02); border-radius: 4px;
}
.rec-meta .meta-label { color: #909399; }
.rec-meta .meta-value { font-weight: 600; color: #e0e0e0; }
.rec-actions { display: flex; gap: 8px; }

/* 供应商列表 */
.supplier-list { display: flex; flex-direction: column; gap: 6px; }
.supplier-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 10px; background: rgba(255, 255, 255, 0.03);
  border-radius: 6px; cursor: pointer; transition: all 0.3s ease;
}
.supplier-item:hover { background: rgba(0, 212, 170, 0.08); }
.supplier-name { font-size: 12px; color: #e0e0e0; }
.supplier-meta { display: flex; gap: 8px; align-items: center; font-size: 10px; }
.supplier-emission { color: #909399; }
.supplier-risk { font-weight: 600; }

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: transparent; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb {
  background: #1890ff; border-radius: 2px;
}
</style>
