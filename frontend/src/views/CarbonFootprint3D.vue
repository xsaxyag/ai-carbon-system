<template>
  <div class="carbon-footprint-3d">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载碳足迹数据...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <el-alert :title="error" type="error" show-icon :closable="false" />
    </div>

    <div v-show="!loading" class="main-layout">
      <!-- 左侧：LCA树形结构 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><List /></el-icon> 产品LCA结构</span>
        </div>
        <div class="tree-container">
          <el-tree
            :data="lcaTree"
            :props="treeProps"
            node-key="id"
            default-expand-all
            highlight-current
            @node-click="handleNodeClick"
            class="lca-tree"
          >
            <template #default="{ node, data: slotData }">
              <span class="tree-node" :class="{ 'high-emission': slotData.isHigh }">
                <span class="node-label">{{ slotData.label }}</span>
                <span v-if="slotData.value !== undefined" class="node-value" :style="{ color: slotData.isHigh ? '#ff4d4f' : '#00d4aa' }">
                  {{ slotData.value }} kgCO₂e
                </span>
              </span>
            </template>
          </el-tree>
        </div>

        <!-- 产品选择 -->
        <div class="product-selector">
          <div class="panel-title" style="margin-bottom: 8px;"><el-icon><Box /></el-icon> 选择产品</div>
          <el-select
            v-model="selectedProduct"
            placeholder="选择产品"
            style="width: 100%;"
            @change="loadProductData"
          >
            <el-option
              v-for="p in products"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </div>
      </div>

      <!-- 中央：3D流程管道图 -->
      <div class="center-3d">
        <div ref="threeContainer" class="three-container"></div>
        <!-- 提示信息 -->
        <div class="scene-hint">
          <el-icon><InfoFilled /></el-icon>
          鼠标拖拽旋转视角 | 滚轮缩放 | 点击管道节点查看详情
        </div>
      </div>

      <!-- 右侧：详情面板 -->
      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><DataLine /></el-icon> 环节详情</span>
        </div>

        <div v-if="selectedNode" class="node-detail">
          <div class="detail-header" :style="{ borderLeft: '4px solid ' + (selectedNode.isHigh ? '#ff4d4f' : '#00d4aa') }">
            <div class="detail-name">{{ selectedNode.label }}</div>
            <div class="detail-value" :style="{ color: selectedNode.isHigh ? '#ff4d4f' : '#00d4aa' }">
              {{ selectedNode.value || 0 }} kgCO₂e
            </div>
          </div>

          <div class="detail-meta">
            <div class="meta-item">
              <span class="meta-label">占比</span>
              <span class="meta-value">{{ selectedNode.percentage || 0 }}%</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">环比</span>
              <span class="meta-value" :class="selectedNode.trend >= 0 ? 'trend-up' : 'trend-down'">
                {{ selectedNode.trend !== undefined ? (selectedNode.trend >= 0 ? '↑' : '↓') + ' ' + Math.abs(selectedNode.trend) + '%' : 'N/A' }}
              </span>
            </div>
            <div class="meta-item">
              <span class="meta-label">等级</span>
              <el-tag
                :type="selectedNode.isHigh ? 'danger' : 'success'"
                size="small"
                effect="dark"
                round
              >
                {{ selectedNode.isHigh ? '高排放' : '正常' }}
              </el-tag>
            </div>
          </div>

          <!-- 减排建议 -->
          <div class="suggestion-box" v-if="selectedNode.suggestions">
            <div class="suggestion-title"><el-icon><Promotion /></el-icon> 减排建议</div>
            <ul class="suggestion-list">
              <li v-for="(s, idx) in selectedNode.suggestions" :key="idx">{{ s }}</li>
            </ul>
          </div>
        </div>

        <div v-else class="no-selection">
          <el-icon :size="48"><DataLine /></el-icon>
          <div style="margin-top: 12px; color: #606266;">请在左侧选择环节或点击3D场景中的节点</div>
        </div>

        <!-- 底部：碳足迹瀑布图 -->
        <div class="waterfall-chart">
          <div class="panel-header" style="margin-top: 16px;">
            <span class="panel-title"><el-icon><Histogram /></el-icon> 碳足迹瀑布图</span>
          </div>
          <div ref="waterfallChart" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'
