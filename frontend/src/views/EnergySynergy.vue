<template>
  <div class="energy-synergy">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载源网荷储协同数据...</div>
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

        <!-- 时间范围选择 -->
        <div class="control-section">
          <div class="section-label">时间范围</div>
          <el-date-picker
            v-model="timeRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            style="width: 100%;"
            @change="handleTimeRangeChange"
          />
        </div>

        <!-- 能源类型筛选 -->
        <div class="control-section">
          <div class="section-label">能源类型</div>
          <el-checkbox-group v-model="selectedEnergyTypes" @change="handleEnergyFilter">
            <el-checkbox label="solar" style="color: #00d4aa;">光伏</el-checkbox>
            <el-checkbox label="wind" style="color: #1890ff;">风电</el-checkbox>
            <el-checkbox label="grid" style="color: #909399;">市电</el-checkbox>
            <el-checkbox label="storage" style="color: #f39c12;">储能</el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 实时数据概览 -->
        <div class="control-section">
          <div class="section-label">实时数据</div>
          <div class="realtime-grid">
            <div class="rt-item" v-for="(item, idx) in realtimeData" :key="idx">
              <div class="rt-icon" :style="{ background: item.color }">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <div class="rt-info">
                <div class="rt-value" :style="{ color: item.color }">{{ item.value }}</div>
                <div class="rt-label">{{ item.label }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI优化建议 -->
        <div class="control-section">
          <div class="section-label">
            <el-icon><Promotion /></el-icon> AI优化建议
          </div>
          <div class="ai-suggestions">
            <div
              v-for="(suggestion, idx) in aiSuggestions"
              :key="idx"
              class="suggestion-item"
            >
              <div class="suggestion-icon">
                <el-icon><Check /></el-icon>
              </div>
              <div class="suggestion-content">
                <div class="suggestion-title">{{ suggestion.title }}</div>
                <div class="suggestion-desc">{{ suggestion.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央3D场景 -->
      <div class="center-3d">
        <div ref="threeContainer" class="three-container"></div>

        <!-- 象限标签 -->
        <div class="quadrant-labels">
          <div class="quadrant-label" style="top: 20px; left: 20px;">源<Promotion /><span>发电侧</span></div>
          <div class="quadrant-label" style="top: 20px; right: 20px;">网<Promotion /><span>电网侧</span></div>
          <div class="quadrant-label" style="bottom: 60px; left: 20px;">荷<Promotion /><span>负荷侧</span></div>
          <div class="quadrant-label" style="bottom: 60px; right: 20px;">储<Promotion /><span>储能侧</span></div>
        </div>

        <!-- 场景提示 -->
        <div class="scene-hint">
          <el-icon><InfoFilled /></el-icon>
          鼠标拖拽旋转 | 滚轮缩放 | 点击设备查看详情
        </div>
      </div>

      <!-- 右侧：详情面板 -->
      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><DataLine /></el-icon> 源侧：绿电产能</span>
        </div>

        <!-- 源侧仪表盘 -->
        <div class="source-meters">
          <div class="meter-item" v-for="(meter, idx) in sourceMeters" :key="idx">
            <div class="meter-title">{{ meter.title }}</div>
            <div ref="meterChart" class="meter-chart"></div>
            <div class="meter-value" :style="{ color: meter.color }">{{ meter.value }} {{ meter.unit }}</div>
          </div>
        </div>

        <!-- 网侧：电网交互 -->
        <div class="panel-header" style="margin-top: 16px;">
          <span class="panel-title"><el-icon><Promotion /></el-icon> 网侧：电网交互</span>
        </div>
        <div class="grid-interaction">
          <div ref="gridChart" class="chart-container"></div>
        </div>

        <!-- 荷侧：负荷曲线 -->
        <div class="panel-header" style="margin-top: 16px;">
          <span class="panel-title"><el-icon><TrendCharts /></el-icon> 荷侧：负荷曲线</span>
        </div>
        <div class="load-chart">
          <div ref="loadChart" class="chart-container"></div>
        </div>

        <!-- 储侧：储能SOC -->
        <div class="panel-header" style="margin-top: 16px;">
          <span class="panel-title"><el-icon><Promotion /></el-icon> 储侧：储能状态</span>
        </div>
        <div class="storage-soc">
          <div class="soc-item" v-for="(bat, idx) in batterySOC" :key="idx">
            <div class="soc-header">
              <span>{{ bat.name }}</span>
              <span class="soc-value" :style="{ color: bat.soc > 70 ? '#00d4aa' : bat.soc > 30 ? '#f39c12' : '#ff4d4f' }">{{ bat.soc }}%</span>
            </div>
            <div class="soc-bar">
              <div
                class="soc-fill"
                :style="{
                  width: bat.soc + '%',
                  background: bat.soc > 70 ? '#00d4aa' : bat.soc > 30 ? '#f39c12' : '#ff4d4f'
                }"
              ></div>
            </div>
            <div class="soc-meta">
              <span>{{ bat.power }} kW</span>
              <span>{{ bat.capacity }} kWh</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'
import { Setting, Promotion, Check, InfoFilled, DataLine, TrendCharts } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import * as THREE from 'three'
import { createThreeScene, createFlowLine, createBatteryModel } from '../utils/three-scene'

// 状态
const loading = ref(true)
const error = ref('')
const timeRange = ref('')
const selectedEnergyTypes = ref(['solar', 'wind', 'grid', 'storage'])

// DOM引用
const threeContainer = ref(null)
const gridChart = ref(null)
const loadChart = ref(null)

// 3D场景
let threeSceneObj = null

// 图表实例
let gridChartInstance = null
let loadChartInstance = null
let meterChartInstances = []

// 实时数据
const realtimeData = ref([
  { label: '光伏出力', value: '2,450', unit: ' kW', color: '#00d4aa', icon: 'Sunny' },
  { label: '风电出力', value: '1,820', unit: ' kW', color: '#1890ff', icon: 'WindPower' },
  { label: '储能SOC', value: '78.5', unit: '%', color: '#f39c12', icon: 'Battery' },
  { label: '总负荷', value: '3,280', unit: ' kW', color: '#ff4d4f', icon: 'Lightning' }
])

// AI优化建议
const aiSuggestions = ref([
  {
    title: '建议增加储能充电',
    description: '未来2小时光伏出力将增加30%，建议提前将储能充电至90%以上'
  },
  {
    title: '可参与需求响应',
    description: '明日14:00-16:00预计电价较高，建议削减非必要负荷约200kW'
  },
  {
    title: '优化充放电策略',
    description: '根据负荷预测，建议调整储能削峰填谷策略，预计节约电费12%'
  }
])

// 源侧仪表盘数据
const sourceMeters = ref([
  { title: '光伏发电', value: 2450, unit: 'kW', color: '#00d4aa', max: 5000 },
  { title: '风电发电', value: 1820, unit: 'kW', color: '#1890ff', max: 5000 },
  { title: '总出力', value: 4270, unit: 'kW', color: '#f39c12', max: 10000 }
])

// 储侧SOC数据
const batterySOC = ref([
  { name: '储能A', soc: 78, power: 500, capacity: 2000 },
  { name: '储能B', soc: 65, power: 300, capacity: 1500 },
  { name: '储能C', soc: 92, power: 800, capacity: 3000 }
])

// 模拟数据
const mockGridData = {
  hours: Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`),
  gridImport: [120, 110, 105, 100, 98, 120, 280, 450, 520, 510, 490, 470, 450, 480, 520, 550, 500, 450, 380, 320, 280, 220, 180, 140],
  gridExport: [0, 0, 0, 0, 0, 0, 0, 50, 120, 150, 180, 200, 220, 250, 280, 300, 280, 220, 150, 80, 30, 10, 5, 0]
}

const mockLoadData = {
  hours: Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`),
  actual: [280, 265, 250, 240, 235, 260, 350, 480, 520, 510, 500, 490, 480, 470, 475, 490, 510, 530, 500, 450, 380, 330, 300, 285],
  predicted: [275, 260, 245, 238, 232, 255, 345, 475, 515, 505, 495, 485, 475, 465, 470, 485, 505, 525, 495, 445, 375, 325, 295, 280],
  baseline: [300, 290, 280, 270, 260, 280, 370, 500, 540, 530, 520, 510, 500, 490, 495, 510, 530, 550, 520, 470, 400, 350, 320, 300]
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    await fetchEnergyData()
    await nextTick()
    initThreeScene()
    initCharts()
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
  ;[gridChartInstance, loadChartInstance].forEach(c => c?.dispose())
  meterChartInstances.forEach(c => c?.dispose())
})

