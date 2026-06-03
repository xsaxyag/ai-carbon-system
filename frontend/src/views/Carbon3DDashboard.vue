<template>
  <div class="carbon-3d-dashboard">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载3D碳全景大屏...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <el-alert :title="error" type="error" show-icon :closable="false" />
      <el-button @click="fetchAllData" type="primary" style="margin-top: 12px;">重试</el-button>
    </div>

    <!-- 主体布局 -->
    <div v-show="!loading" class="dashboard-layout">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <!-- 核心指标卡片 -->
        <div class="stats-cards">
          <div
            v-for="(card, idx) in statCards"
            :key="idx"
            class="stat-card"
            :style="{ borderLeft: '4px solid ' + card.color }"
          >
            <div class="stat-value" :style="{ color: card.color }">
              {{ card.value }}<span class="stat-unit">{{ card.unit }}</span>
            </div>
            <div class="stat-label">{{ card.label }}</div>
            <div v-if="card.trend !== undefined" class="stat-trend">
              <span :class="card.trend >= 0 ? 'trend-up' : 'trend-down'">
                {{ card.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(card.trend) }}%
              </span>
              <span class="trend-label">较上月</span>
            </div>
          </div>
        </div>

        <!-- ECharts 3D饼图 - Scope占比 -->
        <div class="chart-panel">
          <div class="panel-header">
            <span class="panel-title"><el-icon><PieChart /></el-icon> Scope 1/2/3 排放占比</span>
          </div>
          <div ref="pie3DChart" class="chart-container"></div>
        </div>

        <!-- 排放趋势图 -->
        <div class="chart-panel">
          <div class="panel-header">
            <span class="panel-title"><el-icon><TrendCharts /></el-icon> 碳排放趋势</span>
          </div>
          <div ref="trendChart" class="chart-container"></div>
        </div>
      </div>

      <!-- 中央3D场景 -->
      <div class="center-3d">
        <div ref="threeContainer" class="three-container"></div>
        <!-- 悬浮信息 -->
        <div class="scene-info">
          <div class="info-item">
            <span class="info-label">场景</span>
            <span class="info-value">{{ sceneMode === 'earth' ? '3D地球' : '园区俯瞰' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">粒子数</span>
            <span class="info-value">{{ particleCount }}</span>
          </div>
        </div>
        <!-- 场景切换按钮 -->
        <div class="scene-switcher">
          <el-button
            v-for="mode in sceneModes"
            :key="mode.value"
            :type="sceneMode === mode.value ? 'primary' : 'default'"
            size="small"
            @click="switchScene(mode.value)"
            round
          >
            {{ mode.label }}
          </el-button>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- 实时热力图 -->
        <div class="chart-panel full-height">
          <div class="panel-header">
            <span class="panel-title"><el-icon><Histogram /></el-icon> 区域碳排放热力</span>
          </div>
          <div ref="heatmapChart" class="chart-container"></div>
        </div>

        <!-- 排放源排行 -->
        <div class="chart-panel">
          <div class="panel-header">
            <span class="panel-title"><el-icon><Promotion /></el-icon> 排放源排行</span>
          </div>
          <div ref="rankChart" class="chart-container small"></div>
        </div>

        <!-- 碳资产价值 -->
        <div class="chart-panel">
          <div class="panel-header">
            <span class="panel-title"><el-icon><Promotion /></el-icon> 碳资产价值</span>
          </div>
          <div class="asset-value">
            <div class="asset-number">¥ {{ assetValue }}</div>
            <div class="asset-label">预估碳资产价值</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'
import { PieChart, TrendCharts, Histogram, Promotion } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import {
  createThreeScene,
  createCarbonBar,
  createHeatParticle,
  latLonToVector3
} from '../utils/three-scene'

// 状态
const loading = ref(true)
const error = ref('')
const sceneMode = ref('earth')
const particleCount = ref(0)
const assetValue = ref('0')

// DOM引用
const threeContainer = ref(null)
const pie3DChart = ref(null)
const trendChart = ref(null)
const heatmapChart = ref(null)
const rankChart = ref(null)

// 3D场景对象
let threeSceneObj = null
let particleSystem = null
let animationFrameId = null

// 图表实例
let pieChartInstance = null
let trendChartInstance = null
let heatmapInstance = null
let rankChartInstance = null

// 数据
const statCards = ref([
  { label: '总排放量', value: '0', unit: 'tCO₂e', color: '#ff4d4f', trend: 5.2 },
  { label: '减碳率', value: '0', unit: '%', color: '#00d4aa', trend: 12.5 },
  { label: '绿电占比', value: '0', unit: '%', color: '#1890ff', trend: 8.3 },
  { label: '碳资产价值', value: '0', unit: '万元', color: '#f39c12', trend: undefined }
])

const sceneModes = [
  { label: '3D地球', value: 'earth' },
  { label: '园区俯瞰', value: 'park' }
]

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    await fetchAllData()
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
  ;[pieChartInstance, trendChartInstance, heatmapInstance, rankChartInstance].forEach(c => {
    c?.dispose()
  })
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  window.removeEventListener('resize', handleResize)
})