import { List, Box, DataLine, InfoFilled, Histogram, Promotion } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import * as THREE from 'three'
import { createThreeScene, createFlowLine, createFootprintNode } from '../utils/three-scene'

// 状态
const loading = ref(true)
const error = ref('')
const selectedProduct = ref(1)
const selectedNode = ref(null)

// DOM引用
const threeContainer = ref(null)
const waterfallChart = ref(null)

// 3D场景
let threeSceneObj = null

// 图表实例
let waterfallChartInstance = null

// 产品列表
const products = ref([
  { id: 1, name: '光伏组件A型' },
  { id: 2, name: '储能电池B型' },
  { id: 3, name: '逆变器C型' }
])

// LCA树形数据
const lcaTree = ref([])
const treeProps = {
  children: 'children',
  label: 'label'
}

// 模拟数据
const mockLCAData = {
  1: {
    total: 1250,
    stages: [
      {
        id: 'raw', label: '原材料获取', value: 480, percentage: 38.4, trend: 5.2, isHigh: true,
        children: [
          { id: 'aluminum', label: '铝材', value: 280, percentage: 22.4, trend: 3.1, isHigh: true },
          { id: 'steel', label: '钢材', value: 120, percentage: 9.6, trend: 1.2, isHigh: false },
          { id: 'plastic', label: '塑料', value: 80, percentage: 6.4, trend: 2.3, isHigh: false }
        ],
        suggestions: ['采用再生铝材可减少40%碳排放', '优化材料利用率至95%以上']
      },
      {
        id: 'production', label: '生产制造', value: 350, percentage: 28.0, trend: -2.1, isHigh: false,
        children: [
          { id: 'casting', label: '铸造', value: 150, percentage: 12.0, trend: -1.5, isHigh: false },
          { id: 'assembly', label: '组装', value: 120, percentage: 9.6, trend: -0.8, isHigh: false },
          { id: 'testing', label: '测试', value: 80, percentage: 6.4, trend: 0.2, isHigh: false }
        ],
        suggestions: ['使用绿电生产可降低60%碳排放', '优化工艺温度控制']
      },
      {
        id: 'transport', label: '运输物流', value: 180, percentage: 14.4, trend: 8.5, isHigh: false,
        children: [
          { id: 'road', label: '公路运输', value: 120, percentage: 9.6, trend: 10.2, isHigh: true },
          { id: 'rail', label: '铁路运输', value: 40, percentage: 3.2, trend: 2.1, isHigh: false },
          { id: 'sea', label: '海运', value: 20, percentage: 1.6, trend: -1.5, isHigh: false }
        ],
        suggestions: ['优先选择铁路/海运等低碳运输方式', '优化运输路线规划']
      },
      {
        id: 'usage', label: '使用阶段', value: 150, percentage: 12.0, trend: -5.3, isHigh: false,
        children: [
          { id: 'operation', label: '运行', value: 100, percentage: 8.0, trend: -4.2, isHigh: false },
          { id: 'maintenance', label: '维护', value: 50, percentage: 4.0, trend: -1.1, isHigh: false }
        ],
        suggestions: ['提高产品能效等级', '提供定期维护服务']
      },
      {
        id: 'endoflife', label: '废弃处理', value: 90, percentage: 7.2, trend: -8.2, isHigh: false,
        children: [
          { id: 'recycle', label: '回收', value: 60, percentage: 4.8, trend: -10.5, isHigh: false },
          { id: 'landfill', label: '填埋', value: 30, percentage: 2.4, trend: 2.3, isHigh: false }
        ],
        suggestions: ['提高回收利用率至85%以上', '设计易回收产品结构']
      }
    ]
  }
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    await loadProductData(selectedProduct.value)
    await nextTick()
    initThreeScene()
    initWaterfallChart()
    loading.value = false
  } catch (err) {
    error.value = '初始化失败: ' + err.message
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (threeSceneObj) {
    threeSceneObj.destroy()
    threeSceneObj = null
  }
  waterfallChartInstance?.dispose()
})

