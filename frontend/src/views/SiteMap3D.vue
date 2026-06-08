<template>
  <div class="site-map-3d">
    <div class="page-header">
      <h2>🌍 园区3D可视化</h2>
      <p class="subtitle">导入园区平面图，一键生成3D模型并叠加碳数据</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📤 地图导入</span>
              </div>
            </template>
            <el-upload
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleImageUpload"
              :show-file-list="false"
              accept="image/*"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽园区平面图到此处 或 <em>点击上传</em>
              </div>
            </el-upload>
            <div v-if="uploadedImage" class="image-preview">
              <img :src="uploadedImage" alt="园区平面图" class="preview-img" />
              <el-button type="primary" @click="start3DConversion" :loading="converting">
                🚀 一键生成3D园区
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📊 数据配置</span>
              </div>
            </template>
            <el-form label-position="top" size="small">
              <el-form-item label="碳排放数据源">
                <el-select v-model="dataSource" placeholder="选择数据源" style="width: 100%">
                  <el-option label="实时监测数据" value="realtime" />
                  <el-option label="月度汇总" value="monthly" />
                  <el-option label="年度报告" value="yearly" />
                </el-select>
              </el-form-item>
              <el-form-item label="可视化模式">
                <el-radio-group v-model="visualizationMode" size="small">
                  <el-radio-button value="heatmap">热力图</el-radio-button>
                  <el-radio-button value="height">高度</el-radio-button>
                  <el-radio-button value="color">颜色</el-radio-button>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="特效选项">
                <el-checkbox-group v-model="enabledEffects">
                  <el-checkbox value="particle">粒子特效</el-checkbox>
                  <el-checkbox value="breathing">呼吸动画</el-checkbox>
                  <el-checkbox value="glow">光晕效果</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="overlayCarbonData" :loading="overlaying" :disabled="!sceneReady">
                  🎨 叠加碳数据
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📥 导出功能</span>
              </div>
            </template>
            <div class="export-actions">
              <el-button type="primary" @click="exportImage" :disabled="!sceneReady" size="small">
                📷 导出PNG
              </el-button>
              <el-button type="warning" @click="exportJPEG" :disabled="!sceneReady" size="small">
                🖼️ 导出JPEG
              </el-button>
              <el-button type="info" @click="startVideoRecording" :disabled="!sceneReady || isRecording" size="small">
                🎥 {{ isRecording ? '录制中...' : '录视频' }}
              </el-button>
              <el-button type="danger" @click="stopVideoRecording" v-if="isRecording" size="small">
                ⏹️ 停止
              </el-button>
            </div>
            <div v-if="isRecording" class="recording-indicator">
              <span class="recording-dot"></span> 正在录制...
              <span class="recording-time">{{ recordingTime }}s</span>
            </div>
            <el-progress v-if="isRecording" :percentage="recordingProgress" :show-text="false" />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 3D可视化区域 -->
    <el-card class="visualization-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>🏭 3D园区模型</span>
          <div class="header-actions">
            <el-button-group>
              <el-button size="small" @click="resetCamera">重置视角</el-button>
              <el-button size="small" @click="toggleRotation">{{ rotating ? '停止旋转' : '自动旋转' }}</el-button>
              <el-button size="small" @click="toggleWireframe">{{ wireframe ? '实体模式' : '线框模式' }}</el-button>
              <el-button size="small" @click="toggleEffects">{{ showEffects ? '隐藏特效' : '显示特效' }}</el-button>
            </el-button-group>
            <el-button-group style="margin-left: 10px">
              <el-button size="small" @click="toggleDayNight">{{ isNightMode ? '☀️ 白天' : '🌙 夜晚' }}</el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      <div ref="threeContainer" class="three-container"></div>
      <div v-if="!sceneReady" class="placeholder">
        <el-empty description="请先上传园区平面图并生成3D模型" />
      </div>
      <!-- 数据统计 -->
      <div v-if="sceneReady && carbonData" class="carbon-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-value">{{ carbonData.buildings?.length || 0 }}</div>
              <div class="stat-label">建筑数量</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-value">{{ carbonData.total_carbon_emission?.toFixed(1) || 0 }} t</div>
            <div class="stat-label">碳排放量</div>
          </el-col>
          <el-col :span="6">
            <div class="stat-value">{{ carbonData.average_intensity?.toFixed(1) || 0 }}</div>
            <div class="stat-label">平均强度</div>
          </el-col>
          <el-col :span="6">
            <div class="stat-value">{{ carbonData.summary?.green_energy_coverage || 0 }}%</div>
            <div class="stat-label">绿电覆盖率</div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 建筑信息面板 -->
    <el-drawer v-model="buildingInfoVisible" title="建筑碳排放详情" size="30%">
      <div v-if="selectedBuilding" class="building-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="建筑名称">
            {{ selectedBuilding.name }}
          </el-descriptions-item>
          <el-descriptions-item label="建筑类型">
            <el-tag :type="getTypeTag(selectedBuilding.type)">
              {{ getTypeName(selectedBuilding.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="建筑面积">
            {{ selectedBuilding.area || selectedBuilding.area }} m²
          </el-descriptions-item>
          <el-descriptions-item label="碳排放量" v-if="selectedBuilding.carbon_emission">
            <span :style="{ color: getCarbonColor(selectedBuilding.carbon_emission) }">
              {{ selectedBuilding.carbon_emission }} tCO₂
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="碳排放强度" v-if="selectedBuilding.carbon_intensity">
            {{ selectedBuilding.carbon_intensity }} kgCO₂/m²
          </el-descriptions-item>
          <el-descriptions-item label="能耗消耗" v-if="selectedBuilding.energy_consumption">
            {{ selectedBuilding.energy_consumption?.toLocaleString() }} kWh
          </el-descriptions-item>
          <el-descriptions-item label="能源类型" v-if="selectedBuilding.energy_type">
            {{ selectedBuilding.energy_type }}
          </el-descriptions-item>
          <el-descriptions-item label="绿电比例" v-if="selectedBuilding.green_energy_ratio">
            <el-progress :percentage="selectedBuilding.green_energy_ratio" :color="getGreenProgressColor" />
          </el-descriptions-item>
          <el-descriptions-item label="减排潜力" v-if="selectedBuilding.reduction_potential">
            <el-progress :percentage="selectedBuilding.reduction_potential" :color="getReductionProgressColor" />
          </el-descriptions-item>
          <el-descriptions-item label="碳排放排名" v-if="selectedBuilding.rank">
            第 {{ selectedBuilding.rank }} 名
          </el-descriptions-item>
        </el-descriptions>

        <div class="actions">
          <el-button type="primary" @click="showOptimizationPlan">💡 查看优化方案</el-button>
          <el-button type="warning" @click="drillDown">📊 下钻分析</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 标注对话框 -->
    <el-dialog v-model="annotationDialogVisible" title="建筑标注" width="900px" :close-on-click-modal="false">
      <div class="annotation-container">
        <div class="image-annotation-area" ref="annotationArea">
          <img
            ref="annotationImg"
            :src="uploadedImage"
            class="annotation-img"
            :style="{ cursor: drawing ? 'crosshair' : 'default' }"
            @mousedown="startDraw"
            @mousemove="onDraw"
            @mouseup="endDraw"
            @mouseleave="endDraw"
          />
          <!-- 标注框 -->
          <div
            v-for="(building, index) in buildings"
            :key="index"
            class="annotation-box"
            :class="{ selected: editingIndex === index }"
            :style="getAnnotationStyle(building)"
            @click="editBuilding(index)"
          >
            <span class="annotation-label">{{ building.name }}</span>
          </div>
          <!-- 绘制中的框 -->
          <div
            v-if="drawing"
            class="drawing-box"
            :style="getDrawingStyle()"
          />
        </div>

        <div class="annotation-form">
          <el-form :model="currentBuilding" label-width="100px">
            <el-form-item label="建筑名称">
              <el-input v-model="currentBuilding.name" placeholder="请输入建筑名称" />
            </el-form-item>
            <el-form-item label="建筑类型">
              <el-select v-model="currentBuilding.type" style="width: 100%">
                <el-option label="生产车间" value="production" />
                <el-option label="仓储" value="warehouse" />
                <el-option label="办公" value="office" />
                <el-option label="实验室" value="lab" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="建筑面积(m²)">
              <el-input-number v-model="currentBuilding.area" :min="50" :max="10000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="位置信息">
              <el-text>坐标: ({{ drawStart.x.toFixed(0) }}, {{ drawStart.y.toFixed(0) }})</el-text>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBuilding">{{ editingIndex >= 0 ? '更新' : '保存' }}标注</el-button>
              <el-button @click="cancelDrawing">取消</el-button>
              <el-button v-if="editingIndex >= 0" type="danger" @click="deleteBuilding">删除</el-button>
            </el-form-item>
          </el-form>

          <el-divider>已标注建筑 ({{ buildings.length }})</el-divider>
          <div class="building-list">
            <div v-for="(building, index) in buildings" :key="index" class="building-item">
              <span>{{ building.name }}</span>
              <el-tag size="small">{{ getTypeName(building.type) }}</el-tag>
              <el-button size="small" link @click="editBuilding(index)">编辑</el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelAnnotation">取消</el-button>
        <el-button type="primary" @click="finishAnnotation">完成标注 ({{ buildings.length }})</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { API_BASE } from '../utils/auth'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { createThreeScene, createHeatParticle } from '../utils/three-scene.js'

// Three.js变量
let threeSceneObj = null
let scene = null
let camera = null
let renderer = null
let controls = null
let animationId = null
let buildingMeshes = []
let particleSystem = null
let glowSprites = []
let breathingObjects = []
let mediaRecorder = null
let recordedChunks = []
let recordingStartTime = null
let composer = null  // Bloom 后处理合成器

// 状态
const threeContainer = ref(null)
const trendChart = ref(null)
const carbonTrendData = ref(null)
const optimizationSuggestions = ref(null)
const uploadedImage = ref('')
const imageFile = ref(null)
const converting = ref(false)
const overlaying = ref(false)
const annotationDialogVisible = ref(false)
const buildingInfoVisible = ref(false)
const selectedBuilding = ref(null)
const editingIndex = ref(-1)
const sceneReady = ref(false)
const rotating = ref(false)
const wireframe = ref(false)
const showEffects = ref(true)
const isNightMode = ref(false)
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingProgress = ref(0)
const carbonData = ref(null)
const enabledEffects = ref(['particle', 'breathing', 'glow'])

// 绘图状态
const drawing = ref(false)
const drawStart = ref({ x: 0, y: 0 })
const drawSize = ref({ width: 0, height: 0 })
const currentBuilding = ref({
  name: '',
  type: 'production',
  area: 1000
})

// 数据配置
const dataSource = ref('monthly')
const visualizationMode = ref('heatmap')
const buildings = ref([])

// 颜色配置
const typeColors = {
  production: 0x409eff,
  warehouse: 0x67c23a,
  office: 0xe6a23c,
  lab: 0xf56c6c,
  other: 0x909399
}

// 获取真实碳排放数据
const fetchCarbonData = async () => {
  try {
    const response = await fetch(`${API_BASE}/site-map/buildings?company_id=1&month=${new Date().toISOString().slice(0, 7)}`)
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        carbonData.value = data
        return data.buildings
      }
    }
    return null
  } catch (error) {
    console.warn('获取碳排放数据失败，使用模拟数据:', error)
    return null
  }
}

// 处理图片上传
const handleImageUpload = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件！')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target.result
    imageFile.value = file.raw
    ElMessage.success('图片上传成功！请点击"一键生成3D园区"')
  }
  reader.readAsDataURL(file.raw)
}