async function fetchAllData() {
  try {
    const [dashboardRes, scopeRes] = await Promise.all([
      fetch(`${API_BASE}/api/carbon-3d/dashboard`),
      fetch(`${API_BASE}/api/carbon-3d/scope-distribution`)
    ])
    if (!dashboardRes.ok) throw new Error(`dashboard API ${dashboardRes.status}`)
    if (!scopeRes.ok) throw new Error(`scope API ${scopeRes.status}`)
    const dashboard = await dashboardRes.json()
    const scopeData = await scopeRes.json()

    // 统计卡片 (后端 snake_case → 前端显示)
    statCards.value[0].value = (dashboard.total_emissions / 1000).toFixed(1)
    statCards.value[1].value = dashboard.reduction_rate.toFixed(1)
    statCards.value[2].value = dashboard.green_power_ratio.toFixed(1)
    const assetWan = dashboard.carbon_asset_value / 10000
    statCards.value[3].value = assetWan.toFixed(1)
    assetValue.value = assetWan.toFixed(1)

    // Scope 饼图数据
    const scopePieData = [
      {
        value: scopeData.scope1.total,
        name: 'Scope 1 直接排放',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#e74c3c' },
            { offset: 1, color: '#c0392b' }
          ])
        }
      },
      {
        value: scopeData.scope2.total,
        name: 'Scope 2 能源间接',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f39c12' },
            { offset: 1, color: '#e67e22' }
          ])
        }
      },
      {
        value: scopeData.scope3.total,
        name: 'Scope 3 其他间接',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#27ae60' },
            { offset: 1, color: '#2ecc71' }
          ])
        }
      }
    ]

    // 趋势数据
    const monthly = dashboard.monthly_trend || []
    const trendMonths = monthly.map(m => m.month)
    const trendS1 = monthly.map(m => m.scope1)
    const trendS2 = monthly.map(m => m.scope2)
    const trendS3 = monthly.map(m => m.scope3)

    // 区域热力数据
    const regional = dashboard.regional_data || []
    const areas = regional.map(z => z.name)
    const values = regional.map(z => z.emissions)

    window.__carbonData = {
      summary: {
        totalEmission: dashboard.total_emissions,
        reductionRate: dashboard.reduction_rate,
        greenPowerRatio: dashboard.green_power_ratio,
        assetValue: assetWan
      },
      scopeData: scopePieData,
      trendData: { months: trendMonths, scope1: trendS1, scope2: trendS2, scope3: trendS3 },
      heatData: { areas, values }
    }
  } catch (err) {
    error.value = '数据加载失败: ' + err.message
    throw err
  }
}

function initThreeScene() {
  if (!threeContainer.value) return

  threeSceneObj = createThreeScene(threeContainer.value, {
    background: 0x0a1628,
    enablePostProcessing: true,
    autoRotate: true,
    autoRotateSpeed: 0.3
  })

  if (sceneMode.value === 'earth') {
    createEarthScene()
  } else {
    createParkScene()
  }

  particleSystem = createHeatParticle(500, { spread: 80, color: 0xff4d4f })
  threeSceneObj.scene.add(particleSystem)
  particleCount.value = 500

  threeSceneObj.addAnimationHandler(() => {
    if (particleSystem && particleSystem.userData.originalPositions) {
      const positions = particleSystem.geometry.attributes.position.array
      const original = particleSystem.userData.originalPositions
      for (let i = 0; i < positions.length / 3; i++) {
        positions[i * 3 + 1] = original[i * 3 + 1] + Math.sin(Date.now() * 0.001 + i) * 2
      }
      particleSystem.geometry.attributes.position.needsUpdate = true
    }
  })
}

