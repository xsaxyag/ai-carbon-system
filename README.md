# AI碳枢算 - 中小微企业碳中和智能管理系统

## 项目结构

```
ai-carbon-system/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   └── main.py       # 入口
│   ├── requirements.txt   # 依赖
│   └── .env             # 环境变量
│
└── frontend/             # Vue 3前端
    ├── src/
    │   ├── api/         # API调用
    │   ├── components/  # 组件
    │   ├── views/      # 页面
    │   └── router/     # 路由
    └── package.json
```

## 功能清单

- [x] 碳数据录入（企业信息、能耗数据）
- [x] OCR发票识别（上传图片→结构化数据）
- [x] 碳排放核算（Scope 1/2/3计算）
- [x] 数据可视化（ECharts图表）
- [ ] 报告生成
- [ ] 预测模型

## 快速启动

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```