// 开始3D转换
const start3DConversion = async () => {
  if (!uploadedImage.value) {
    ElMessage.warning('请先上传园区平面图！')
    return
  }
  
  converting.value = true
  
  // 如果有真实数据，先获取
  await fetchCarbonData()
  
  // 显示标注对话框
  annotationDialogVisible.value = true
  converting.value = false
}

// 初始化标注事件
const initAnnotationEvents = () => {
  nextTick(() => {
    const img = document.querySelector('.annotation-img')
    if (!img) return
    
    img.addEventListener('mousedown', (e) => {
      drawing.value = true
      drawStart.value = { x: e.offsetX, y: e.offsetY }
    })
    
    img.addEventListener('mousemove', (e) => {
      if (!drawing.value) return
      drawSize.value = {
        width: e.offsetX - drawStart.value.x,
        height: e.offsetY - drawStart.value.y
      }
    })
    
    img.addEventListener('mouseup', (e) => {
      endDraw(e)
    })
  })
}

// 开始绘制
const startDraw = (e) => {
  drawing.value = true
  drawStart.value = { x: e.offsetX, y: e.offsetY }
}

// 绘制中
const onDraw = (e) => {
  if (!drawing.value) return
  drawSize.value = {
    width: e.offsetX - drawStart.value.x,
    height: e.offsetY - drawStart.value.y
  }
}