function createEarthScene() {
  const scene = threeSceneObj.scene
  const earthGeometry = new THREE.SphereGeometry(50, 64, 64)
  const earthMaterial = new THREE.MeshPhongMaterial({
    color: 0x111d33,
    emissive: 0x0a1628,
    emissiveIntensity: 0.3,
    specular: 0x222222,
    shininess: 5
  })
  const earth = new THREE.Mesh(earthGeometry, earthMaterial)
  earth.rotation.x = Math.PI / 6
  scene.add(earth)

  const wireframe = new THREE.WireframeGeometry(earthGeometry)
  const lineMaterial = new THREE.LineBasicMaterial({
    color: 0x1890ff,
    transparent: true,
    opacity: 0.15
  })
  const wireframeMesh = new THREE.LineSegments(wireframe, lineMaterial)
  wireframeMesh.rotation.x = Math.PI / 6
  scene.add(wireframeMesh)

  const cityData = [
    { lat: 31.23, lon: 121.47, value: 1200 },
    { lat: 39.90, lon: 116.40, value: 980 },
    { lat: 23.13, lon: 113.26, value: 750 },
    { lat: 22.54, lon: 114.06, value: 680 },
    { lat: 30.57, lon: 104.07, value: 520 },
    { lat: 34.34, lon: 108.94, value: 430 }
  ]

  cityData.forEach(city => {
    const pos = latLonToVector3(city.lat, city.lon, 50.5)
    const bar = createCarbonBar(pos.x * 0.3, 0, pos.z * 0.3, city.value, {
      maxHeight: 20,
      maxValue: 1500,
      width: 1,
      depth: 1
    })
    bar.position.copy(pos.clone().multiplyScalar(0.3))
    bar.position.y = 0
    scene.add(bar)
  })

  threeSceneObj.camera.position.set(0, 80, 120)
}

function createParkScene() {
  const scene = threeSceneObj.scene
  const groundGeometry = new THREE.PlaneGeometry(200, 200)
  const groundMaterial = new THREE.MeshPhongMaterial({
    color: 0x111d33,
    side: THREE.DoubleSide
  })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)

  const gridHelper = new THREE.GridHelper(200, 50, 0x1890ff, 0x111d33)
  gridHelper.position.y = 0.01
  scene.add(gridHelper)

  const buildings = [
    { x: -30, z: -20, w: 15, h: 25, d: 15, emission: 800 },
    { x: 0, z: -20, w: 20, h: 30, d: 15, emission: 1200 },
    { x: 35, z: -20, w: 12, h: 20, d: 12, emission: 600 },
    { x: -30, z: 20, w: 18, h: 22, d: 14, emission: 950 },
    { x: 10, z: 25, w: 25, h: 18, d: 18, emission: 1500 },
    { x: 40, z: 15, w: 10, h: 15, d: 10, emission: 300 }
  ]

  buildings.forEach(b => {
    const color = b.emission > 1000 ? 0xff4d4f : b.emission > 500 ? 0xf39c12 : 0x00d4aa
    const geometry = new THREE.BoxGeometry(b.w, b.h, b.d)
    const material = new THREE.MeshPhongMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.15,
      transparent: true,
      opacity: 0.88
    })
    const building = new THREE.Mesh(geometry, material)
    building.position.set(b.x, b.h / 2, b.z)
    building.castShadow = true
    building.receiveShadow = true
    scene.add(building)

    const labelGeometry = new THREE.SphereGeometry(1.5, 16, 16)
    const labelMaterial = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 0.7
    })
    const label = new THREE.Mesh(labelGeometry, labelMaterial)
    label.position.set(b.x, b.h + 3, b.z)
    scene.add(label)
  })

  threeSceneObj.camera.position.set(80, 60, 80)
  threeSceneObj.controls.target.set(5, 10, 0)
}