async function loadProductData(productId) {
  try {
    // 调用真实API
    const res = await fetch(`${API_BASE}/api/v1/footprint-3d/lca-chain/prod_${String(productId).padStart(3, '0')}`)
    if (!res.ok) throw new Error(`API请求失败: ${res.status}`)
    const apiData = await res.json()

    // 数据格式转换 snake_case → camelCase
    const data = {
      total: apiData.total_footprint || 0,
      stages: (apiData.chain_nodes || []).map(node => ({
        id: node.id || 0,
        label: node.name || 'Unknown',
        value: node.emissions || 0,
        percentage: node.percentage || 0,
        trend: node.status === 'warning' ? 5.2 : (node.status === 'critical' ? 12.1 : -2.3),
        isHigh: node.status === 'critical' || node.status === 'warning',
        suggestions: node.detail ? [`优化建议: ${node.detail}`] : [],
        children: []
      }))
    }

    // 如果API无数据，使用mock兜底
    if (!data.stages || data.stages.length === 0) {
      data = mockLCAData[productId] || mockLCAData[1]
    }

    // 构建树形数据
    const tree = data.stages.map(stage => ({
      id: stage.id,
      label: stage.label,
      value: stage.value,
      percentage: stage.percentage,
      trend: stage.trend,
      isHigh: stage.isHigh,
      suggestions: stage.suggestions,
      children: stage.children.map(child => ({
        id: child.id,
        label: child.label,
        value: child.value,
        percentage: child.percentage,
        trend: child.trend,
        isHigh: child.isHigh
      }))
    }))

    lcaTree.value = tree

    // 自动选择第一个节点
    if (tree.length > 0) {
      selectedNode.value = { ...tree[0] }
    }

    // 更新3D场景
    if (threeSceneObj) {
      updateThreeScene(tree)
    }

    // 更新瀑布图
    updateWaterfallChart(data)
  } catch (err) {
    error.value = '加载数据失败: ' + err.message
    // 降级到mock数据
    try {
      const fallback = mockLCAData[productId] || mockLCAData[1]
      // 使用fallback数据继续构建tree...
      const tree = fallback.stages.map(stage => ({
        id: stage.id,
        label: stage.label,
        value: stage.value,
        percentage: stage.percentage,
        trend: stage.trend,
        isHigh: stage.isHigh,
        suggestions: stage.suggestions,
        children: stage.children.map(child => ({
          id: child.id,
          label: child.label,
          value: child.value,
          percentage: child.percentage,
          trend: child.trend,
          isHigh: child.isHigh
        }))
      }))
      lcaTree.value = tree
      if (tree.length > 0) selectedNode.value = { ...tree[0] }
      if (threeSceneObj) updateThreeScene(tree)
      updateWaterfallChart(fallback)
    } catch (fallbackErr) {
      console.error('Mock data fallback failed:', fallbackErr)
    }
  } finally {
    loading.value = false
  }
}

function handleNodeClick(data) {
  selectedNode.value = { ...data }
  // 在3D场景中高亮对应节点
  highlightThreeNode(data.id)
}

function initThreeScene() {
  if (!threeContainer.value) return

  threeSceneObj = createThreeScene(threeContainer.value, {
    background: 0x0a1628,
    enablePostProcessing: true,
    autoRotate: false,
    autoRotateSpeed: 0
  })

  // 添加灯光
  const scene = threeSceneObj.scene

  // 地面
  const groundGeometry = new THREE.PlaneGeometry(200, 200)
  const groundMaterial = new THREE.MeshPhongMaterial({ color: 0x111d33, side: THREE.DoubleSide })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)

  // 初始化管道
  const tree = lcaTree.value
  if (tree.length > 0) {
    updateThreeScene(tree)
  }

  // 相机位置
  threeSceneObj.camera.position.set(0, 40, 80)
  threeSceneObj.controls.target.set(0, 10, 0)
}

