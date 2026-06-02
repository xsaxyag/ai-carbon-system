"""
AI碳枢算 - 后端入口
中小微企业碳中和智能管理系统 V2.0
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
from pathlib import Path
from app.api import carbon, ocr, ai_advisor
from app.api.report import router as report_router
from app.api import optimization, measures, alert, auth, backup, footprint, validation, wizard
from app.api import carbon_3d, footprint_3d, digital_twin, supply_chain, energy_synergy

# 创建FastAPI应用
app = FastAPI(
    title="AI碳枢算 API",
    description="中小微企业碳中和智能管理系统 V2.0 - 3D可视化增强版",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 限流配置
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 自定义CORS中间件
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

app.add_middleware(CustomCORSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 注册路由
app.include_router(carbon.router, prefix="/api/v1/carbon", tags=["碳数据管理"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR识别"])
app.include_router(report_router, prefix="/api/v1/report", tags=["报告管理"])
app.include_router(ai_advisor.router, prefix="/api/v1/ai-advisor", tags=["AI顾问"])
app.include_router(optimization.router, prefix="/api/v1/optimization", tags=["降碳优化"])
app.include_router(measures.router, prefix="/api/v1/measures", tags=["措施库管理"])
app.include_router(alert.router, prefix="/api/v1/alert", tags=["碳排放预警"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证管理"])
app.include_router(backup.router, prefix="/api/v1/backup", tags=["数据备份"])
app.include_router(footprint.router, prefix="/api/v1/footprint", tags=["碳足迹追踪"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["数据校验"])
app.include_router(wizard.router, prefix="/api/v1/wizard", tags=["智能填报向导"])
# V2.0 3D可视化模块
app.include_router(carbon_3d.router, prefix="/api/v1/carbon-3d", tags=["3D碳全景"])
app.include_router(footprint_3d.router, prefix="/api/v1/footprint-3d", tags=["碳足迹3D追踪"])
app.include_router(digital_twin.router, prefix="/api/v1/digital-twin", tags=["数字孪生工厂"])
app.include_router(supply_chain.router, prefix="/api/v1/supply-chain", tags=["供应链碳图谱"])
app.include_router(energy_synergy.router, prefix="/api/v1/energy-synergy", tags=["源网荷储协同"])

@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    return {"status": "ok", "message": "AI碳枢算 API V2.0 服务运行中", "version": "2.0.0"}

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
