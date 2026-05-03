# AI碳枢算开发任务记录

## 开发时间
2026-04-25

## 项目概述
AI碳枢算 - 中小微企业碳中和智能管理系统 Demo

## 已完成内容

### 后端 (FastAPI)
- `/backend/app/main.py` - FastAPI入口，配置CORS跨域
- `/backend/app/models/schemas.py` - 数据模型（企业、碳记录、OCR结果）
- `/backend/app/services/carbon_calc.py` - 碳排放计算服务（含排放因子库）
- `/backend/app/api/carbon.py` - 碳数据管理API
- `/backend/app/api/ocr.py` - OCR识别API
- `/backend/app/api/company.py` - 企业管理API

### 前端 (Vue 3)
- `/frontend/src/App.vue` - 主布局
- `/frontend/src/views/Dashboard.vue` - 数据概览页
- `/frontend/src/views/CarbonEntry.vue` - 碳数据录入页
- `/frontend/src/views/OCRUpload.vue` - OCR识别页
- `/frontend/src/views/CompanyManage.vue` - 企业管理页

## 核心功能
1. 碳数据录入 + 自动核算
2. OCR发票识别
3. 企业管理
4. 数据可视化

## 启动方式
```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 待解决问题
- PaddleOCR安装可能需要较大空间
- 数据库应从内存切换到MySQL