function updateThreeScene(tree) {
  if (!threeSceneObj) return
  const scene = threeSceneObj.scene

  // 清理旧对象（保留灯光和地面）
  const toRemove = []
  scene.traverse((obj) => {
    if (obj.userData && obj.userData.isLCANode) {
      toRemove.push(obj)
    }
  })
  toRemove.forEach(obj => {
    if (obj.geometry) obj.geometry.dispose()
    if (obj.material) obj.material.dispose()
    scene.remove(obj)
  })

  // 创建流程节点（水平排列）
  const spacing = 25
  const startX = -((tree.length - 1) * spacing) / 2

  for (let i = 0; i < tree.length; i++) {
    const stage = tree[i]
    const x = startX + i * spacing
    const y = 10
    const z = 0

    // 创建节点
    const node = createFootprintNode(stage.label, stage.value, {
      radius: 3 + (stage.value / 500) * 2,
      color: stage.isHigh ? 0xff4d4f : 0x00d4aa,
      isHigh: stage.isHigh
    })
    node.position.set(x, y, z)
    node.userData = {
      ...node.userData,
      isLCANode: true,
      stageId: stage.id
    }
    scene.add(node)

    // 创建流向管道（连接到下一个节点）
    if (i < tree.length - 1) {
      const nextX = startX + (i + 1) * spacing
      const startVec = new THREE.Vector3(x, y, z)
      const endVec = new THREE.Vector3(nextX, y, z)
      const flowLine = createFlowLine(startVec, endVec, {
        particleCount: 50,
        color: stage.isHigh ? 0xff4d4f : 0x00d4aa,
        lineColor: 0x1890ff
      })
      flowLine.userData.isLCANode = true
      scene.add(flowLine)

      // 添加动画更新
      threeSceneObj.addAnimationHandler((time) => {
        if (flowLine.userData.update) {
          flowLine.userData.update(time)
        }
      })
    }

    // 添加标签精灵
    const canvas = document.createElement('canvas')
    canvas.width = 256
    canvas.height = 64
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = 'rgba(10, 22, 40, 0.8)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = stage.isHigh ? '#ff4d4f' : '#00d4aa'
    ctx.font = 'bold 20px Microsoft YaHei'
    ctx.textAlign = 'center'
    ctx.fillText(stage.label, 128, 30)
    ctx.font = '16px Microsoft YaHei'
    ctx.fillText(`${stage.value} kgCO₂e`, 128, 52)

    const texture = new THREE.CanvasTexture(canvas)
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true })
    const sprite = new THREE.Sprite(spriteMaterial)
    sprite.position.set(x, y + 6, z)
    sprite.scale.set(12, 3, 1)
    sprite.userData.isLCANode = true
    scene.add(sprite)
  }
}

function highlightThreeNode(stageId) {
  if (!threeSceneObj) return
  const scene = threeSceneObj.scene
  scene.traverse((obj) => {
    if (obj.userData && obj.userData.stageId === stageId) {
      // 高亮效果：放大并改变颜色
      obj.scale.set(1.2, 1.2, 1.2)
      setTimeout(() => {
        obj.scale.set(1, 1, 1)
      }, 1000)
    }
  })
}

function initWaterfallChart() {
  if (!waterfallChart.value) return
  waterfallChartInstance = markRaw(echarts.init(waterfallChart.value))
  updateWaterfallChart(mockLCAData[1])
}

