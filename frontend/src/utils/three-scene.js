/**
 * Three.js 场景工具类
 * 封装场景初始化、常用3D对象创建、性能优化
 * 主题: 深色科技风 - 背景#0a1628, 卡片#111d33
 */

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'

/**
 * 创建标准Three.js场景
 * @param {HTMLElement} container - 渲染容器DOM元素
 * @param {Object} options - 配置选项
 * @returns {Object} 场景对象集合
 */
export function createThreeScene(container, options = {}) {
  const {
    background = 0x0a1628,
    enablePostProcessing = true,
    enableControls = true,
    autoRotate = true,
    autoRotateSpeed = 0.5
  } = options

  // 场景
  const scene = new THREE.Scene()
  scene.background = new THREE.Color(background)
  scene.fog = new THREE.FogExp2(background, 0.002)

  // 相机
  const camera = new THREE.PerspectiveCamera(
    60,
    container.clientWidth / container.clientHeight,
    0.1,
    10000
  )
  camera.position.set(0, 50, 100)

  // 渲染器
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  })
  renderer.setSize(container.clientWidth, container.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  container.appendChild(renderer.domElement)

  // 后期处理
  let composer = null
  if (enablePostProcessing) {
    composer = new EffectComposer(renderer)
    composer.addPass(new RenderPass(scene, camera))
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(container.clientWidth, container.clientHeight),
      0.6,  // strength
      0.4,  // radius
      0.85  // threshold
    )
    composer.addPass(bloomPass)
  }

  // 轨道控制器
  let controls = null
  if (enableControls) {
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.autoRotate = autoRotate
    controls.autoRotateSpeed = autoRotateSpeed
    controls.minDistance = 10
    controls.maxDistance = 500
    controls.maxPolarAngle = Math.PI / 2.1
  }

  // 灯光系统
  addLights(scene)

  // 网格辅助（可选）
  // const gridHelper = new THREE.GridHelper(200, 50, 0x111d33, 0x111d33)
  // scene.add(gridHelper)

  // 动画循环
  const animHandlers = []
  let animationId = null
  let isDestroyed = false

  function animate() {
    if (isDestroyed) return
    animationId = requestAnimationFrame(animate)
    controls?.update()
    animHandlers.forEach(handler => handler())
    if (composer) {
      composer.render()
    } else {
      renderer.render(scene, camera)
    }
  }

  function start() {
    if (!isDestroyed && !animationId) {
      animate()
    }
  }

  function stop() {
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
  }

  function addAnimationHandler(handler) {
    animHandlers.push(handler)
    return () => {
      const idx = animHandlers.indexOf(handler)
      if (idx > -1) animHandlers.splice(idx, 1)
    }
  }

  // 窗口自适应
  function onWindowResize() {
    if (isDestroyed) return
    const width = container.clientWidth
    const height = container.clientHeight
    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
    composer?.setSize(width, height)
  }

  window.addEventListener('resize', onWindowResize)

  // 销毁清理
  function destroy() {
    isDestroyed = true
    stop()
    window.removeEventListener('resize', onWindowResize)

    // 清理场景对象
    scene.traverse((object) => {
      if (object.geometry) object.geometry.dispose()
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(m => m.dispose())
        } else {
          object.material.dispose()
        }
      }
    })

    controls?.dispose()
    renderer.dispose()
    if (renderer.domElement && renderer.domElement.parentNode) {
      renderer.domElement.parentNode.removeChild(renderer.domElement)
    }
  }

  // 启动渲染循环
  start()

  return {
    scene,
    camera,
    renderer,
    composer,
    controls,
    animateHandlers: animHandlers,
    addAnimationHandler,
    start,
    stop,
    destroy,
    onWindowResize
  }
}

/**
 * 添加灯光系统
 */