// 结束绘制
const endDraw = (e) => {
  if (!drawing.value) return
  drawing.value = false
  
  const x = Math.min(drawStart.value.x, e.offsetX)
  const y = Math.min(drawStart.value.y, e.offsetY)
  const width = Math.abs(drawSize.value.width)
  const height = Math.abs(drawSize.value.height)
  
  if (width < 10 || height < 10) {
    ElMessage.warning('框选区域太小，请重新框选')
    return
  }
  
  drawStart.value = { x, y }
  drawSize.value = { width, height }
  ElMessage.info('请填写建筑详情并保存')
}

// 获取标注框样式
const getAnnotationStyle = (building) => {
  return {
    left: `${building.x}px`,
    top: `${building.y}px`,
    width: `${building.width}px`,
    height: `${building.height}px`
  }
}

// 获取绘制框样式
const getDrawingStyle = () => {
  return {
    left: `${Math.min(drawStart.value.x, drawStart.value.x + drawSize.value.width)}px`,
    top: `${Math.min(drawStart.value.y, drawStart.value.y + drawSize.value.height)}px`,
    width: `${Math.abs(drawSize.value.width)}px`,
    height: `${Math.abs(drawSize.value.height)}px`
  }
}

// 保存建筑标注
const saveBuilding = () => {
  if (!currentBuilding.value.name) {
    ElMessage.error('请填写建筑名称！')
    return
  }
  
  // 从API数据中查找匹配的碳排放信息
  let carbonInfo = null
  if (carbonData.value?.buildings) {
    const apiBuilding = carbonData.value.buildings.find(b => 
      b.name.includes(currentBuilding.value.name) || 
      currentBuilding.value.name.includes(b.name)
    )
    if (apiBuilding) {
      carbonInfo = apiBuilding
    }
  }
  
  const building = {
    name: currentBuilding.value.name,
    type: currentBuilding.value.type,
    area: currentBuilding.value.area,
    x: drawStart.value.x,
    y: drawStart.value.y,
    width: drawSize.value.width,
    height: drawSize.value.height,
    // 使用真实API数据或模拟
    carbon_emission: carbonInfo?.carbon_emission || (Math.random() * 500 + 100).toFixed(1),
    energy_consumption: carbonInfo?.energy_consumption || (Math.random() * 100000 + 50000).toFixed(0),
    carbon_intensity: carbonInfo?.carbon_intensity || (Math.random() * 30 + 5).toFixed(1),
    energy_type: carbonInfo?.energy_type || '电力',
    green_energy_ratio: carbonInfo?.green_energy_ratio || (Math.random() * 30 + 10).toFixed(1),
    reduction_potential: carbonInfo?.reduction_potential || (Math.random() * 30 + 10).toFixed(1),
    rank: carbonInfo?.rank || buildings.value.length + 1
  }
  
  if (editingIndex.value >= 0) {
    buildings.value[editingIndex.value] = building
  } else {
    buildings.value.push(building)
  }
  
  currentBuilding.value = { name: '', type: 'production', area: 1000 }
  drawStart.value = { x: 0, y: 0 }
  drawSize.value = { width: 0, height: 0 }
  editingIndex.value = -1
  
  ElMessage.success('建筑标注已保存！')
}

// 编辑建筑
const editBuilding = (index) => {
  editingIndex.value = index
  const building = buildings.value[index]
  currentBuilding.value = {
    name: building.name,
    type: building.type,
    area: building.area
  }
  drawStart.value = { x: building.x, y: building.y }
  drawSize.value = { width: building.width, height: building.height }
}

// 删除建筑
const deleteBuilding = () => {
  if (editingIndex.value >= 0) {
    buildings.value.splice(editingIndex.value, 1)
    cancelDrawing()
    ElMessage.success('建筑已删除')
  }
}

// 取消绘制
const cancelDrawing = () => {
  drawing.value = false
  currentBuilding.value = { name: '', type: 'production', area: 1000 }
  drawStart.value = { x: 0, y: 0 }
  drawSize.value = { width: 0, height: 0 }
  editingIndex.value = -1
}

// 取消标注
const cancelAnnotation = () => {
  annotationDialogVisible.value = false
  buildings.value = []
  ElMessage.info('已取消标注')
}

