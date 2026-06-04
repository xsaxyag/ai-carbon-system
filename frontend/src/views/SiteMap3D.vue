<template>
  <div class="site-map-3d">
    <div class="page-header">
      <h2>🌍 园区3D可视化</h2>
      <p class="subtitle">导入园区平面图，一键生成3D模型并叠加碳数据</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="12">
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
              <template #tip>
                <div class="el-upload__tip">
                  支持 JPG/PNG/WEBP 格式，建议分辨率 ≥ 1920×1080
                </div>
              </template>
            </el-upload>
            <div v-if="uploadedImage" class="image-preview">
              <img :src="uploadedImage" alt="园区平面图" class="preview-img" />
              <el-button type="primary" @click="start3DConversion" :loading="converting">
                🚀 一键生成3D园区
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📊 数据叠加</span>
              </div>
            </template>
            <el-form label-position="top">
              <el-form-item label="碳排放数据源">
                <el-select v-model="dataSource" placeholder="选择数据源" style="width: 100%">
                  <el-option label="实时监测数据" value="realtime" />
                  <el-option label="月度汇总" value="monthly" />
                  <el-option label="年度报告" value="yearly" />
                </el-select>
              </el-form-item>
              <el-form-item label="可视化模式">
                <el-radio-group v-model="visualizationMode">
                  <el-radio value="heatmap">热力图</el-radio>
                  <el-radio value="height">高度映射</el-radio>
                  <el-radio value="color">颜色编码</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="overlayCarbonData" :loading="overlaying">
                  🎨 叠加碳数据
                </el-button>
              </el-form-item>
            </el-form>
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
            </el-button-group>
          </div>
        </div>
      </template>
      <div ref="threeContainer" class="three-container"></div>
      <div v-if="!sceneReady" class="placeholder">
        <el-empty description="请先上传园区平面图并生成3D模型" />
      </div>
    </el-card>

    <!-- 建筑信息面板 -->
    <el-drawer v-model="buildingInfoVisible" title="建筑碳排放详情" size="30%">
      <div v-if="selectedBuilding" class="building-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="建筑名称">{{ selectedBuilding.name }}</el-descriptions-item>
          <el-descriptions-item label="建筑面积">{{ selectedBuilding.area }} m²</el-descriptions-item>
          <el-descriptions-item label="碳排放量">
            <span :style="{ color: getCarbonColor(selectedBuilding.carbonEmission) }">
              {{ selectedBuilding.carbonEmission }} tCO₂e
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="能耗强度">{{ selectedBuilding.energyIntensity }} kWh/m²</el-descriptions-item>
          <el-descriptions-item label="减排潜力">{{ selectedBuilding.reductionPotential }}%</el-descriptions-item>
        </el-descriptions>

        <div class="chart-container">
          <h4>历史碳排放趋势</h4>
          <div ref="trendChart" style="width: 100%; height: 200px;"></div>
        </div>

        <div class="actions">
          <el-button type="primary" @click="showOptimizationPlan">查看优化方案</el-button>
          <el-button type="success" @click="drillDown">下钻分析</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 建筑物标注对话框 -->
    <el-dialog v-model="annotationDialogVisible" title="标注建筑物位置" width="80%">
      <div class="annotation-container">
        <div class="image-annotation-area">
          <img :src="uploadedImage" alt="标注" class="annotation-img" ref="annotationImage" />
          <div
            v-for="(building, index) in buildings"
            :key="index"
            class="building-marker"
            :style="{
              left: building.x + 'px',
              top: building.y + 'px',
              width: building.width + 'px',
              height: building.height + 'px'
            }"
            @click="editBuilding(index)"
          >
            <span class="marker-label">{{ building.name }}</span>
          </div>
          <div
            v-if="drawing"
            class="building-marker drawing"
            :style="{
              left: drawStart.x + 'px',
              top: drawStart.y + 'px',
              width: drawSize.width + 'px',
              height: drawSize.height + 'px'
            }"
          ></div>
        </div>
        <div class="annotation-controls">
          <p>在左侧图片上拖拽框选建筑物位置</p>
          <el-form :model="currentBuilding" label-width="80px">
            <el-form-item label="建筑名称">
              <el-input v-model="currentBuilding.name" placeholder="例如：生产车间" />
            </el-form-item>
            <el-form-item label="建筑类型">
              <el-select v-model="currentBuilding.type" placeholder="选择类型">
                <el-option label="生产车间" value="production" />
                <el-option label="仓库" value="warehouse" />
                <el-option label="办公楼" value="office" />
                <el-option label="实验室" value="lab" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="建筑面积">
              <el-input-number v-model="currentBuilding.area" :min="0" :step="100" />
              <span style="margin-left: 10px">m²</span>
            </el-form-item>
          </el-form>
          <div class="form-actions">
            <el-button type="primary" @click="saveBuilding">保存标注</el-button>
            <el-button @click="cancelDrawing">取消</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="success" @click="finishAnnotation">完成标注 ({{ buildings.length }} 个建筑)</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { ElMessage, ElLoading } from 'element-plus'

