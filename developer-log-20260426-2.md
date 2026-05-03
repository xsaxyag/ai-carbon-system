# AI碳枢算项目研发日志 2026-04-26 21:49

## 目标
继续推进AI碳枢算项目研发，重点解决OCR引擎安装和功能完善。

## 完成工作

### 1. OCR引擎切换：cnocr → RapidOCR
- **问题**: cnocr依赖HuggingFace下载模型(ch_PP-OCRv5_det_infer.onnx)，网络不通导致初始化失败
- **解决**: 安装`rapidocr_onnxruntime`（阿里镜像源），cnocr的底层引擎，更轻量无外部模型依赖
- **验证**: RapidOCR真实识别测试通过，英文识别置信度0.995

### 2. ocr.py 重构
- 引擎优先级: RapidOCR > EasyOCR
- 增强发票字段解析正则（发票代码/号码/金额/税额/价税合计多种格式）
- 优雅降级: OCR失败时自动切换模拟模式并标注`is_mock: true`
- 修复get_ocr_engine缓存机制，避免重复初始化失败

### 3. carbon_calc.py 修复
- 修复`" GJ"`键名多余空格
- 新增`RENEWABLE`的`kWh`单位（前端scope3绿电默认用kWh）
- scope3供应链排放自动乘1.2倍系数（简化模型）

### 4. OCRUpload.vue 修复
- viewReport按钮从emit改为`router.push('/report')`直接跳转
- 移除未使用的`defineEmits`

### 5. 端到端验证
- 企业创建 ✅
- scope1天然气/汽油录入 ✅
- scope2电力录入 ✅  
- scope3绿电录入（零排放）✅
- 碳汇总: scope1=1505, scope2=2905, scope3=0, 总计=4410 kgCO2 ✅
- 月度报告生成（含减排建议）✅
- OCR引擎状态检查 ✅
- RapidOCR真实识别测试 ✅

## 当前状态
- 后端: http://localhost:8000 (uvicorn, PID 18592)
- 前端: http://localhost:5173 (vite, PID 4080)
- OCR: RapidOCR就绪 ✅
- 5个页面路由全部正常: Dashboard/碳数据录入/OCR识别/企业管理/碳排报告

## 待后续推进
- 前端UI截图验证（浏览器受限未完成）
- 中文OCR识别效果测试（需真实发票图片）
- scope3排放因子细化和文档补充
- 大赛材料准备（PPT、演示视频等）