// 完成标注
const finishAnnotation = () => {
  if (buildings.value.length === 0) {
    ElMessage.warning('请至少标注一个建筑！')
    return
  }
  
  annotationDialogVisible.value = false
  ElMessage.success(`标注完成！共 ${buildings.value.length} 个建筑，正在生成3D模型...`)
  
  // 开始生成3D场景
  initThreeScene()
}

// 初始化Three.js场景
const initThreeScene = () => {
  if (!threeContainer.value) return
  
  // 调用 createThreeScene，它内部会创建 renderer 并添加到 DOM
  threeSceneObj = createThreeScene(threeContainer.value, {
    background: 0x0a1628,
    enablePostProcessing: true,
    autoRotate: false,
    autoRotateSpeed: 0
  })
  
  // 直接使用 threeSceneObj 里的对象
  scene = threeSceneObj.scene
  camera = threeSceneObj.camera
  renderer = threeSceneObj.renderer
  composer = threeSceneObj.composer
  controls = threeSceneObj.controls
  
  // 覆盖相机位置
  camera.position.set(80, 60, 80)
  camera.lookAt(0, 0, 0)
  
  // 调整 Bloom 后处理参数（createThreeScene 默认 strength=0.6，这里改为 1.2）
  if (composer && composer.passes && composer.passes.length > 1) {
    const bloomPass = composer.passes[1]  // 第二个 pass 是 UnrealBloomPass
    if (bloomPass && bloomPass.strength !== undefined) {
      bloomPass.strength = 1.2
      console.log('[SiteMap3D] Bloom strength 已调整为 1.2')
    }
  }
  
  // 根据日夜模式更新背景
  updateSceneBackground()
  
  // 添加光源
  updateLighting()
  
  // 添加地面
  createGroundPlane()
  
  // 创建建筑
  createBuildings()
  
  // 添加特效
  if (showEffects.value) {
    createParticleSystem()
    createGlowEffects()
  }
  
  // 使用 threeSceneObj.addAnimationHandler() 注册动画更新
  threeSceneObj.addAnimationHandler((time) => {
    const t = time * 0.001
    
    // 自动旋转
    if (rotating.value) {
      buildingMeshes.forEach((mesh) => {
        mesh.rotation.y += 0.005
      })
    }
    
    // 呼吸动画
    if (enabledEffects.value.includes('breathing') && breathingObjects.length > 0) {
      breathingObjects.forEach((obj, index) => {
        if (obj.material) {
          const breathe = Math.sin(t * 2 + index * 0.5) * 0.1 + 0.9
          if (obj.material.emissiveIntensity !== undefined) {
            obj.material.emissiveIntensity = breathe * (isNightMode.value ? 0.35 : 0.08)
          }
        }
      })
    }
    
    // 粒子动画
    if (particleSystem && enabledEffects.value.includes('particle')) {
      particleSystem.rotation.y += 0.0005
      const positions = particleSystem.geometry.attributes.position.array
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += Math.sin(t + i) * 0.02
        if (positions[i + 1] > 120) positions[i + 1] = 10
      }
      particleSystem.geometry.attributes.position.needsUpdate = true
    }
    
    // 光晕效果
    if (enabledEffects.value.includes('glow') && glowSprites.length > 0) {
      glowSprites.forEach((sprite, index) => {
        if (sprite.material.opacity !== undefined) {
          sprite.material.opacity = Math.sin(t * 1.5 + index * 0.3) * 0.3 + 0.4
        }
      })
    }
  })
  
  sceneReady.value = true
  ElMessage.success('3D园区模型生成成功！')
}

// 更新场景背景
const updateSceneBackground = () => {
  if (!scene) return
  if (isNightMode.value) {
    scene.background = new THREE.Color(0x0a0a1a)
    scene.fog = new THREE.Fog(0x0a0a1a, 100, 300)
  } else {
    scene.background = new THREE.Color(0xe8f4f8)
    scene.fog = new THREE.Fog(0xe8f4f8, 150, 350)
  }
}

// 更新光照
const updateLighting = () => {
  if (!scene) return
  
  // 移除旧光源
  const oldLights = scene.children.filter(c => c.isLight)
  oldLights.forEach(l => scene.remove(l))
  
  if (isNightMode.value) {
    // 夜晚模式：蓝色月光 + 建筑灯光
    const moonLight = new THREE.DirectionalLight(0x4466ff, 0.3)
    moonLight.position.set(50, 100, 50)
    scene.add(moonLight)
    
    const ambientLight = new THREE.AmbientLight(0x112244, 0.4)
    scene.add(ambientLight)
    
    // 建筑窗户灯光
    buildingMeshes.forEach((mesh, index) => {
      const light = new THREE.PointLight(0xffaa00, 0.5, 15)
      light.position.set(mesh.position.x, mesh.position.y + 5, mesh.position.z)
      scene.add(light)
    })
  } else {
    // 白天模式：阳光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(50, 100, 50)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.width = 2048
    directionalLight.shadow.mapSize.height = 2048
    scene.add(directionalLight)
  }
}

