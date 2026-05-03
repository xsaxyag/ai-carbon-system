# AI碳枢算 - 开发进度

## 系统状态 (2026-04-25 23:58)

### ✅ 已完成
1. **后端API** - 运行中 http://localhost:8000
2. **前端页面** - 运行中 http://localhost:5174
3. **数据库** - SQLite持久化存储
4. **企业CRUD** - 增删改查
5. **碳数据录入** - 自动碳核算
6. **碳排放计算** - Scope 1/2/3
7. **报告生成** - 月度/季度/年度报告
8. **OCR框架** - 代码完整

### 🔄 安装中
- PaddleOCR - 正在下载(约105MB)

### API接口
| 路径 | 方法 | 功能 |
|-----|------|------|
| /api/v1/company/ | GET/POST | 企业管理 |
| /api/v1/carbon/records/ | GET/POST | 碳记录 |
| /api/v1/carbon/summary/{id}/ | GET | 碳汇总 |
| /api/v1/carbon/factors/ | GET | 排放因子 |
| /api/v1/report/report/{id}/ | GET | 报告 |
| /api/v1/ocr/recognize | POST | OCR识别 |

### 后续工作
1. 等PaddleOCR安装完成
2. 测试OCR发票识别
3. 完善前端页面