async function fetchEnergyData() {
  try {
    error.value = ''
    loading.value = true

    // 调用真实API
    const [overviewRes, predictionRes, storageRes, suggestionsRes, realtimeRes] = await Promise.all([
      fetch(`${API_BASE}/energy-synergy/overview`),
      fetch(`${API_BASE}/energy-synergy/prediction?hours=24`),
      fetch(`${API_BASE}/energy-synergy/storage/status`),
      fetch(`${API_BASE}/energy-synergy/optimization-suggestions`),
      fetch(`${API_BASE}/energy-synergy/energy-flow-realtime`)
    ])

    if (!overviewRes.ok) throw new Error(`能源概览API请求失败: ${overviewRes.status}`)

    const overview = await overviewRes.json()
    const prediction = predictionRes.ok ? await predictionRes.json() : null
    const storage = storageRes.ok ? await storageRes.json() : null
    const suggestions = suggestionsRes.ok ? await suggestionsRes.json() : { suggestions: [] }
    const realtime = realtimeRes.ok ? await realtimeRes.json() : null

    // 更新实时数据
    const src = overview.source || {}
    realtimeData.value = [
      { label: '光伏出力', value: (src.solar_power || 2450).toFixed(0), unit: ' kW', color: '#00d4aa', icon: 'Sunny' },
      { label: '风电出力', value: (src.wind_power || 1820).toFixed(0), unit: ' kW', color: '#1890ff', icon: 'WindPower' },
      { label: '储能SOC', value: (storage?.batteries?.[0]?.soc || 78.5).toFixed(1), unit: '%', color: '#f39c12', icon: 'Battery' },
      { label: '总负荷', value: (src.total_load || 3280).toFixed(0), unit: ' kW', color: '#ff4d4f', icon: 'Lightning' }
    ]

    // 更新源侧仪表盘
    sourceMeters.value = [
      { title: '光伏发电', value: src.solar_power || 2450, unit: 'kW', color: '#00d4aa', max: src.solar_capacity || 5000 },
      { title: '风电发电', value: src.wind_power || 1820, unit: 'kW', color: '#1890ff', max: src.wind_capacity || 5000 },
      { title: '总出力', value: (src.solar_power || 0) + (src.wind_power || 0), unit: 'kW', color: '#f39c12', max: (src.solar_capacity || 5000) + (src.wind_capacity || 5000) }
    ]

    // 更新储能SOC
    const batteries = storage?.batteries || []
    batterySOC.value = batteries.length > 0 ? batteries.map(b => ({
      name: b.name || '储能',
      soc: b.soc || 78,
      power: b.power || 500,
      capacity: b.capacity || 2000
    })) : [
      { name: '储能A', soc: 78, power: 500, capacity: 2000 },
      { name: '储能B', soc: 65, power: 300, capacity: 1500 },
      { name: '储能C', soc: 92, power: 800, capacity: 3000 }
    ]

    // 更新AI优化建议
    aiSuggestions.value = (suggestions.suggestions || []).map(s => ({
      title: s.title || '优化建议',
      description: s.detail || s.description || '根据数据分析和AI算法生成的优化建议'
    }))

    // 存储API数据供图表使用
    window.__energyOverview = overview
    window.__energyPrediction = prediction
    window.__energyStorage = storage
    window.__energyRealtime = realtime

    console.log('[API] 源网荷储数据加载成功', { overview, prediction, storage, suggestions, realtime })
  } catch (err) {
    error.value = '数据加载失败: ' + err.message
    console.warn('[API] 加载失败，使用mock数据兜底', err)
    // 保持mock数据不变（realtimeData、sourceMeters、batterySOC、aiSuggestions已有默认值）
  } finally {
    loading.value = false
  }
}