// 创建带网格和反射效果的地面
const createGroundPlane = () => {
  // 地面主体（深色带轻微反射）
  const groundGeometry = new THREE.PlaneGeometry(300, 300)
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: isNightMode.value ? 0x111122 : 0x3a5f3a,
    metalness: 0.3,
    roughness: 0.6
  })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)
  
  // 半透明网格覆盖层（Canvas纹理）
  const gridCanvas = document.createElement('canvas')
  gridCanvas.width = 512
  gridCanvas.height = 512
  const ctx = gridCanvas.getContext('2d')
  ctx.strokeStyle = isNightMode.value ? 'rgba(0, 180, 255, 0.15)' : 'rgba(0, 100, 0, 0.12)'
  ctx.lineWidth = 1
  const step = 32
  for (let i = 0; i <= 512; i += step) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, 512); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(512, i); ctx.stroke()
  }
  const gridTexture = new THREE.CanvasTexture(gridCanvas)
  gridTexture.wrapS = THREE.RepeatWrapping
  gridTexture.wrapT = THREE.RepeatWrapping
  gridTexture.repeat.set(8, 8)
  const gridOverlay = new THREE.Mesh(
    new THREE.PlaneGeometry(300, 300),
    new THREE.MeshBasicMaterial({ map: gridTexture, transparent: true, opacity: 0.6, depthWrite: false })
  )
  gridOverlay.rotation.x = -Math.PI / 2
  gridOverlay.position.y = 0.02
  scene.add(gridOverlay)
  
  // 园区边界发光环
  const ringGeometry = new THREE.RingGeometry(145, 150, 64)
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0x00d4aa,
    transparent: true,
    opacity: isNightMode.value ? 0.5 : 0.25,
    side: THREE.DoubleSide,
    depthWrite: false
  })
  const boundaryRing = new THREE.Mesh(ringGeometry, ringMaterial)
  boundaryRing.rotation.x = -Math.PI / 2
  boundaryRing.position.y = 0.05
  scene.add(boundaryRing)
}

// 切换日夜模式
const toggleDayNight = () => {
  isNightMode.value = !isNightMode.value
  updateSceneBackground()
  updateLighting()
  ElMessage.success(isNightMode.value ? '切换到夜晚模式 🌙' : '切换到白天模式 ☀️')
}

// 创建建筑模型
const createBuildings = () => {
  buildingMeshes = []
  breathingObjects = []
  
  if (!buildings.value || buildings.value.length === 0) {
    console.warn('No buildings to render')
    return
  }
  
  buildings.value.forEach((building, index) => {
    // 根据图片坐标映射到3D空间
    const imgWidth = 1000
    const imgHeight = 800
    const sceneSize = 160
    
    // 防御性检查：确保坐标有效
    const bx = Number(building.x) || 0
    const by = Number(building.y) || 0
    const bw = Number(building.width) || 50
    const bh = Number(building.height) || 50
    const area = Number(building.area) || 1000
    
    const x = (bx / imgWidth) * sceneSize - sceneSize / 2
    const z = (by / imgHeight) * sceneSize - sceneSize / 2
    const width = Math.max((bw / imgWidth) * sceneSize, 2)  // 最小宽度2
    const depth = Math.max((bh / imgHeight) * sceneSize, 2) // 最小深度2
    
    // NaN 检查
    if (isNaN(x) || isNaN(z) || isNaN(width) || isNaN(depth)) {
      console.error('Invalid building coordinates:', building)
      return
    }
    
    // 根据碳排放强度计算高度（真实数据或模拟）
    const carbonEmission = parseFloat(building.carbon_emission) || 0
    let baseHeight = Math.sqrt(area) / 3 + (carbonEmission / 100)
    const height = Math.max(baseHeight, 3)
    
    // 创建建筑几何体
    const geometry = new THREE.BoxGeometry(width, height, depth)
    const color = typeColors[building.type] || typeColors.other
    
    // 建筑材质 - 使用 MeshStandardMaterial（稳定可靠，不依赖envMap也能正常显示）
    const material = new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      metalness: 0.3,
      roughness: 0.4,
      emissive: new THREE.Color(color),
      emissiveIntensity: isNightMode.value ? 0.5 : 0.15
    })
    
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.set(x + width / 2, height / 2, z + depth / 2)
    mesh.castShadow = true
    mesh.receiveShadow = true
    
    // 添加用户数据
    mesh.userData = { buildingIndex: index, ...building, baseHeight: height }
    
    scene.add(mesh)
    buildingMeshes.push(mesh)
    breathingObjects.push(mesh)
    
    // 建筑边框发光线条（增强轮廓可见性）
    const edges = new THREE.EdgesGeometry(geometry)
    const lineMat = new THREE.LineBasicMaterial({ color: 0x00d4aa, transparent: true, opacity: 0.5 })
    const line = new THREE.LineSegments(edges, lineMat)
    line.position.copy(mesh.position)
    scene.add(line)
    
    // 添加建筑标签
    addBuildingLabel(mesh, building.name, height)
    
    // 添加屋顶装饰
    addRoofDecoration(mesh, width, depth)
  })
  
  // 添加点击事件监听
  renderer.domElement.addEventListener('click', onBuildingClick)
}

// 添加屋顶装饰
const addRoofDecoration = (mesh, width, depth) => {
  // 防御性检查
  if (!mesh || !mesh.geometry) return
  
  const meshHeight = mesh.geometry.parameters?.height || 10
  const roofRadius = Math.max(Number(width) || 5, Number(depth) || 5) * 0.6
  
  // NaN 检查
  if (isNaN(roofRadius) || roofRadius <= 0) return
  
  // 添加屋顶
  const roofGeometry = new THREE.ConeGeometry(roofRadius, 3, 4)
  const roofMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x333333,
    metalness: 0.8,
    roughness: 0.3
  })
  const roof = new THREE.Mesh(roofGeometry, roofMaterial)
  roof.position.set(mesh.position.x, meshHeight + 1.5, mesh.position.z)
  roof.rotation.y = Math.PI / 4
  scene.add(roof)
  
  // 存储屋顶用于呼吸动画
  breathingObjects.push(roof)
}

