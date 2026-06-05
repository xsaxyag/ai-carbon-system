const fs = require('fs');

const filePath = 'D:/ai-carbon-system/frontend/src/views/SiteMap3D.vue';
let content = fs.readFileSync(filePath, 'utf8');

// 1. Add echarts import
if (!content.includes("import * as echarts")) {
    content = content.replace(
        "import { OrbitControls } from 'three/addons/controls/OrbitControls.js'",
        "import { OrbitControls } from 'three/addons/controls/OrbitControls.js'\nimport * as echarts from 'echarts'"
    );
}

// 2. Add new state variables
content = content.replace(
    'const threeContainer = ref(null)',
    `const threeContainer = ref(null)
const trendChart = ref(null)
const carbonTrendData = ref(null)
const optimizationSuggestions = ref(null)`
);

// 3. Add new functions
const newFunctions = `// 获取优化建议类型名称
const getSuggestionTypeName = (type) => {
  const names = {
    '屋顶光伏': '屋顶光伏', '绿电采购': '绿电采购', '空压机节能': '空压机节能',
    'LED照明': 'LED照明', '能源管理': '能源管理', '储能系统': '储能系统'
  }
  return names[type] || type
}

// 获取优化建议标签类型
const getSuggestionTagType = (type) => {
  const types = {
    '屋顶光伏': 'warning', '绿电采购': 'success', '空压机节能': 'info',
    'LED照明': '', '能源管理': 'danger', '储能系统': ''
  }
  return types[type] || ''
}

// 获取碳趋势数据
const fetchCarbonTrend = async () => {
  try {
    const response = await fetch(\`\${API_BASE}/site-map/carbon-trend?company_id=1\`)
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        carbonTrendData.value = data
        renderTrendChart(data)
      }
    }
  } catch (error) {
    console.error('获取碳趋势数据失败:', error)
  }
}

// 渲染趋势图表
const renderTrendChart = (data) => {
  nextTick(() => {
    const chartDom = document.querySelector('.trend-chart')
    if (!chartDom) return
    const chart = echarts.init(chartDom)
    const months = data.trend.map(t => t.month)
    const emissions = data.trend.map(t => t.emission)
    const greenRatios = data.trend.map(t => t.green_ratio)
    const option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['碳排放量(tCO2)', '绿电比例(%)'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: months, boundaryGap: false },
      yAxis: [
        { type: 'value', name: '碳排放(tCO2)', position: 'left' },
        { type: 'value', name: '绿电比例(%)', min: 0, max: 50, position: 'right' }
      ],
      series: [
        { name: '碳排放量(tCO2)', type: 'bar', data: emissions, itemStyle: { color: '#f56c6c' } },
        { name: '绿电比例(%)', type: 'line', yAxisIndex: 1, data: greenRatios, smooth: true,
          lineStyle: { color: '#67c23a', width: 3 },
          areaStyle: { color: 'rgba(103, 194, 58, 0.2)' }
        }
      ]
    }
    chart.setOption(option)
    trendChart.value = chart
  })
}

// 获取优化建议
const fetchOptimizationSuggestions = async () => {
  try {
    const response = await fetch(\`\${API_BASE}/site-map/optimization-suggestions?company_id=1\`)
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        optimizationSuggestions.value = data.suggestions
      }
    }
  } catch (error) {
    console.error('获取优化建议失败:', error)
  }
}

// 获取减排潜力进度条颜色
const getReductionProgressColor`;

content = content.replace(
    '// 获取减排潜力进度条颜色\nconst getReductionProgressColor',
    newFunctions
);

// 4. Add template cards
const chartCard = `
      <!-- 碳排放趋势图表 -->
      <el-card v-if="sceneReady" class="trend-chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>📈 碳排放趋势分析</span>
            <el-button type="primary" size="small" @click="fetchCarbonTrend">刷新数据</el-button>
          </div>
        </template>
        <div ref="trendChart" class="trend-chart"></div>
      </el-card>

      <!-- 减排优化建议 -->
      <el-card v-if="sceneReady" class="optimization-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>💡 减排优化建议</span>
            <el-button type="success" size="small" @click="fetchOptimizationSuggestions">
              查看完整方案
            </el-button>
          </div>
        </template>
        <el-row :gutter="20" v-if="optimizationSuggestions">
          <el-col :xs="24" :sm="12" :md="8" v-for="s in optimizationSuggestions.slice(0, 3)" :key="s.priority">
            <el-card class="suggestion-card" shadow="hover">
              <template #header>
                <div class="suggestion-header">
                  <el-tag :type="getSuggestionTagType(s.type)">{{ getSuggestionTypeName(s.type) }}</el-tag>
                  <span class="priority-badge">#{{ s.priority }}</span>
                </div>
              </template>
              <h4>{{ s.title }}</h4>
              <p class="suggestion-desc">{{ s.description }}</p>
              <div class="suggestion-stats">
                <div class="stat-row">
                  <span class="label">预计减排:</span>
                  <span class="value reduction">{{ s.estimated_reduction }} tCO2</span>
                </div>
                <div class="stat-row">
                  <span class="label">投资:</span>
                  <span class="value">{{ s.investment > 0 ? s.investment + '万元' : '无额外投资' }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-else description="点击"查看完整方案"加载优化建议" />
      </el-card>
`;

content = content.replace(
    '    <!-- 建筑信息抽屉 -->',
    chartCard + '    <!-- 建筑信息抽屉 -->'
);

// 5. Add CSS
const newCSS = `.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.trend-chart-card {
  margin-bottom: 20px;
}

.trend-chart {
  width: 100%;
  height: 300px;
}

.optimization-card {
  margin-bottom: 20px;
}

.suggestion-card {
  margin-bottom: 15px;
  height: 100%;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.priority-badge {
  background: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.suggestion-card h4 {
  margin: 10px 0;
  font-size: 16px;
  color: #303133;
}

.suggestion-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.5;
}

.suggestion-stats {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 13px;
}

.stat-row .label {
  color: #909399;
}

.stat-row .value {
  color: #303133;
  font-weight: 500;
}

.stat-row .value.reduction {
  color: #67c23a;
  font-weight: bold;
}

.stat-row .value.roi {
  color: #409eff;
}`;

content = content.replace(
    '.stat-label {\n  font-size: 14px;\n  color: #909399;\n  margin-top: 5px;\n}',
    newCSS
);

fs.writeFileSync(filePath, content, 'utf8');
console.log('Successfully updated SiteMap3D.vue');