function handleTimeRangeChange() {
  console.log('时间范围变化:', timeRange.value)
  fetchEnergyData()
}

function handleEnergyFilter() {
  console.log('能源类型筛选:', selectedEnergyTypes.value)
  // 更新3D场景中显示的能源类型
  updateThreeSceneVisibility()
}

function updateThreeSceneVisibility() {
  if (!threeSceneObj) return
  const scene = threeSceneObj.scene
  scene.traverse((obj) => {
    if (obj.userData && obj.userData.energyType) {
      obj.visible = selectedEnergyTypes.value.includes(obj.userData.energyType)
    }
  })
}

function initThreeScene() {
  if (!threeContainer.value) return

  threeSceneObj = createThreeScene(threeContainer.value, {
    background: 0x0a1628,
    enablePostProcessing: true,
    autoRotate: true,
    autoRotateSpeed: 0.2
  })

  const scene = threeSceneObj.scene

  // 地面
  const groundGeometry = new THREE.PlaneGeometry(300, 300)
  const groundMaterial = new THREE.MeshPhongMaterial({ color: 0x111d33, side: THREE.DoubleSide })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)

  // 网格
  const gridHelper = new THREE.GridHelper(300, 60, 0x1890ff, 0x111d33)
  gridHelper.position.y = 0.01
  scene.add(gridHelper)

  // 创建四象限布局
  createEnergyQuadrants()

  // 相机位置
  threeSceneObj.camera.position.set(80, 60, 80)
  threeSceneObj.controls.target.set(0, 10, 0)

  // 点击事件
  threeContainer.value.addEventListener('click', onThreeClick)
}