// 响应式数据
const threeContainer = ref(null)
const sceneReady = ref(false)
const converting = ref(false)
const overlaying = ref(false)
const rotating = ref(false)
const wireframe = ref(false)
const uploadedImage = ref(null)
const imageFile = ref(null)
const dataSource = ref('realtime')
const visualizationMode = ref('heatmap')
const buildingInfoVisible = ref(false)
const selectedBuilding = ref(null)
const annotationDialogVisible = ref(false)
const drawing = ref(false)
const drawStart = ref({ x: 0, y: 0 })
const drawSize = ref({ width: 0, height: 0 })
const buildings = ref([])
const currentBuilding = ref({ name: '', type: 'production', area: 1000 })
const editingIndex = ref(-1)

// Three.js 变量
let scene = null
let camera = null
let renderer = null
let controls = null
let animationId = null
let buildingMeshes = []

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
const start3DConversion = () => {
  if (!uploadedImage.value) {
    ElMessage.warning('请先上传园区平面图！')
    return
  }
  
  converting.value = true
  
  // 显示标注对话框
  annotationDialogVisible.value = true
  converting.value = false
}

// 鼠标事件处理（标注）
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
      if (!drawing.value) return
      drawing.value = false
      
      // 确保宽高为正数
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
    })
  })
}

// 保存建筑标注
const saveBuilding = () => {
  if (!currentBuilding.value.name) {
    ElMessage.error('请填写建筑名称！')
    return
  }
  
  const building = {
    name: currentBuilding.value.name,
    type: currentBuilding.value.type,
    area: currentBuilding.value.area,
    x: drawStart.value.x,
    y: drawStart.value.y,
    width: drawSize.value.width,
    height: drawSize.value.height,
    carbonEmission: (Math.random() * 500 + 100).toFixed(1), // 模拟数据
    energyIntensity: (Math.random() * 100 + 50).toFixed(1),
    reductionPotential: (Math.random() * 30 + 10).toFixed(1)
  }
  
  if (editingIndex.value >= 0) {
    buildings.value[editingIndex.value] = building
    editingIndex.value = -1
  } else {
    buildings.value.push(building)
  }
  
  currentBuilding.value = { name: '', type: 'production', area: 1000 }
  drawStart.value = { x: 0, y: 0 }
  drawSize.value = { width: 0, height: 0 }
  
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

// 取消绘制
const cancelDrawing = () => {
  drawing.value = false
  currentBuilding.value = { name: '', type: 'production', area: 1000 }
  drawStart.value = { x: 0, y: 0 }
  drawSize.value = { width: 0, height: 0 }
  editingIndex.value = -1
}

// 完成标注
const finishAnnotation = () => {
  if (buildings.value.length === 0) {
    ElMessage.warning('请至少标注一个建筑！')
    return
  }
  
  annotationDialogVisible.value = false
  ElMessage.success(`标注完成！共 ${buildings.value.length} 个建筑`)
  
  // 开始生成3D场景
  initThreeScene()
}

// 初始化Three.js场景
const initThreeScene = () => {
  if (!threeContainer.value) return
  
  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f2f5)
  
  // 创建相机
  const container = threeContainer.value
  camera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  )
  camera.position.set(50, 50, 50)
  camera.lookAt(0, 0, 0)
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(container.clientWidth, container.clientHeight)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.innerHTML = ''
  container.appendChild(renderer.domElement)
  
  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  
  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(50, 100, 50)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  scene.add(directionalLight)
  
  // 添加地面
  const groundGeometry = new THREE.PlaneGeometry(200, 200)
  const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x98fb98 })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)
  
  // 根据标注数据创建筑模型
  createBuildings()
  
  // 添加网格辅助
  const gridHelper = new THREE.GridHelper(200, 20, 0x000000, 0x000000)
  gridHelper.material.opacity = 0.2
  gridHelper.material.transparent = true
  scene.add(gridHelper)
  
  // 开始动画循环
  animate()
  
  sceneReady.value = true
  ElMessage.success('3D园区模型生成成功！')
}