function switchScene(mode) {
  sceneMode.value = mode
  if (threeSceneObj) {
    const scene = threeSceneObj.scene
    while (scene.children.length > 0) {
      const obj = scene.children[0]
      if (obj.geometry) obj.geometry.dispose()
      if (obj.material) obj.material.dispose()
      scene.remove(obj)
    }
    if (mode === 'earth') {
      createEarthScene()
    } else {
      createParkScene()
    }
    if (particleSystem) {
      scene.add(particleSystem)
    }
  }
}

function initCharts() {
  if (pie3DChart.value) {
    pieChartInstance = markRaw(echarts.init(pie3DChart.value))
    const data = window.__carbonData?.scopeData || []
    pieChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} tCO₂e ({d}%)',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#00d4aa',
        textStyle: { color: '#fff', fontSize: 12 }
      },
      series: [{
        type: 'pie',
        radius: ['25%', '65%'],
        center: ['50%', '50%'],
        data: data,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#0a1628',
          borderWidth: 2
        },
        label: {
          formatter: '{b}\n{d}%',
          fontSize: 10,
          color: '#c0c4cc'
        },
        emphasis: {
          label: { fontSize: 14, fontWeight: 'bold' },
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(0,212,170,0.5)'
          }
        },
        animationType: 'scale',
        animationEasing: 'elasticOut',
        animationDelay: (idx) => idx * 200
      }]
    })
  }

  if (trendChart.value) {
    trendChartInstance = markRaw(echarts.init(trendChart.value))
    const td = window.__carbonData?.trendData || { months: [], scope1: [], scope2: [], scope3: [] }
    trendChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#1890ff',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        data: ['Scope 1', 'Scope 2', 'Scope 3'],
        bottom: 0,
        textStyle: { fontSize: 10, color: '#909399' },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 8
      },
      grid: { left: '8%', right: '4%', bottom: '18%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: td.months,
        axisLabel: { fontSize: 9, color: '#606266', rotate: 30 },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      yAxis: {
        type: 'value',
        name: 'tCO₂e',
        nameTextStyle: { fontSize: 9, color: '#606266' },
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      series: [
        {
          name: 'Scope 1', type: 'line', smooth: true, data: td.scope1,
          itemStyle: { color: '#e74c3c' },
          lineStyle: { width: 2 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(231,76,60,0.3)' }, { offset: 1, color: 'rgba(231,76,60,0.01)' }]) },
          symbol: 'circle', symbolSize: 5
        },
        {
          name: 'Scope 2', type: 'line', smooth: true, data: td.scope2,
          itemStyle: { color: '#f39c12' },
          lineStyle: { width: 2 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(243,156,18,0.3)' }, { offset: 1, color: 'rgba(243,156,18,0.01)' }]) },
          symbol: 'circle', symbolSize: 5
        },
        {
          name: 'Scope 3', type: 'line', smooth: true, data: td.scope3,
          itemStyle: { color: '#27ae60' },
          lineStyle: { width: 2 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(39,174,96,0.3)' }, { offset: 1, color: 'rgba(39,174,96,0.01)' }]) },
          symbol: 'circle', symbolSize: 5
        }
      ],
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    })
  }

  if (heatmapChart.value) {
    heatmapInstance = markRaw(echarts.init(heatmapChart.value))
    const hd = window.__carbonData?.heatData || { areas: [], values: [] }
    heatmapInstance.setOption({
      tooltip: {
        formatter: '{b}: {c} tCO₂e',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#00d4aa',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      grid: { left: '12%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'tCO₂e',
        nameTextStyle: { fontSize: 9, color: '#606266' },
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      yAxis: {
        type: 'category',
        data: hd.areas,
        axisLabel: { fontSize: 10, color: '#c0c4cc' },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      series: [{
        type: 'bar',
        data: hd.values.map((v, i) => ({
          value: v,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: v > 2000 ? '#ff4d4f' : v > 500 ? '#f39c12' : '#00d4aa' },
              { offset: 1, color: v > 2000 ? '#c0392b' : v > 500 ? '#e67e22' : '#27ae60' }
            ])
          }
        })),
        itemStyle: { borderRadius: [0, 6, 6, 0] },
        barWidth: '60%',
        label: { show: true, position: 'right', fontSize: 9, color: '#c0c4cc' },
        animationDuration: 1200,
        animationEasing: 'elasticOut',
        animationDelay: (idx) => idx * 120
      }]
    })
  }

  if (rankChart.value) {
    rankChartInstance = markRaw(echarts.init(rankChart.value))
    const sources = [
      { name: '天然气燃烧', value: 4520 },
      { name: '外购电力', value: 3890 },
      { name: '汽油使用', value: 1260 },
      { name: '柴油使用', value: 980 },
      { name: '垃圾处理', value: 520 },
      { name: '商务航班', value: 670 }
    ]
    rankChartInstance.setOption({
      tooltip: {
        formatter: '{b}: {c} tCO₂e',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#1890ff',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      grid: { left: '15%', right: '8%', bottom: '3%', top: '5%', containLabel: true },
      xAxis: {
        type: 'value',
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      yAxis: {
        type: 'category',
        data: sources.map(s => s.name).reverse(),
        axisLabel: { fontSize: 9, color: '#c0c4cc' },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      series: [{
        type: 'bar',
        data: sources.map(s => s.value).reverse(),
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        barWidth: '50%',
        label: { show: true, position: 'right', fontSize: 9, color: '#c0c4cc' },
        animationDuration: 1000,
        animationDelay: (idx) => idx * 100
      }]
    })
  }

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  ;[pieChartInstance, trendChartInstance, heatmapInstance, rankChartInstance].forEach(c => {
    c?.resize()
  })
}
</script>




<style scoped>
.carbon-3d-dashboard {
  width: 100%;
  height: 100vh;
  background: #0a1628;
  position: relative;
  overflow: hidden;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 加载状态 */
.loading-wrapper {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(10, 22, 40, 0.95);
  z-index: 1000;
}
.loading-spinner {
  width: 60px; height: 60px;
  border: 4px solid rgba(0, 212, 170, 0.2);
  border-top: 4px solid #00d4aa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: #00d4aa; margin-top: 20px; font-size: 16px; letter-spacing: 2px; }

/* 错误提示 */
.error-banner {
  position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
  z-index: 1001; min-width: 400px; text-align: center;
}

/* 主体布局 */
.dashboard-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  padding: 12px;
  gap: 12px;
}

/* 左侧面板 */
.left-panel {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}
.stats-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.stat-card {
  background: #111d33;
  border-radius: 10px;
  padding: 12px;
  transition: all 0.3s ease;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0, 212, 170, 0.15); }
.stat-value { font-size: 22px; font-weight: 800; }
.stat-unit { font-size: 11px; margin-left: 3px; font-weight: 400; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }
.stat-trend { font-size: 10px; margin-top: 4px; }
.trend-up { color: #f56c6c; font-weight: 600; }
.trend-down { color: #67c23a; font-weight: 600; }
.trend-label { color: #606266; margin-left: 3px; }

/* 图表面板 */
.chart-panel {
  background: #111d33;
  border-radius: 10px;
  padding: 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 180px;
}
.chart-panel.full-height { flex: 1.5; }
.panel-header { margin-bottom: 8px; }
.panel-title {
  font-size: 13px; font-weight: 600; color: #c0c4cc;
  display: flex; align-items: center; gap: 5px;
}
.chart-container { flex: 1; min-height: 140px; }
.chart-container.small { min-height: 120px; }

/* 中央3D区域 */
.center-3d {
  flex: 1;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: #0a1628;
  border: 1px solid #111d33;
}
.three-container {
  width: 100%; height: 100%;
}

/* 场景信息 */
.scene-info {
  position: absolute; top: 12px; left: 12px;
  background: rgba(17, 29, 51, 0.85); border-radius: 8px;
  padding: 8px 14px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2);
}
.info-item { display: flex; gap: 8px; font-size: 11px; margin: 3px 0; }
.info-label { color: #606266; }
.info-value { color: #00d4aa; font-weight: 600; }

/* 场景切换 */
.scene-switcher {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px;
  background: rgba(17, 29, 51, 0.85); border-radius: 20px;
  padding: 6px 14px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 144, 255, 0.2);
}

/* 右侧面板 */
.right-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

/* 碳资产价值 */
.asset-value {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.asset-number {
  font-size: 32px; font-weight: 800; color: #f39c12;
  text-shadow: 0 0 20px rgba(243, 156, 18, 0.4);
}
.asset-label { font-size: 12px; color: #909399; margin-top: 6px; }

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: transparent; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb {
  background: #1890ff; border-radius: 2px;
}
</style>