function createEnergyQuadrants() {
  if (!threeSceneObj) return
  const scene = threeSceneObj.scene

  // 源侧（左上）：光伏板+风机
  createSolarPanels(scene, -40, 0, -30)
  createWindTurbines(scene, -60, 0, -40)

  // 网侧（右上）：电网交互
  createGridInteraction(scene, 40, 0, -30)

  // 荷侧（左下）：负荷建筑
  createLoadBuildings(scene, -30, 0, 30)

  // 储侧（右下）：储能电池
  createStorageBatteries(scene, 40, 0, 30)

  // 中心枢纽
  createCentralHub(scene, 0, 0, 0)

  // 创建能源流动线
  createEnergyFlows(scene)
}

function createSolarPanels(scene, x, y, z) {
  // 创建光伏板阵列
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const panelGeometry = new THREE.BoxGeometry(8, 0.3, 6)
      const panelMaterial = new THREE.MeshPhongMaterial({
        color: 0x1a1a2e,
        emissive: 0x00d4aa,
        emissiveIntensity: 0.2
      })
      const panel = new THREE.Mesh(panelGeometry, panelMaterial)
      panel.position.set(x + i * 10, y + 2, z + j * 8)
      panel.rotation.x = -Math.PI / 6 // 倾斜角度
      panel.castShadow = true
      panel.userData = { energyType: 'solar', isEnergyDevice: true }
      scene.add(panel)
    }
  }

  // 添加标签
  const labelGeometry = new THREE.SphereGeometry(1.5, 16, 16)
  const labelMaterial = new THREE.MeshBasicMaterial({ color: 0x00d4aa, transparent: true, opacity: 0.7 })
  const label = new THREE.Mesh(labelGeometry, labelMaterial)
  label.position.set(x + 10, y + 8, z + 10)
  label.userData = { energyType: 'solar' }
  scene.add(label)
}

function createWindTurbines(scene, x, y, z) {
  // 创建风机
  for (let i = 0; i < 2; i++) {
    // 塔筒
    const towerGeometry = new THREE.CylinderGeometry(0.5, 0.8, 20, 8)
    const towerMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc })
    const tower = new THREE.Mesh(towerGeometry, towerMaterial)
    tower.position.set(x + i * 15, y + 10, z)
    tower.castShadow = true
    tower.userData = { energyType: 'wind', isEnergyDevice: true }
    scene.add(tower)

    // 机舱
    const nacelleGeometry = new THREE.BoxGeometry(3, 2, 5)
    const nacelleMaterial = new THREE.MeshPhongMaterial({ color: 0xaaaaaa })
    const nacelle = new THREE.Mesh(nacelleGeometry, nacelleMaterial)
    nacelle.position.set(x + i * 15, y + 20, z)
    nacelle.castShadow = true
    scene.add(nacelle)

    // 叶片（简化）
    for (let j = 0; j < 3; j++) {
      const bladeGeometry = new THREE.BoxGeometry(1, 12, 0.2)
      const bladeMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff })
      const blade = new THREE.Mesh(bladeGeometry, bladeMaterial)
      blade.position.set(x + i * 15, y + 20, z)
      blade.rotation.z = (j * Math.PI * 2) / 3
      blade.castShadow = true
      scene.add(blade)
    }
  }
}