// 创建建筑模型
const createBuildings = () => {
  const colors = {
    production: 0x409eff,
    warehouse: 0x67c23a,
    office: 0xe6a23c,
    lab: 0xf56c6c,
    other: 0x909399
  }
  
  buildings.value.forEach((building, index) => {
    // 根据图片坐标映射到3D空间
    const x = (building.x / 1000) * 200 - 100
    const z = (building.y / 800) * 200 - 100
    const width = (building.width / 1000) * 200
    const depth = (building.height / 800) * 200
    const height = Math.sqrt(building.area) / 10
    
    // 创建建筑几何体
    const geometry = new THREE.BoxGeometry(width, height, depth)
    const material = new THREE.MeshLambertMaterial({
      color: colors[building.type] || colors.other,
      transparent: true,
      opacity: 0.8
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.set(x + width / 2, height / 2, z + depth / 2)
    mesh.castShadow = true
    mesh.receiveShadow = true
    
    // 添加用户数据
    mesh.userData = { buildingIndex: index, ...building }
    
    // 添加点击事件
    mesh.cursor = 'pointer'
    
    scene.add(mesh)
    buildingMeshes.push(mesh)
    
    // 添加建筑标签
    addBuildingLabel(mesh, building.name)
  })
  
  // 添加点击事件监听
  renderer.domElement.addEventListener('click', onBuildingClick)
}

// 添加建筑标签
const addBuildingLabel = (mesh, text) => {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  canvas.width = 256
  canvas.height = 128
  
  context.fillStyle = 'rgba(0, 0, 0, 0.7)'
  context.fillRect(0, 0, canvas.width, canvas.height)
  
  context.font = 'bold 24px Arial'
  context.fillStyle = 'white'
  context.textAlign = 'center'
  context.textBaseline = 'middle'
  context.fillText(text, canvas.width / 2, canvas.height / 2)
  
  const texture = new THREE.CanvasTexture(canvas)
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
  const sprite = new THREE.Sprite(spriteMaterial)
  sprite.position.set(
    mesh.position.x,
    mesh.position.y + mesh.geometry.parameters.height / 2 + 2,
    mesh.position.z
  )
  sprite.scale.set(8, 4, 1)
  scene.add(sprite)
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
    selectedBuilding.value = buildings.value[buildingIndex]
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
  
  // 根据可视化模式调整建筑颜色/高度
  buildingMeshes.forEach((mesh, index) => {
    const building = buildings.value[index]
    const carbonValue = parseFloat(building.carbonEmission)
    
    if (visualizationMode.value === 'heatmap') {
      // 热力图模式：根据碳排放量调整颜色
      const color = getHeatmapColor(carbonValue)
      mesh.material.color.setHex(color)
    } else if (visualizationMode.value === 'height') {
      // 高度映射：根据碳排放量调整建筑高度
      const scale = 1 + carbonValue / 500
      mesh.scale.y = scale
    } else if (visualizationMode.value === 'color') {
      // 颜色编码：固定颜色映射
      const color = getCarbonColorHex(carbonValue)
      mesh.material.color.setHex(color)
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
  const ratio = (value - min) / (max - min)
  
  if (ratio < 0.5) {
    // 绿色到黄色
    const r = Math.floor(2 * ratio * 255)
    const g = 255
    return (r << 16) | (g << 8)
  } else {
    // 黄色到红色
    const r = 255
    const g = Math.floor(2 * (1 - ratio) * 255)
    const b = 0
    return (r << 16) | (g << 8) | b
  }
}

// 获取碳排放颜色（CSS）
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

// 动画循环
const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  if (rotating.value) {
    buildingMeshes.forEach((mesh) => {
      mesh.rotation.y += 0.01
    })
  }
  
  controls.update()
  renderer.render(scene, camera)
}

// 重置相机
const resetCamera = () => {
  camera.position.set(50, 50, 50)
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

// 查看优化方案
const showOptimizationPlan = () => {
  ElMessage.info('优化方案功能开发中...')
}

// 下钻分析
const drillDown = () => {
  ElMessage.info('下钻分析功能开发中...')
}

// 组件挂载
onMounted(() => {
  initAnnotationEvents()
  
  // 监听窗口大小变化
  window.addEventListener('resize', onWindowResize)
})

// 组件卸载
onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  
  if (renderer) {
    renderer.dispose()
  }
  
  window.removeEventListener('resize', onWindowResize)
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

.chart-container {
  margin-top: 20px;
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
  border-radius: 4px;
}

.annotation-img {
  max-width: 100%;
  display: block;
}

.building-marker {
  position: absolute;
  border: 2px solid #409eff;
  background: rgba(64, 158, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s;
}

.building-marker:hover {
  background: rgba(64, 158, 255, 0.4);
}

.marker-label {
  position: absolute;
  top: -20px;
  left: 0;
  background: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  white-space: nowrap;
}

.drawing {
  border-style: dashed;
  background: rgba(64, 158, 255, 0.1);
}

.annotation-controls {
  width: 300px;
  padding: 20px;
  border-left: 1px solid #dcdfe6;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