function addLights(scene) {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0x404060, 0.6)
  scene.add(ambientLight)

  // 主方向光
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2)
  directionalLight.position.set(50, 100, 50)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  directionalLight.shadow.camera.near = 0.5
  directionalLight.shadow.camera.far = 500
  directionalLight.shadow.camera.left = -100
  directionalLight.shadow.camera.right = 100
  directionalLight.shadow.camera.top = 100
  directionalLight.shadow.camera.bottom = -100
  scene.add(directionalLight)

  // 补光
  const fillLight = new THREE.DirectionalLight(0x6688cc, 0.4)
  fillLight.position.set(-50, 50, -30)
  scene.add(fillLight)

  // 点光源（用于特效）
  const pointLight = new THREE.PointLight(0x00d4aa, 1.5, 200)
  pointLight.position.set(0, 30, 0)
  scene.add(pointLight)
}

/**
 * 创建碳排放柱状图（3D）
 * @param {number} x - X坐标
 * @param {number} y - Y坐标（高度）
 * @param {number} z - Z坐标
 * @param {number} value - 排放值
 * @param {Object} options - 样式选项
 * @returns {THREE.Group} 柱状图组
 */
export function createCarbonBar(x, y, z, value, options = {}) {
  const {
    maxHeight = 50,
    maxValue = 1000,
    colorLow = 0x00d4aa,   // 低碳-绿色
    colorHigh = 0xff4d4f,  // 高碳-红色
    width = 2,
    depth = 2
  } = options

  const height = Math.max(1, (value / maxValue) * maxHeight)
  const color = value < maxValue * 0.3 ? colorLow :
               value < maxValue * 0.7 ? 0xf39c12 : colorHigh

  const group = new THREE.Group()
  group.position.set(x, y, z)

  // 柱体
  const geometry = new THREE.BoxGeometry(width, height, depth)
  const material = new THREE.MeshPhongMaterial({
    color,
    emissive: color,
    emissiveIntensity: 0.2,
    transparent: true,
    opacity: 0.85
  })
  const bar = new THREE.Mesh(geometry, material)
  bar.position.y = height / 2
  bar.castShadow = true
  bar.receiveShadow = true
  group.add(bar)

  // 顶部发光效果
  const topGeometry = new THREE.BoxGeometry(width * 1.1, 0.3, depth * 1.1)
  const topMaterial = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0.6
  })
  const top = new THREE.Mesh(topGeometry, topMaterial)
  top.position.y = height
  group.add(top)

  // 存储数据
  group.userData = { value, height, color }
  return group
}

/**
 * 创建热力粒子系统
 * @param {number} count - 粒子数量
 * @param {Object} options - 配置选项
 * @returns {THREE.Points} 粒子系统
 */
export function createHeatParticle(count = 1000, options = {}) {
  const {
    spread = 100,
    minSize = 0.5,
    maxSize = 3,
    color = 0xff4d4f
  } = options

  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const sizes = new Float32Array(count)

  const colorObj = new THREE.Color(color)

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * spread
    positions[i * 3 + 1] = Math.random() * 30
    positions[i * 3 + 2] = (Math.random() - 0.5) * spread

    const mixFactor = Math.random()
    const particleColor = new THREE.Color().lerpColors(
      new THREE.Color(0x00d4aa),
      colorObj,
      mixFactor
    )

    colors[i * 3] = particleColor.r
    colors[i * 3 + 1] = particleColor.g
    colors[i * 3 + 2] = particleColor.b

    sizes[i] = minSize + Math.random() * (maxSize - minSize)
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))

  const material = new THREE.PointsMaterial({
    size: maxSize,
    vertexColors: true,
    transparent: true,
    opacity: 0.7,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true
  })

  const particles = new THREE.Points(geometry, material)
  particles.userData = { originalPositions: positions.slice() }
  return particles
}

/**
 * 创建能源流动线（粒子流动效果）
 * @param {THREE.Vector3} start - 起点
 * @param {THREE.Vector3} end - 终点
 * @param {Object} options - 配置选项
 * @returns {THREE.Group} 流动线组
 */