function createGridInteraction(scene, x, y, z) {
  // 创建电网交互可视化
  const gridGeometry = new THREE.BoxGeometry(15, 10, 8)
  const gridMaterial = new THREE.MeshPhongMaterial({
    color: 0x1890ff,
    emissive: 0x1890ff,
    emissiveIntensity: 0.2,
    transparent: true,
    opacity: 0.7
  })
  const grid = new THREE.Mesh(gridGeometry, gridMaterial)
  grid.position.set(x, y + 5, z)
  grid.castShadow = true
  grid.userData = { energyType: 'grid', isEnergyDevice: true }
  scene.add(grid)

  // 添加标签
  const labelGeometry = new THREE.SphereGeometry(1.5, 16, 16)
  const labelMaterial = new THREE.MeshBasicMaterial({ color: 0x1890ff, transparent: true, opacity: 0.7 })
  const label = new THREE.Mesh(labelGeometry, labelMaterial)
  label.position.set(x, y + 12, z)
  label.userData = { energyType: 'grid' }
  scene.add(label)
}

function createLoadBuildings(scene, x, y, z) {
  // 创建负荷建筑
  const buildings = [
    { x: x, z: z, w: 12, h: 15, d: 10 },
    { x: x + 20, z: z, w: 15, h: 18, d: 12 },
    { x: x, z: z + 15, w: 10, h: 12, d: 8 }
  ]

  buildings.forEach(b => {
    const geometry = new THREE.BoxGeometry(b.w, b.h, b.d)
    const material = new THREE.MeshPhongMaterial({
      color: 0xff4d4f,
      emissive: 0xff4d4f,
      emissiveIntensity: 0.1,
      transparent: true,
      opacity: 0.8
    })
    const building = new THREE.Mesh(geometry, material)
    building.position.set(b.x, y + b.h / 2, b.z)
    building.castShadow = true
    building.receiveShadow = true
    building.userData = { energyType: 'load', isEnergyDevice: true }
    scene.add(building)

    // 添加窗户灯光效果
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 2; j++) {
        const windowGeometry = new THREE.PlaneGeometry(b.w * 0.2, b.h * 0.1)
        const windowMaterial = new THREE.MeshBasicMaterial({
          color: 0xffcc00,
          transparent: true,
          opacity: 0.6,
          side: THREE.DoubleSide
        })
        const window = new THREE.Mesh(windowGeometry, windowMaterial)
        window.position.set(
          b.x - b.w * 0.3 + i * b.w * 0.3,
          b.y + b.h * 0.3 + j * b.h * 0.3,
          b.d / 2 + 0.1
        )
        scene.add(window)
      }
    }
  })
}

function createStorageBatteries(scene, x, y, z) {
  // 创建储能电池组
  for (let i = 0; i < 3; i++) {
    const battery = createBatteryModel(
      new THREE.Vector3(x + i * 10, y + 7.5, z),
      batterySOC.value[i].soc / 100
    )
    battery.userData = { energyType: 'storage', isEnergyDevice: true }
    scene.add(battery)
  }
}

function createCentralHub(scene, x, y, z) {
  // 创建中心枢纽
  const hubGeometry = new THREE.SphereGeometry(5, 32, 32)
  const hubMaterial = new THREE.MeshPhongMaterial({
    color: 0x111d33,
    emissive: 0x00d4aa,
    emissiveIntensity: 0.3,
    transparent: true,
    opacity: 0.8
  })
  const hub = new THREE.Mesh(hubGeometry, hubMaterial)
  hub.position.set(x, y + 5, z)
  hub.castShadow = true
  scene.add(hub)

  // 添加脉动效果
  threeSceneObj.addAnimationHandler((time) => {
    const scale = 1 + Math.sin(time * 0.002) * 0.1
    hub.scale.set(scale, scale, scale)
  })
}