// 添加建筑标签
const addBuildingLabel = (mesh, text, height) => {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  canvas.width = 512
  canvas.height = 256
  
  // 绘制背景
  context.fillStyle = isNightMode.value ? 'rgba(20, 20, 40, 0.9)' : 'rgba(0, 0, 0, 0.7)'
  context.fillRect(0, 0, canvas.width, canvas.height)
  
  // 绘制边框
  context.strokeStyle = '#409eff'
  context.lineWidth = 4
  context.strokeRect(2, 2, canvas.width - 4, canvas.height - 4)
  
  // 绘制文字
  context.font = 'bold 36px Arial'
  context.fillStyle = 'white'
  context.textAlign = 'center'
  context.textBaseline = 'middle'
  
  // 文字换行
  const words = text.split('')
  let line = ''
  let y = canvas.height / 2
  const maxCharsPerLine = 10
  
  for (let i = 0; i < words.length; i++) {
    const testLine = line + words[i]
    if (testLine.length > maxCharsPerLine) {
      context.fillText(line, canvas.width / 2, y)
      line = words[i]
      y += 40
    } else {
      line = testLine
    }
  }
  context.fillText(line, canvas.width / 2, y)
  
  const texture = new THREE.CanvasTexture(canvas)
  const spriteMaterial = new THREE.SpriteMaterial({ 
    map: texture,
    transparent: true
  })
  const sprite = new THREE.Sprite(spriteMaterial)
  
  // 防御性检查
  const meshHeight = mesh.geometry?.parameters?.height || 10
  const labelHeight = Number(height) || meshHeight
  
  sprite.position.set(
    mesh.position.x,
    mesh.position.y + labelHeight / 2 + 8,
    mesh.position.z
  )
  sprite.scale.set(12, 6, 1)
  scene.add(sprite)
  
  glowSprites.push(sprite)
}

// 创建粒子系统
const createParticleSystem = () => {
  if (particleSystem) {
    scene.remove(particleSystem)
  }
  
  const particleCount = 2000
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)
  const sizes = new Float32Array(particleCount)
  
  for (let i = 0; i < particleCount; i++) {
    // 分布在整个园区上空
    positions[i * 3] = (Math.random() - 0.5) * 200
    positions[i * 3 + 1] = Math.random() * 100 + 10
    positions[i * 3 + 2] = (Math.random() - 0.5) * 200
    
    // 碳排放相关颜色（绿色=低碳，红色=高碳）
    const color = new THREE.Color()
    if (isNightMode.value) {
      color.setHSL(0.55, 0.8, 0.6) // 青色粒子
    } else {
      color.setHSL(0.3 + Math.random() * 0.1, 0.7, 0.5) // 绿色系
    }
    colors[i * 3] = color.r
    colors[i * 3 + 1] = color.g
    colors[i * 3 + 2] = color.b
    
    sizes[i] = Math.random() * 2 + 0.5
  }
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  
  // 粒子改为发光球体（升级视觉效果）
  const material = new THREE.PointsMaterial({
    size: 1.8,  // 更大
    vertexColors: true,
    transparent: true,
    opacity: 0.75,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
    depthWrite: false  // 防止深度冲突
  })
  
  particleSystem = new THREE.Points(geometry, material)
  scene.add(particleSystem)
}

// 创建光晕效果
const createGlowEffects = () => {
  glowSprites.forEach(sprite => {
    // 光晕效果（升级：更大更亮）
    const glowCanvas = document.createElement('canvas')
    glowCanvas.width = 256
    glowCanvas.height = 256
    const glowCtx = glowCanvas.getContext('2d')
    
    const gradient = glowCtx.createRadialGradient(128, 128, 0, 128, 128, 128)
    gradient.addColorStop(0, 'rgba(0, 212, 170, 0.9)')
    gradient.addColorStop(0.3, 'rgba(24, 144, 255, 0.5)')
    gradient.addColorStop(0.7, 'rgba(64, 158, 255, 0.15)')
    gradient.addColorStop(1, 'rgba(64, 158, 255, 0)')
    
    glowCtx.fillStyle = gradient
    glowCtx.fillRect(0, 0, 256, 256)
    
    glowCtx.fillStyle = gradient
    glowCtx.fillRect(0, 0, 128, 128)
    
    const glowTexture = new THREE.CanvasTexture(glowCanvas)
    const glowMaterial = new THREE.SpriteMaterial({
      map: glowTexture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      opacity: 0.5
    })
    
    const glowSprite = new THREE.Sprite(glowMaterial)
    glowSprite.position.copy(sprite.position)
    glowSprite.scale.set(22, 22, 1)  // 更大
    scene.add(glowSprite)
    glowSprites.push(glowSprite)
  })
}

// 建筑点击事件
const onBuildingClick = (event) => {
  const rect = renderer.domElement.getBoundingClientRect()
  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1
  )
  
  const raycaster = new THREE.Raycaster()
  raycaster.setFromCamera(mouse, camera)
  
  const intersects = raycaster.intersectObjects(buildingMeshes)
  if (intersects.length > 0) {
    const mesh = intersects[0].object
    const buildingIndex = mesh.userData.buildingIndex
    selectedBuilding.value = { ...buildings.value[buildingIndex], ...mesh.userData }
    buildingInfoVisible.value = true
  }
}

// 叠加碳数据
const overlayCarbonData = () => {
  if (!sceneReady.value) {
    ElMessage.warning('请先生成3D园区模型！')
    return
  }
  
  overlaying.value = true
  
  buildingMeshes.forEach((mesh, index) => {
    const building = buildings.value[index]
    let carbonValue = parseFloat(building.carbon_emission)
    
    if (!carbonValue || carbonValue < 0) {
      carbonValue = Math.random() * 500 + 100
    }
    
    if (visualizationMode.value === 'heatmap') {
      // 热力图模式：根据碳排放量调整颜色
      const color = getHeatmapColor(carbonValue)
      mesh.material.color.setHex(color)
      mesh.material.emissive.setHex(color)
      mesh.material.emissiveIntensity = 0.2
    } else if (visualizationMode.value === 'height') {
      // 高度映射：根据碳排放量调整建筑高度
      const scale = 1 + carbonValue / 300
      mesh.scale.y = scale
      mesh.position.y = (mesh.userData.baseHeight * scale) / 2
    } else if (visualizationMode.value === 'color') {
      // 颜色编码：固定颜色映射
      const color = getCarbonColorHex(carbonValue)
      mesh.material.color.setHex(color)
      mesh.material.emissive.setHex(color)
      mesh.material.emissiveIntensity = 0.1
    }
  })
  
  setTimeout(() => {
    overlaying.value = false
    ElMessage.success('碳数据叠加完成！')
  }, 1000)
}