export function createFlowLine(start, end, options = {}) {
  const {
    particleCount = 100,
    color = 0x00d4aa,
    particleSize = 0.5,
    lineColor = 0x1890ff
  } = options

  const group = new THREE.Group()

  // 曲线路径
  const midPoint = new THREE.Vector3()
    .addVectors(start, end)
    .multiplyScalar(0.5)
  midPoint.y += 10

  const curve = new THREE.QuadraticBezierCurve3(start, midPoint, end)
  const points = curve.getPoints(50)

  // 基础线条
  const lineGeometry = new THREE.BufferGeometry().setFromPoints(points)
  const lineMaterial = new THREE.LineBasicMaterial({
    color: lineColor,
    transparent: true,
    opacity: 0.4
  })
  const line = new THREE.Line(lineGeometry, lineMaterial)
  group.add(line)

  // 流动粒子
  const particlePositions = new Float32Array(particleCount * 3)
  const particleSizes = new Float32Array(particleCount)

  for (let i = 0; i < particleCount; i++) {
    const t = i / particleCount
    const point = curve.getPoint(t)
    particlePositions[i * 3] = point.x
    particlePositions[i * 3 + 1] = point.y
    particlePositions[i * 3 + 2] = point.z
    particleSizes[i] = particleSize
  }

  const particleGeometry = new THREE.BufferGeometry()
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))
  particleGeometry.setAttribute('size', new THREE.BufferAttribute(particleSizes, 1))

  const particleMaterial = new THREE.PointsMaterial({
    color,
    size: particleSize * 2,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })

  const particles = new THREE.Points(particleGeometry, particleMaterial)
  group.add(particles)

  // 动画更新方法
  group.userData = {
    curve,
    particleCount,
    update: (time) => {
      const positions = particles.geometry.attributes.position.array
      for (let i = 0; i < particleCount; i++) {
        const t = ((time * 0.001 + i / particleCount) % 1)
        const point = curve.getPoint(t)
        positions[i * 3] = point.x
        positions[i * 3 + 1] = point.y
        positions[i * 3 + 2] = point.z
      }
      particles.geometry.attributes.position.needsUpdate = true
    }
  }

  return group
}

/**
 * 创建碳足迹节点（LCA树节点）
 * @param {string} label - 节点标签
 * @param {number} value - 排放值
 * @param {Object} options - 选项
 * @returns {THREE.Group} 节点组
 */
export function createFootprintNode(label, value, options = {}) {
  const {
    radius = 3,
    color = 0x00d4aa,
    isHigh = false
  } = options

  const group = new THREE.Group()

  // 球体
  const geometry = new THREE.SphereGeometry(radius, 32, 32)
  const material = new THREE.MeshPhongMaterial({
    color: isHigh ? 0xff4d4f : color,
    emissive: isHigh ? 0xff4d4f : color,
    emissiveIntensity: 0.3,
    shininess: 100
  })
  const sphere = new THREE.Mesh(geometry, material)
  sphere.castShadow = true
  group.add(sphere)

  // 光环
  const ringGeometry = new THREE.RingGeometry(radius * 1.3, radius * 1.5, 32)
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: isHigh ? 0xff4d4f : color,
    transparent: true,
    opacity: 0.3,
    side: THREE.DoubleSide
  })
  const ring = new THREE.Mesh(ringGeometry, ringMaterial)
  ring.rotation.x = -Math.PI / 2
  group.add(ring)

  group.userData = { label, value, isHigh }
  return group
}

/**
 * 创建数字孪生工厂建筑
 * @param {number} x - X坐标
 * @param {number} z - Z坐标
 * @param {Object} options - 选项
 * @returns {THREE.Group} 建筑组
 */
