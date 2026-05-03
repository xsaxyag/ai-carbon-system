"""
AI碳枢算 - 后端入口
中小微企业碳中和智能管理系统
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
from pathlib import Path
from app.api import carbon, ocr, ai_advisor
from app.api.report import router as report_router
from app.api import carbon_asset, optimization, measures, alert, auth, backup, footprint, validation, wizard, price_alert

# 创建FastAPI应用
app = FastAPI(
    title="AI碳枢算 API",
    description="中小微企业碳中和智能管理系统 - 后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 限流配置
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 注册路由
app.include_router(carbon.router, prefix="/api/v1/carbon", tags=["碳数据管理"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR识别"])
app.include_router(report_router, prefix="/api/v1/report", tags=["报告管理"])
app.include_router(ai_advisor.router, prefix="/api/v1/ai-advisor", tags=["AI顾问"])
app.include_router(carbon_asset.router, prefix="/api/v1/carbon-asset", tags=["碳资产管理"])
app.include_router(optimization.router, prefix="/api/v1/optimization", tags=["降碳优化"])
app.include_router(measures.router, prefix="/api/v1/measures", tags=["措施库管理"])
app.include_router(alert.router, prefix="/api/v1/alert", tags=["碳排放预警"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证管理"])
app.include_router(backup.router, prefix="/api/v1/backup", tags=["数据备份"])
app.include_router(footprint.router, prefix="/api/v1/footprint", tags=["碳足迹追踪"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["数据校验"])
app.include_router(wizard.router, prefix="/api/v1/wizard", tags=["智能填报向导"])
app.include_router(price_alert.router, prefix="/api/v1/price-alert", tags=["碳价预警"])

@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """健康检查"""
    return {
        "status": "ok", 
        "message": "AI碳枢算 API 服务运行中",
        "version": "1.0.0"
    }

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )