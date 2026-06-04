<template>
  <div class="digital-twin-factory">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载数字孪生工厂...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <el-alert :title="error" type="error" show-icon :closable="false" />
    </div>

    <div v-show="!loading" class="main-layout">
      <!-- 左侧控制面板 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><Promotion /></el-icon> 控制面板</span>
        </div>

        <!-- 视图切换 -->
        <div class="control-section">
          <div class="section-label">视图模式</div>
          <el-radio-group v-model="viewMode" @change="switchView" size="small" style="width: 100%;">
            <el-radio-button label="global" style="width:33%;">全局</el-radio-button>
            <el-radio-button label="workshop" style="width:33%;">车间</el-radio-button>
            <el-radio-button label="line" style="width:34%;">产线</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 时间范围筛选 -->
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

        <!-- 工厂区域列表 -->
        <div class="control-section">
          <div class="section-label">工厂区域</div>
          <div class="zone-list">
            <div
              v-for="zone in factoryZones"
              :key="zone.id"
              class="zone-item"
              :class="{ active: selectedZone?.id === zone.id }"
              @click="selectZone(zone)"
            >
              <div class="zone-color" :style="{ background: zone.color }"></div>
              <div class="zone-info">
                <div class="zone-name">{{ zone.name }}</div>
                <div class="zone-emission">{{ zone.emission }} kgCO₂/h</div>
              </div>
              <div class="zone-status" :class="zone.status">
                {{ zone.status === 'normal' ? '正常' : zone.status === 'warning' ? '预警' : '超标' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 实时数据 -->
        <div class="control-section">
          <div class="section-label">实时数据</div>
          <div class="realtime-data">
            <div class="data-item" v-for="(item, idx) in realtimeData" :key="idx">
              <div class="data-label">{{ item.label }}</div>
              <div class="data-value" :style="{ color: item.color }">{{ item.value }}{{ item.unit }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央3D场景 -->
      <div class="center-3d">
        <div ref="threeContainer" class="three-container"></div>

        <!-- 悬浮信息 -->
        <div v-if="hoveredZone" class="hover-info">
          <div class="hover-title">{{ hoveredZone.name }}</div>
          <div class="hover-data">
            <div>实时排放: {{ hoveredZone.emission }} kgCO₂/h</div>
            <div>碳强度: {{ hoveredZone.intensity }} kgCO₂/万元</div>
            <div>状态:
              <span :style="{ color: hoveredZone.status === 'normal' ? '#00d4aa' : '#ff4d4f' }">
                {{ hoveredZone.status === 'normal' ? '正常' : hoveredZone.status === 'warning' ? '预警' : '超标' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 图例 -->
        <div class="legend">
          <div class="legend-title">排放强度</div>
          <div class="legend-bar"></div>
          <div class="legend-labels">
            <span>低</span>
            <span>中</span>
            <span>高</span>
          </div>
        </div>
      </div>

      <!-- 右侧详情面板 -->
      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><InfoFilled /></el-icon> 区域详情</span>
        </div>

        <div v-if="selectedZone" class="zone-detail">
          <div class="detail-header" :style="{ borderLeft: '4px solid ' + selectedZone.color }">
            <div class="detail-name">{{ selectedZone.name }}</div>
            <div class="detail-status" :class="selectedZone.status">
              {{ selectedZone.status === 'normal' ? '正常' : selectedZone.status === 'warning' ? '预警' : '超标' }}
            </div>
          </div>

          <div class="detail-meta">
            <div class="meta-item">
              <span class="meta-label">实时排放</span>
              <span class="meta-value" :style="{ color: selectedZone.color }">{{ selectedZone.emission }} kgCO₂/h</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">碳强度</span>
              <span class="meta-value">{{ selectedZone.intensity }} kgCO₂/万元</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">能耗</span>
              <span class="meta-value">{{ selectedZone.energy }} kWh</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">面积</span>
              <span class="meta-value">{{ selectedZone.area }} m²</span>
            </div>
          </div>

          <!-- 排放趋势 -->
          <div class="detail-chart">
            <div class="chart-title">24小时排放趋势</div>
            <div ref="trendChart" class="chart-container"></div>
          </div>

          <!-- 能源结构 -->
          <div class="detail-chart">
            <div class="chart-title">能源结构</div>
            <div ref="energyChart" class="chart-container small"></div>
          </div>
        </div>

        <div v-else class="no-selection">
          <el-icon :size="48"><Promotion /></el-icon>
          <div style="margin-top: 12px; color: #606266;">请在左侧选择工厂区域</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
import * as echarts from 'echarts'
import { Promotion, InfoFilled } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import * as THREE from 'three'
import { createThreeScene, createFactoryBuilding, createFlowLine } from '../utils/three-scene'

// 状态
const loading = ref(true)
const error = ref('')
const viewMode = ref('global')
const timeRange = ref('')
const selectedZone = ref(null)
const hoveredZone = ref(null)

// DOM引用
const threeContainer = ref(null)
const trendChart = ref(null)
const energyChart = ref(null)

// 3D场景
let threeSceneObj = null

// 图表实例
let trendChartInstance = null
let energyChartInstance = null

// 工厂区域数据
const factoryZones = ref([
  { id: 1, name: '生产车间A', emission: 320, intensity: 45.2, energy: 580, area: 2500, status: 'normal', color: '#00d4aa' },
  { id: 2, name: '生产车间B', emission: 480, intensity: 68.7, energy: 820, area: 3000, status: 'warning', color: '#f39c12' },
  { id: 3, name: '仓库', emission: 120, intensity: 18.5, energy: 150, area: 5000, status: 'normal', color: '#00d4aa' },
  { id: 4, name: '办公楼', emission: 85, intensity: 12.3, energy: 120, area: 1800, status: 'normal', color: '#00d4aa' },
  { id: 5, name: '研发中心', emission: 65, intensity: 9.8, energy: 95, area: 1200, status: 'normal', color: '#00d4aa' },
  { id: 6, name: '污水处理站', emission: 280, intensity: 120.5, energy: 350, area: 800, status: 'danger', color: '#ff4d4f' }
])

// 实时数据
const realtimeData = ref([
  { label: '总排放', value: '1,350', unit: ' kgCO₂/h', color: '#ff4d4f' },
  { label: '总能耗', value: '2,115', unit: ' kWh', color: '#1890ff' },
  { label: '绿电占比', value: '42.3', unit: '%', color: '#00d4aa' },
  { label: '碳强度', value: '52.8', unit: ' kgCO₂/万元', color: '#f39c12' }
])

// 模拟数据
const mockTrendData = {
  hours: Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`),
  values: [280, 265, 250, 240, 235, 260, 350, 480, 520, 510, 500, 490, 480, 470, 475, 490, 510, 530, 500, 450, 380, 330, 300, 285]
}

const mockEnergyData = [
  { name: '电力', value: 58, color: '#1890ff' },
  { name: '天然气', value: 27, color: '#f39c12' },
  { name: '蒸汽', value: 10, color: '#00d4aa' },
  { name: '其他', value: 5, color: '#909399' }
]

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    await fetchFactoryData()
    await nextTick()
    initThreeScene()
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
  ;[trendChartInstance, energyChartInstance].forEach(c => c?.dispose())
})

async function fetchFactoryData() {
  try {
    error.value = ''
    loading.value = true

    // 调用真实API
    const [zonesRes, emissionsRes] = await Promise.all([
      fetch(`${API_BASE}/digital-twin/factory/zones`),
      fetch(`${API_BASE}/digital-twin/factory/emissions?hours=24`)
    ])

    if (!zonesRes.ok) throw new Error(`工厂区域API请求失败: ${zonesRes.status}`)
    if (!emissionsRes.ok) throw new Error(`排放数据API请求失败: ${emissionsRes.status}`)

    const zonesData = await zonesRes.json()
    const emissionsData = await emissionsRes.json()

    // 更新工厂区域数据
    const statusMap = { operating: 'normal', alert: 'danger', standby: 'warning' }
    factoryZones.value = (zonesData.zones || []).map((z, idx) => ({
      id: z.id || idx,
      name: z.name || `区域${idx + 1}`,
      status: statusMap[z.status] || 'normal',
      carbonRate: z.carbon_rate || (200 + Math.random() * 100).toFixed(1),
      trend: z.trend || (Math.random() * 10 - 3).toFixed(1),
      temperature: z.temperature || (65 + Math.random() * 15).toFixed(1),
      utilization: z.utilization || (70 + Math.random() * 20).toFixed(1)
    }))

    // 更新实时数据
    realtimeData.value = [
      { label: '总排放', value: (emissionsData.total_emissions || 1820).toFixed(0), unit: ' kgCO₂/h', color: '#ff4d4f', icon: 'TrendCharts' },
      { label: '光伏发电', value: (emissionsData.solar_power || 450).toFixed(0), unit: ' kW', color: '#00d4aa', icon: 'Sunny' },
      { label: '风电发电', value: (emissionsData.wind_power || 320).toFixed(0), unit: ' kW', color: '#1890ff', icon: 'WindPower' },
      { label: '负荷', value: (emissionsData.total_load || 1280).toFixed(0), unit: ' kW', color: '#f39c12', icon: 'Lightning' }
    ]

    // 存储API数据供图表使用
    window.__factoryEmissionsData = emissionsData
    window.__factoryZonesData = zonesData

    console.log('[API] 工厂数据加载成功', { zones: zonesData, emissions: emissionsData })
  } catch (err) {
    error.value = '数据加载失败: ' + err.message
    console.warn('[API] 加载失败，使用mock数据兜底', err)
    // 保持mock数据不变（factoryZones.value已有默认值）
  } finally {
    loading.value = false
  }
}

function switchView(mode) {
  viewMode.value = mode
  if (threeSceneObj) {
    // 根据视图模式调整相机
    const camera = threeSceneObj.camera
    const controls = threeSceneObj.controls
    switch (mode) {
      case 'global':
        camera.position.set(100, 80, 100)
        controls.target.set(0, 10, 0)
        break
      case 'workshop':
        camera.position.set(40, 30, 40)
        controls.target.set(-10, 10, -10)
        break
      case 'line':
        camera.position.set(15, 10, 15)
        controls.target.set(0, 5, 0)
        break
    }
  }
}

function handleTimeRangeChange() {
  // 处理时间范围变化
  console.log('时间范围变化:', timeRange.value)
  // 重新加载数据
  fetchFactoryData()
}

function selectZone(zone) {
  selectedZone.value = zone
  // 更新3D场景中的高亮
  highlightZone(zone.id)
  // 更新图表
  updateCharts(zone)
}

function highlightZone(zoneId) {
  if (!threeSceneObj) return
  const scene = threeSceneObj.scene
  scene.traverse((obj) => {
    if (obj.userData && obj.userData.zoneId === zoneId) {
      // 高亮效果
      if (obj.material) {
        obj.material.emissive = new THREE.Color(0x00d4aa)
        obj.material.emissiveIntensity = 0.5
        setTimeout(() => {
          obj.material.emissiveIntensity = 0.1
        }, 1500)
      }
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

  // 创建工厂建筑
  const buildings = [
    { id: 1, x: -40, z: -30, w: 30, h: 25, d: 20, zone: factoryZones.value[0] },
    { id: 2, x: 10, z: -30, w: 35, h: 28, d: 22, zone: factoryZones.value[1] },
    { id: 3, x: -40, z: 20, w: 40, h: 15, d: 30, zone: factoryZones.value[2] },
    { id: 4, x: 30, z: 20, w: 25, h: 20, d: 18, zone: factoryZones.value[3] },
    { id: 5, x: 30, z: -10, w: 20, h: 18, d: 15, zone: factoryZones.value[4] },
    { id: 6, x: -10, z: 20, w: 18, h: 12, d: 15, zone: factoryZones.value[5] }
  ]

  buildings.forEach(b => {
    const building = createFactoryBuilding(b.x, b.z, {
      width: b.w,
      height: b.h,
      depth: b.d,
      emissionValue: b.zone.emission,
      label: b.zone.name
    })
    building.userData = {
      ...building.userData,
      zoneId: b.id,
      isFactoryBuilding: true
    }
    scene.add(building)

    // 添加碳排放标签（悬浮球体）
    const labelColor = b.zone.status === 'normal' ? 0x00d4aa : b.zone.status === 'warning' ? 0xf39c12 : 0xff4d4f
    const labelGeometry = new THREE.SphereGeometry(1.2, 16, 16)
    const labelMaterial = new THREE.MeshBasicMaterial({
      color: labelColor,
      transparent: true,
      opacity: 0.8
    })
    const label = new THREE.Mesh(labelGeometry, labelMaterial)
    label.position.set(b.x, b.h + 3, b.z)
    label.userData = { zoneId: b.id, isLabel: true }
    scene.add(label)

    // 添加脉动动画
    threeSceneObj.addAnimationHandler((time) => {
      const scale = 1 + Math.sin(time * 0.003) * 0.2
      label.scale.set(scale, scale, scale)
    })
  })

  // 添加能源流动线
  const flowLines = [
    { start: new THREE.Vector3(-60, 0, 0), end: new THREE.Vector3(-40, 0, -30), color: 0x00d4aa }, // 电力
    { start: new THREE.Vector3(0, 0, -60), end: new THREE.Vector3(10, 0, -30), color: 0xf39c12 },  // 燃气
    { start: new THREE.Vector3(60, 0, 0), end: new THREE.Vector3(30, 0, 20), color: 0x1890ff }     // 水
  ]

  flowLines.forEach(flow => {
    const flowLine = createFlowLine(flow.start, flow.end, {
      particleCount: 30,
      color: flow.color,
      lineColor: 0x1890ff
    })
    flowLine.userData.isFactoryBuilding = true
    scene.add(flowLine)

    // 添加动画更新
    threeSceneObj.addAnimationHandler((time) => {
      if (flowLine.userData.update) {
        flowLine.userData.update(time)
      }
    })
  })

  // 添加大气粒子效果
  const particleCount = 800
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 200
    positions[i * 3 + 1] = Math.random() * 50
    positions[i * 3 + 2] = (Math.random() - 0.5) * 200

    // 根据高度设置颜色（低=绿色，高=红色）
    const heightFactor = positions[i * 3 + 1] / 50
    const color = new THREE.Color()
    color.setHSL(0.3 - heightFactor * 0.3, 0.8, 0.5)
    colors[i * 3] = color.r
    colors[i * 3 + 1] = color.g
    colors[i * 3 + 2] = color.b
  }

  const particleGeometry = new THREE.BufferGeometry()
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const particleMaterial = new THREE.PointsMaterial({
    size: 1.5,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })

  const particles = new THREE.Points(particleGeometry, particleMaterial)
  particles.userData.isFactoryBuilding = true
  scene.add(particles)

  // 粒子动画
  threeSceneObj.addAnimationHandler((time) => {
    const pos = particles.geometry.attributes.position.array
    for (let i = 0; i < particleCount; i++) {
      pos[i * 3 + 1] += Math.sin(time * 0.001 + i) * 0.02
      if (pos[i * 3 + 1] > 50) pos[i * 3 + 1] = 0
    }
    particles.geometry.attributes.position.needsUpdate = true
  })

  // 相机位置
  threeSceneObj.camera.position.set(100, 80, 100)
  threeSceneObj.controls.target.set(0, 10, 0)

  // 点击事件
  threeContainer.value.addEventListener('click', onThreeClick)
}

function onThreeClick(event) {
  if (!threeSceneObj) return

  const rect = threeContainer.value.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  const y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  const raycaster = new THREE.Raycaster()
  raycaster.setFromCamera(new THREE.Vector2(x, y), threeSceneObj.camera)

  const intersects = raycaster.intersectObjects(threeSceneObj.scene.children, true)
  if (intersects.length > 0) {
    const obj = intersects[0].object
    if (obj.userData && obj.userData.zoneId) {
      const zone = factoryZones.value.find(z => z.id === obj.userData.zoneId)
      if (zone) {
        selectZone(zone)
      }
    }
  }
}

function updateCharts(zone) {
  // 更新趋势图
  if (trendChart.value) {
    if (!trendChartInstance) {
      trendChartInstance = markRaw(echarts.init(trendChart.value))
    }
    trendChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: zone.color,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      grid: { left: '8%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: mockTrendData.hours,
        axisLabel: { fontSize: 8, color: '#606266', rotate: 45 },
        axisLine: { lineStyle: { color: '#2c3e50' } }
      },
      yAxis: {
        type: 'value',
        name: 'kgCO₂',
        nameTextStyle: { fontSize: 9, color: '#606266' },
        axisLabel: { fontSize: 9, color: '#606266' },
        splitLine: { lineStyle: { color: '#1a2a3a', type: 'dashed' } }
      },
      series: [{
        type: 'line',
        data: mockTrendData.values.map(v => v * (zone.emission / 1350)),
        itemStyle: { color: zone.color },
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: zone.color + '80' },
            { offset: 1, color: zone.color + '05' }
          ])
        },
        smooth: true,
        symbol: 'circle',
        symbolSize: 4
      }],
      animationDuration: 1000
    })
  }

  // 更新能源结构图
  if (energyChart.value) {
    if (!energyChartInstance) {
      energyChartInstance = markRaw(echarts.init(energyChart.value))
    }
    energyChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}%',
        backgroundColor: 'rgba(10,22,40,0.95)',
        borderColor: '#1890ff',
        textStyle: { color: '#fff', fontSize: 11 }
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '55%'],
        data: mockEnergyData.map(d => ({
          name: d.name,
          value: d.value,
          itemStyle: { color: d.color }
        })),
        label: { fontSize: 9, color: '#c0c4cc' },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' }
        },
        animationDuration: 800
      }]
    })
  }

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  trendChartInstance?.resize()
  energyChartInstance?.resize()
}
</script>

<style scoped>
.digital-twin-factory {
  width: 100%; height: 100vh;
  background: #0a1628; position: relative;
  overflow: hidden; font-family: 'Microsoft YaHei', sans-serif;
}

/* 加载状态 */
.loading-wrapper {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(10,22,40,0.95); z-index: 1000;
}
.loading-spinner {
  width: 50px; height: 50px;
  border: 4px solid rgba(0,212,170,0.2);
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

/* 区域列表 */
.zone-list { display: flex; flex-direction: column; gap: 8px; }
.zone-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; background: rgba(255,255,255,0.03);
  border-radius: 8px; cursor: pointer; transition: all 0.3s ease;
}
.zone-item:hover { background: rgba(0,212,170,0.08); }
.zone-item.active { background: rgba(0,212,170,0.12); border: 1px solid rgba(0,212,170,0.3); }
.zone-color { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.zone-info { flex: 1; }
.zone-name { font-size: 12px; color: #e0e0e0; margin-bottom: 2px; }
.zone-emission { font-size: 10px; color: #909399; }
.zone-status { font-size: 10px; padding: 2px 6px; border-radius: 4px; }
.zone-status.normal { background: rgba(0,212,170,0.15); color: #00d4aa; }
.zone-status.warning { background: rgba(243,156,18,0.15); color: #f39c12; }
.zone-status.danger { background: rgba(255,77,79,0.15); color: #ff4d4f; }

/* 实时数据 */
.realtime-data { display: flex; flex-direction: column; gap: 8px; }
.data-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 10px; background: rgba(255,255,255,0.03);
  border-radius: 6px; font-size: 12px;
}
.data-label { color: #909399; }
.data-value { font-weight: 600; }

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
  background: rgba(17,29,51,0.9); border-radius: 8px;
  padding: 10px 14px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24,144,255,0.2); font-size: 12px;
  min-width: 200px;
}
.hover-title { font-size: 14px; font-weight: 600; color: #e0e0e0; margin-bottom: 6px; }
.hover-data { color: #c0c4cc; line-height: 1.6; }

/* 图例 */
.legend {
  position: absolute; bottom: 12px; left: 12px;
  background: rgba(17,29,51,0.9); border-radius: 8px;
  padding: 10px 14px; backdrop-filter: blur(8px);
  border: 1px solid rgba(24,144,255,0.2); font-size: 11px;
}
.legend-title { color: #909399; margin-bottom: 6px; }
.legend-bar {
  width: 150px; height: 10px;
  background: linear-gradient(90deg, #00d4aa, #f39c12, #ff4d4f);
  border-radius: 5px; margin-bottom: 4px;
}
.legend-labels { display: flex; justify-content: space-between; color: #909399; }

/* 右侧面板 */
.right-panel {
  width: 300px; display: flex; flex-direction: column;
  background: #111d33; border-radius: 12px; padding: 12px;
  overflow-y: auto; gap: 12px;
}

/* 区域详情 */
.zone-detail { flex: 1; }
.detail-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; background: rgba(0,212,170,0.05);
  border-radius: 8px; margin-bottom: 12px;
}
.detail-name { font-size: 16px; font-weight: 600; color: #e0e0e0; }
.detail-status { font-size: 12px; padding: 3px 10px; border-radius: 4px; }
.detail-status.normal { background: rgba(0,212,170,0.15); color: #00d4aa; }
.detail-status.warning { background: rgba(243,156,18,0.15); color: #f39c12; }
.detail-status.danger { background: rgba(255,77,79,0.15); color: #ff4d4f; }

.detail-meta { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.meta-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 10px; background: rgba(255,255,255,0.03);
  border-radius: 6px; font-size: 12px;
}
.meta-label { color: #909399; }
.meta-value { font-weight: 600; color: #e0e0e0; }

/* 图表 */
.detail-chart { margin-bottom: 12px; }
.chart-title { font-size: 12px; color: #909399; margin-bottom: 6px; font-weight: 500; }
.chart-container { height: 180px; }
.chart-container.small { height: 150px; }

/* 无选择提示 */
.no-selection {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #606266;
}

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: transparent; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb {
  background: #1890ff; border-radius: 2px;
}
</style>