function createEnergyFlows(scene) {
  // 创建能源流动线
  const flows = [
    { start: new THREE.Vector3(-50, 5, -30), end: new THREE.Vector3(0, 5, 0), color: 0x00d4aa, energyType: 'solar' }, // 源→枢纽
    { start: new THREE.Vector3(50, 5, -30), end: new THREE.Vector3(0, 5, 0), color: 0x1890ff, energyType: 'grid' }, // 网→枢纽
    { start: new THREE.Vector3(0, 5, 0), end: new THREE.Vector3(-30, 5, 30), color: 0xff4d4f, energyType: 'load' }, // 枢纽→荷
    { start: new THREE.Vector3(0, 5, 0), end: new THREE.Vector3(50, 5, 30), color: 0xf39c12, energyType: 'storage' } // 枢纽→储
  ]

  flows.forEach(flow => {
    const flowLine = createFlowLine(flow.start, flow.end, {
      particleCount: 40,
      color: flow.color,
      lineColor: 0x1890ff
    })
    flowLine.userData = { energyType: flow.energyType, isEnergyDevice: true }
    scene.add(flowLine)

    // 添加动画更新
    threeSceneObj.addAnimationHandler((time) => {
      if (flowLine.userData.update) {
        flowLine.userData.update(time)
      }
    })
  })
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
    if (obj.userData && obj.userData.isEnergyDevice) {
      console.log('点击了能源设备:', obj.userData.energyType)
      // 这里可以显示设备详情
    }
  }
}

function initCharts() {
  // 源侧仪表盘
  nextTick(() => {
    const meterRefs = document.querySelectorAll('.meter-chart')
    meterRefs.forEach((ref, idx) => {
      if (ref && sourceMeters.value[idx]) {
        const meter = sourceMeters.value[idx]
        const chart = markRaw(echarts.init(ref))
        meterChartInstances.push(chart)

        chart.setOption({
          series: [{
            type: 'gauge',
            startAngle: 200,
            endAngle: -20,
            min: 0,
            max: meter.max,
            itemWidth: 10,
            itemHeight: 10,
            axisLine: {
              lineStyle: {
                width: 8,
                color: [
                  [0.3, '#00d4aa'],
                  [0.7, '#f39c12'],
                  [1, '#ff4d4f']
                ]
              }
            },
            pointer: { itemStyle: { color: 'auto' } },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            title: { show: false },
            detail: {
              valueAnimation: true,
              formatter: '{value}',
              color: meter.color,
              fontSize: 14,
              fontWeight: 'bold',
              offsetCenter: [0, '40%']
            },
            data: [{ value: meter.value }]
          }]
        })
      }
    })
  })

  // 网侧：电网交互图
  if (gridChart.value) {
    gridChartInstance = markRaw(echarts.init(gridChart.value))
    gridChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#1890ff',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        data: ['市电输入', '余电上网'],
        bottom: 0,
        textStyle: { fontSize: 10, color: '#909399' },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 8
      },
      grid: { left: '8%', right: '4%', bottom: '18%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: mockGridData.hours,
        axisLabel: { fontSize: 8, color: '#606266', rotate: 30 },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      yAxis: {
        type: 'value',
        name: 'kW',
        nameTextStyle: { fontSize: 9, color: '#909399' },
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      series: [
        {
          name: '市电输入',
          type: 'bar',
          data: mockGridData.gridImport,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24,144,255,0.8)' },
              { offset: 1, color: 'rgba(24,144,255,0.1)' }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: '40%'
        },
        {
          name: '余电上网',
          type: 'bar',
          data: mockGridData.gridExport,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0,212,170,0.8)' },
              { offset: 1, color: 'rgba(0,212,170,0.1)' }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: '40%'
        }
      ],
      animationDuration: 1000
    })
  }

  // 荷侧：负荷曲线图
  if (loadChart.value) {
    loadChartInstance = markRaw(echarts.init(loadChart.value))
    loadChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#ff4d4f',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        data: ['实际负荷', '预测负荷', '基准负荷'],
        bottom: 0,
        textStyle: { fontSize: 10, color: '#909399' },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 8
      },
      grid: { left: '8%', right: '4%', bottom: '18%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: mockLoadData.hours,
        axisLabel: { fontSize: 8, color: '#606266', rotate: 30 },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      yAxis: {
        type: 'value',
        name: 'kW',
        nameTextStyle: { fontSize: 9, color: '#909399' },
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      series: [
        {
          name: '实际负荷',
          type: 'line',
          smooth: true,
          data: mockLoadData.actual,
          itemStyle: { color: '#ff4d4f' },
          lineStyle: { width: 2 },
          symbol: 'circle',
          symbolSize: 3
        },
        {
          name: '预测负荷',
          type: 'line',
          smooth: true,
          data: mockLoadData.predicted,
          itemStyle: { color: '#1890ff' },
          lineStyle: { width: 2, type: 'dashed' },
          symbol: 'circle',
          symbolSize: 3
        },
        {
          name: '基准负荷',
          type: 'line',
          smooth: true,
          data: mockLoadData.baseline,
          itemStyle: { color: '#909399' },
          lineStyle: { width: 1, type: 'dotted' },
          symbol: 'none'
        }
      ],
      animationDuration: 1200
    })
  }

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  ;[gridChartInstance, loadChartInstance].forEach(c => c?.resize())
  meterChartInstances.forEach(c => c?.resize())
}
</script>