// 获取热力图颜色
const getHeatmapColor = (value) => {
  const min = 100
  const max = 600
  const ratio = Math.min(Math.max((value - min) / (max - min), 0), 1)
  
  // 绿 -> 黄 -> 红
  const r = Math.floor(ratio * 255)
  const g = Math.floor((1 - ratio) * 255)
  const b = 0
  
  return (r << 16) | (g << 8) | b
}

// 获取碳排放颜色
const getCarbonColor = (value) => {
  if (value < 200) return '#67c23a'
  if (value < 400) return '#e6a23c'
  return '#f56c6c'
}

// 获取碳排放颜色（Hex）
const getCarbonColorHex = (value) => {
  if (value < 200) return 0x67c23a
  if (value < 400) return 0xe6a23c
  return 0xf56c6c
}

// 获取建筑类型名称
const getTypeName = (type) => {
  const names = {
    production: '生产车间',
    warehouse: '仓储',
    office: '办公',
    lab: '实验室',
    other: '其他'
  }
  return names[type] || type
}

// 获取建筑类型标签颜色
const getTypeTag = (type) => {
  const colors = {
    production: '',
    warehouse: 'success',
    office: 'warning',
    lab: 'danger',
    other: 'info'
  }
  return colors[type] || 'info'
}

// 获取绿电进度条颜色
const getGreenProgressColor = (percentage) => {
  if (percentage < 20) return '#f56c6c'
  if (percentage < 40) return '#e6a23c'
  return '#67c23a'
}

// 获取减排潜力进度条颜色
const getReductionProgressColor = (percentage) => {
  if (percentage < 20) return '#909399'
  if (percentage < 35) return '#409eff'
  return '#67c23a'
}

// 重置相机
const resetCamera = () => {
  camera.position.set(80, 60, 80)
  camera.lookAt(0, 0, 0)
  controls.reset()
}

// 切换旋转
const toggleRotation = () => {
  rotating.value = !rotating.value
}

// 切换线框模式
const toggleWireframe = () => {
  wireframe.value = !wireframe.value
  buildingMeshes.forEach((mesh) => {
    mesh.material.wireframe = wireframe.value
  })
}

// 切换特效显示
const toggleEffects = () => {
  showEffects.value = !showEffects.value
  if (particleSystem) {
    particleSystem.visible = showEffects.value
  }
  glowSprites.forEach(sprite => {
    sprite.visible = showEffects.value
  })
  ElMessage.success(showEffects.value ? '显示3D特效' : '隐藏3D特效')
}

// 导出PNG图片
const exportImage = () => {
  if (!renderer) return
  
  // 确保渲染器使用preserveDrawingBuffer
  renderer.render(scene, camera)
  
  const dataURL = renderer.domElement.toDataURL('image/png')
  downloadFile(dataURL, `园区3D_${new Date().toISOString().slice(0, 10)}.png`)
  ElMessage.success('PNG图片已导出！')
}

// 导出JPEG图片
const exportJPEG = () => {
  if (!renderer) return
  
  renderer.render(scene, camera)
  
  const dataURL = renderer.domElement.toDataURL('image/jpeg', 0.9)
  downloadFile(dataURL, `园区3D_${new Date().toISOString().slice(0, 10)}.jpg`)
  ElMessage.success('JPEG图片已导出！')
}

// 下载文件
const downloadFile = (dataURL, filename) => {
  const link = document.createElement('a')
  link.href = dataURL
  link.download = filename
  link.click()
}

// 开始录制视频
const startVideoRecording = () => {
  if (!renderer || !renderer.domElement) return
  
  isRecording.value = true
  recordingTime.value = 0
  recordingProgress.value = 0
  recordedChunks = []
  
  const stream = renderer.domElement.captureStream(30)
  
  // 尝试使用MediaRecorder API
  const options = { mimeType: 'video/webm;codecs=vp9' }
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
    options.mimeType = 'video/webm'
  }
  
  try {
    mediaRecorder = new MediaRecorder(stream, options)
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'video/webm' })
      const url = URL.createObjectURL(blob)
      downloadFile(url, `园区3D_${new Date().toISOString().slice(0, 10)}.webm`)
      ElMessage.success('视频已导出！')
    }
    
    mediaRecorder.start(100)
    
    // 更新录制时间
    recordingStartTime = Date.now()
    const updateRecordingTime = () => {
      if (isRecording.value) {
        recordingTime.value = Math.floor((Date.now() - recordingStartTime) / 1000)
        recordingProgress.value = Math.min(recordingTime.value / 30 * 100, 100) // 最多30秒
        setTimeout(updateRecordingTime, 1000)
      }
    }
    updateRecordingTime()
    
    ElMessage.success('开始录制视频...')
  } catch (error) {
    isRecording.value = false
    ElMessage.error('视频录制失败，请尝试导出图片')
    console.error('MediaRecorder error:', error)
  }
}

// 停止录制视频
const stopVideoRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
}

// 查看优化方案
const showOptimizationPlan = () => {
  ElMessage.info('正在获取AI优化建议...')
  // 可以调用API获取优化建议
}

// 下钻分析
const drillDown = () => {
  ElMessage.info('正在加载详细分析数据...')
  // 可以跳转到详细分析页面
}

// 组件挂载
onMounted(() => {
  initAnnotationEvents()
  
  // ========== 新增：默认示例建筑数据 ==========
  // 自动加载默认建筑数据，无需用户上传图片
  loadDefaultBuildings()
  
  window.addEventListener('resize', onWindowResize)
})