function updateWaterfallChart(data) {
  if (!waterfallChartInstance) return

  const stages = data.stages
  const total = data.total

  // 瀑布图数据
  const values = []
  let cumulative = 0
  stages.forEach((stage, idx) => {
    values.push({
      name: stage.label,
      value: stage.value,
      cumulative: cumulative,
      percentage: stage.percentage
    })
    cumulative += stage.value
  })

  waterfallChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<Promotion />排放: ${p.data.value} kgCO₂e<Promotion />占比: ${p.data.percentage}%`
      },
      backgroundColor: 'rgba(10,22,40,0.95)',
      borderColor: '#00d4aa',
      textStyle: { color: '#fff', fontSize: 11 }
    },
    grid: { left: '8%', right: '5%', bottom: '15%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: stages.map(s => s.label),
      axisLabel: { fontSize: 9, color: '#909399', rotate: 20 },
      axisLine: { lineStyle: { color: '#2c3e50' } }
    },
    yAxis: {
      type: 'value',
      name: 'kgCO₂e',
      nameTextStyle: { fontSize: 9, color: '#909399' },
      axisLabel: { fontSize: 9, color: '#909399' },
      splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      data: stages.map((s, idx) => ({
        value: s.value,
        cumulative: values[idx].cumulative,
        percentage: s.percentage,
        itemStyle: {
          color: s.isHigh
            ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#ff4d4f' }, { offset: 1, color: '#c0392b' }])
            : new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#00d4aa' }, { offset: 1, color: '#27ae60' }])
        }
      })),
      itemStyle: { borderRadius: [4, 4, 0, 0] },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}',
        fontSize: 9,
        color: '#c0c4cc'
      },
      animationDuration: 1200,
      animationDelay: (idx) => idx * 150
    }]
  })

  window.addEventListener('resize', () => waterfallChartInstance?.resize())
}

function handleResize() {
  waterfallChartInstance?.resize()
}
</script>

<style scoped>
.carbon-footprint-3d {
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
  width: 260px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px; gap: 12px;
  overflow-y: auto;
}
.panel-header { margin-bottom: 8px; }
.panel-title {
  font-size: 13px; font-weight: 600; color: #c0c4cc;
  display: flex; align-items: center; gap: 6px;
}
.tree-container { flex: 1; overflow-y: auto; }

/* 树形样式 */
.lca-tree { background: transparent; color: #c0c4cc; font-size: 12px; }
:deep(.el-tree-node__content):hover { background: rgba(0, 212, 170, 0.1) !important; }
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(0, 212, 170, 0.2) !important; color: #00d4aa;
}
.tree-node { display: flex; align-items: center; justify-content: space-between; width: 100%; padding-right: 8px; }
.tree-node.high-emission .node-label { color: #ff4d4f; }
.node-label { font-size: 12px; }
.node-value { font-size: 11px; font-weight: 600; }

/* 产品选择器 */
.product-selector { margin-top: 12px; }

/* 中央3D区域 */
.center-3d {
  flex: 1; position: relative;
  border-radius: 12px; overflow: hidden;
  background: #0a1628; border: 1px solid #111d33;
}
.three-container { width: 100%; height: 100%; }

/* 场景提示 */
.scene-hint {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  background: rgba(17, 29, 51, 0.85); border-radius: 8px;
  padding: 8px 16px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2);
  font-size: 11px; color: #909399; display: flex; align-items: center; gap: 6px;
}

/* 右侧面板 */
.right-panel {
  width: 300px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px;
  overflow-y: auto; gap: 12px;
}

/* 节点详情 */
.node-detail { flex: 1; }
.detail-header {
  padding: 12px; background: rgba(0, 212, 170, 0.05);
  border-radius: 8px; margin-bottom: 12px;
}
.detail-name { font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 6px; }
.detail-value { font-size: 24px; font-weight: 800; }

.detail-meta { display: flex; flex-direction: column; gap: 8px; }
.meta-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 10px; background: rgba(255, 255, 255, 0.03);
  border-radius: 6px; font-size: 12px;
}
.meta-label { color: #909399; }
.meta-value { font-weight: 600; color: #e0e0e0; }
.trend-up { color: #f56c6c !important; }
.trend-down { color: #67c23a !important; }

/* 减排建议 */
.suggestion-box {
  margin-top: 16px; padding: 12px;
  background: rgba(0, 212, 170, 0.05);
  border-radius: 8px; border: 1px solid rgba(0, 212, 170, 0.2);
}
.suggestion-title {
  font-size: 13px; font-weight: 600; color: #00d4aa;
  margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.suggestion-list {
  margin: 0; padding-left: 20px; font-size: 12px; color: #c0c4cc; line-height: 1.8;
}

/* 无选择提示 */
.no-selection {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #606266;
}

/* 瀑布图 */
.waterfall-chart { margin-top: 12px; }
.chart-container { height: 220px; }

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: transparent; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb {
  background: #1890ff; border-radius: 2px;
}
</style>