<style scoped>
.energy-synergy {
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

/* 实时数据网格 */
.realtime-grid { display: flex; flex-direction: column; gap: 8px; }
.rt-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; background: rgba(255,255,255,0.03);
  border-radius: 6px; font-size: 12px;
}
.rt-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
}
.rt-info { flex: 1; }
.rt-value { font-size: 14px; font-weight: 700; }
.rt-label { font-size: 10px; color: #909399; margin-top: 2px; }

/* AI优化建议 */
.ai-suggestions { display: flex; flex-direction: column; gap: 8px; }
.suggestion-item {
  display: flex; gap: 8px; padding: 8px;
  background: rgba(0, 212, 170, 0.05); border-radius: 6px;
  border: 1px solid rgba(0, 212, 170, 0.15); font-size: 11px;
}
.suggestion-icon {
  color: #00d4aa; flex-shrink: 0; margin-top: 2px;
}
.suggestion-content { flex: 1; }
.suggestion-title { color: #e0e0e0; font-weight: 600; margin-bottom: 4px; }
.suggestion-desc { color: #909399; line-height: 1.5; }

/* 中央3D区域 */
.center-3d {
  flex: 1; position: relative;
  border-radius: 12px; overflow: hidden;
  background: #0a1628; border: 1px solid #111d33;
}
.three-container { width: 100%; height: 100%; }

/* 象限标签 */
.quadrant-labels { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
.quadrant-label {
  position: absolute; font-size: 14px; font-weight: 700; color: #1890ff;
  text-align: center; line-height: 1.4;
}
.quadrant-label span { font-size: 11px; font-weight: 400; color: #909399; }

/* 场景提示 */
.scene-hint {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  background: rgba(17, 29, 51, 0.85); border-radius: 8px;
  padding: 8px 16px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2);
  font-size: 11px; color: #909399; display: flex; align-items: center; gap: 6px;
  white-space: nowrap; pointer-events: none;
}

/* 右侧面板 */
.right-panel {
  width: 320px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px;
  overflow-y: auto; gap: 12px;
}

/* 源侧仪表盘 */
.source-meters { display: flex; flex-direction: column; gap: 12px; }
.meter-item {
  background: rgba(255,255,255,0.03); border-radius: 8px;
  padding: 10px; text-align: center;
}
.meter-title { font-size: 11px; color: #909399; margin-bottom: 4px; }
.meter-chart { height: 100px; }
.meter-value { font-size: 16px; font-weight: 700; margin-top: 4px; }

/* 网侧/荷侧图表 */
.grid-interaction, .load-chart { flex: 1; }
.chart-container { height: 180px; }

/* 储侧SOC */
.storage-soc { display: flex; flex-direction: column; gap: 10px; }
.soc-item {
  background: rgba(255,255,255,0.03); border-radius: 6px;
  padding: 8px 10px;
}
.soc-header {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; color: #c0c4cc; margin-bottom: 6px;
}
.soc-value { font-weight: 700; }
.soc-bar {
  width: 100%; height: 8px; background: #1a2a3a; border-radius: 4px;
  overflow: hidden; margin-bottom: 4px;
}
.soc-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.soc-meta {
  display: flex; justify-content: space-between; font-size: 10px; color: #909399;
}

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: transparent; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb {
  background: #1890ff; border-radius: 2px;
}
</style>