// 加载默认建筑数据
const loadDefaultBuildings = () => {
  console.log('[SiteMap3D] 开始加载默认建筑数据...')
  
  // 8-10个典型工业园区建筑，合理分布在 1000x800 标注区域内
  buildings.value = [
    { name: '生产车间A', type: 'production', area: 4500, x: 100, y: 150, width: 180, height: 120, carbon_emission: 420, energy_consumption: 95000, carbon_intensity: 9.3, energy_type: '电力+天然气', green_energy_ratio: 25, reduction_potential: 35, rank: 2 },
    { name: '生产车间B', type: 'production', area: 3800, x: 320, y: 150, width: 160, height: 110, carbon_emission: 350, energy_consumption: 82000, carbon_intensity: 9.2, energy_type: '电力', green_energy_ratio: 30, reduction_potential: 40, rank: 3 },
    { name: '生产车间C', type: 'production', area: 3200, x: 100, y: 320, width: 150, height: 100, carbon_emission: 280, energy_consumption: 68000, carbon_intensity: 8.8, energy_type: '电力+蒸汽', green_energy_ratio: 20, reduction_potential: 30, rank: 4 },
    { name: '原材料仓库', type: 'warehouse', area: 2000, x: 520, y: 100, width: 140, height: 100, carbon_emission: 80, energy_consumption: 15000, carbon_intensity: 4.0, energy_type: '电力', green_energy_ratio: 10, reduction_potential: 15, rank: 8 },
    { name: '成品仓库', type: 'warehouse', area: 2500, x: 520, y: 250, width: 150, height: 110, carbon_emission: 60, energy_consumption: 12000, carbon_intensity: 2.4, energy_type: '电力', green_energy_ratio: 15, reduction_potential: 20, rank: 9 },
    { name: '办公楼A', type: 'office', area: 1800, x: 300, y: 500, width: 120, height: 80, carbon_emission: 45, energy_consumption: 25000, carbon_intensity: 2.5, energy_type: '电力', green_energy_ratio: 45, reduction_potential: 55, rank: 6 },
    { name: '办公楼B', type: 'office', area: 1500, x: 450, y: 500, width: 110, height: 70, carbon_emission: 32, energy_consumption: 18000, carbon_intensity: 2.1, energy_type: '电力', green_energy_ratio: 50, reduction_potential: 60, rank: 7 },
    { name: '研发中心', type: 'lab', area: 1800, x: 700, y: 400, width: 130, height: 90, carbon_emission: 48, energy_consumption: 22000, carbon_intensity: 2.7, energy_type: '电力+太阳能', green_energy_ratio: 40, reduction_potential: 50, rank: 5 },
    { name: '动力中心', type: 'other', area: 800, x: 700, y: 150, width: 90, height: 70, carbon_emission: 280, energy_consumption: 120000, carbon_intensity: 35.0, energy_type: '天然气+电力', green_energy_ratio: 5, reduction_potential: 25, rank: 1 },
  ]
  
  // 计算碳排放统计数据
  const totalEmission = buildings.value.reduce((sum, b) => sum + b.carbon_emission, 0)
  const avgIntensity = buildings.value.reduce((sum, b) => sum + b.carbon_intensity, 0) / buildings.value.length
  
  carbonData.value = {
    buildings: buildings.value,
    total_carbon_emission: totalEmission,
    average_intensity: avgIntensity,
    summary: {
      green_energy_coverage: 25
    }
  }
  
  // 设置场景就绪状态
  sceneReady.value = true
  
  // 自动初始化3D场景
  nextTick(() => {
    initThreeScene()
    console.log('[SiteMap3D] 默认建筑数据加载完成，3D场景已生成', {
      buildingCount: buildings.value.length,
      totalEmission,
      avgIntensity: avgIntensity.toFixed(1)
    })
  })
}

// 组件卸载
onBeforeUnmount(() => {
  // 使用 threeSceneObj.destroy() 统一清理资源
  if (threeSceneObj && threeSceneObj.destroy) {
    threeSceneObj.destroy()
  }
  
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
})

// 窗口大小变化处理
const onWindowResize = () => {
  if (!threeContainer.value || !camera || !renderer) return
  
  const container = threeContainer.value
  camera.aspect = container.clientWidth / container.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(container.clientWidth, container.clientHeight)
}
</script>

<style scoped>
.site-map-3d {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.control-panel {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.image-preview {
  margin-top: 20px;
  text-align: center;
}

.preview-img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.visualization-card {
  margin-bottom: 30px;
}

.three-container {
  width: 100%;
  height: 600px;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.building-info {
  padding: 20px;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.annotation-container {
  display: flex;
  gap: 20px;
  height: 500px;
}

.image-annotation-area {
  flex: 1;
  position: relative;
  overflow: auto;
  border: 1px solid #dcdfe6;
  background: #f5f7fa;
}

.annotation-img {
  display: block;
  max-width: 100%;
}

.annotation-box {
  position: absolute;
  border: 2px solid #409eff;
  background: rgba(64, 158, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.annotation-box:hover,
.annotation-box.selected {
  background: rgba(64, 158, 255, 0.4);
  border-color: #66b1ff;
}

.annotation-label {
  position: absolute;
  top: -20px;
  left: 0;
  background: #409eff;
  color: white;
  padding: 2px 8px;
  font-size: 12px;
  border-radius: 4px;
  white-space: nowrap;
}

.drawing-box {
  position: absolute;
  border: 2px dashed #ff6600;
  background: rgba(255, 102, 0, 0.2);
  pointer-events: none;
}

.annotation-form {
  width: 280px;
  overflow-y: auto;
}

.building-list {
  max-height: 200px;
  overflow-y: auto;
}

.building-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.building-item span:first-child {
  flex: 1;
}

.export-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.recording-indicator {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #f56c6c;
  font-weight: bold;
}

.recording-dot {
  width: 12px;
  height: 12px;
  background: #f56c6c;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.recording-time {
  margin-left: auto;
}

.carbon-stats {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