export function createFactoryBuilding(x, z, options = {}) {
  const {
    width = 20,
    height = 30,
    depth = 20,
    emissionValue = 0,
    label = '车间'
  } = options

  const group = new THREE.Group()
  group.position.set(x, 0, z)

  // 建筑主体
  const color = emissionValue < 100 ? 0x00d4aa :
                emissionValue < 500 ? 0xf39c12 : 0xff4d4f

  const geometry = new THREE.BoxGeometry(width, height, depth)
  const material = new THREE.MeshPhongMaterial({
    color,
    emissive: color,
    emissiveIntensity: 0.1,
    transparent: true,
    opacity: 0.9
  })
  const building = new THREE.Mesh(geometry, material)
  building.position.y = height / 2
  building.castShadow = true
  building.receiveShadow = true
  group.add(building)

  // 窗户
  const windowColor = new THREE.Color(0x1890ff)
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 2; j++) {
      const windowGeometry = new THREE.PlaneGeometry(width * 0.2, height * 0.1)
      const windowMaterial = new THREE.MeshBasicMaterial({
        color: windowColor,
        transparent: true,
        opacity: 0.6,
        side: THREE.DoubleSide
      })
      const windowMesh = new THREE.Mesh(windowGeometry, windowMaterial)
      windowMesh.position.set(
        -width * 0.3 + i * width * 0.3,
        height * 0.3 + j * height * 0.3,
        depth / 2 + 0.1
      )
      group.add(windowMesh)
    }
  }

  group.userData = { label, emissionValue, width, height, depth }
  return group
}

/**
 * 创建能源电池模型（储能SOC）
 * @param {THREE.Vector3} position - 位置
 * @param {number} soc - 电池SOC (0-1)
 * @returns {THREE.Group} 电池组
 */
export function createBatteryModel(position, soc = 0.8) {
  const group = new THREE.Group()
  group.position.copy(position)

  const batteryWidth = 8
  const batteryHeight = 15
  const batteryDepth = 5

  // 电池外壳
  const outerGeometry = new THREE.BoxGeometry(batteryWidth, batteryHeight, batteryDepth)
  const outerMaterial = new THREE.MeshPhongMaterial({
    color: 0x111d33,
    emissive: 0x111d33,
    emissiveIntensity: 0.1,
    wireframe: false
  })
  const outer = new THREE.Mesh(outerGeometry, outerMaterial)
  outer.position.y = batteryHeight / 2
  group.add(outer)

  // 电池电量填充
  const fillHeight = batteryHeight * Math.max(0.05, Math.min(1, soc))
  const fillGeometry = new THREE.BoxGeometry(batteryWidth * 0.9, fillHeight, batteryDepth * 0.9)
  const fillColor = soc > 0.7 ? 0x00d4aa : soc > 0.3 ? 0xf39c12 : 0xff4d4f
  const fillMaterial = new THREE.MeshPhongMaterial({
    color: fillColor,
    emissive: fillColor,
    emissiveIntensity: 0.4,
    transparent: true,
    opacity: 0.8
  })
  const fill = new THREE.Mesh(fillGeometry, fillMaterial)
  fill.position.y = fillHeight / 2
  group.add(fill)

  // 正极
  const terminalGeometry = new THREE.BoxGeometry(batteryWidth * 0.3, batteryHeight * 0.1, batteryDepth * 0.3)
  const terminalMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc })
  const terminal = new THREE.Mesh(terminalGeometry, terminalMaterial)
  terminal.position.y = batteryHeight + batteryHeight * 0.05
  group.add(terminal)

  group.userData = { soc, fillHeight }
  return group
}

/**
 * 工具函数：线性插值
 */
export function lerp(a, b, t) {
  return a + (b - a) * t
}

/**
 * 工具函数：将经纬度转换为3D坐标（用于地球模式）
 */
export function latLonToVector3(lat, lon, radius = 50) {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  const x = -(radius * Math.sin(phi) * Math.cos(theta))
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)
  return new THREE.Vector3(x, y, z)
}

export default {
  createThreeScene,
  createCarbonBar,
  createHeatParticle,
  createFlowLine,
  createFootprintNode,
  createFactoryBuilding,
  createBatteryModel,
  latLonToVector3,
  lerp
}
