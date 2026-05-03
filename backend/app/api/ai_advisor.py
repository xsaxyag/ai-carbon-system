"""
AI碳枢算 - AI顾问API
集成大语言模型，提供智能碳排放咨询和OCR智能提取
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.llm_service import llm_service
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


# ========== 请求/响应模型 ==========

class ChatMessage(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=20, description="对话消息")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度0-2")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="最大token数")


class ChatResponse(BaseModel):
    success: bool
    reply: str
    error: Optional[str] = None


class OCRExtractRequest(BaseModel):
    """OCR智能提取请求"""
    ocr_text: str = Field(..., min_length=1, max_length=10000, description="OCR识别的原始文本")
    use_llm: Optional[bool] = True


class AnalyzeRequest(BaseModel):
    """企业碳排放分析请求"""
    company_data: dict = Field(..., description="企业基本信息")
    emission_records: list = Field(..., max_length=500, description="碳排放记录")


# ========== API端点 ==========

@router.get("/status")
async def ai_status():
    """获取AI服务状态"""
    status = llm_service.get_status()
    return {
        "available": status["available"],
        "model": status["model"],
        "base_url": status["base_url"],
        "api_key_configured": status["api_key_configured"],
        "message": "AI顾问服务就绪" if status["available"] else f"AI服务未配置: {status.get('error', '请设置API Key')}"
    }


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_advisor(request: Request, req: ChatRequest):
    """
    与AI顾问对话

    - messages: 对话消息列表
    - temperature: 生成温度（0-1）
    - max_tokens: 最大token数
    """
    if not llm_service.available:
        return ChatResponse(
            success=False,
            reply="AI顾问服务当前不可用。请在 backend/.env 中配置有效的 LLM_API_KEY 和 LLM_BASE_URL 后重启服务。\n\n"
                  "支持的平台：\n"
                  "• DeepSeek: https://platform.deepseek.com\n"
                  "• 通义千问: https://dashscope.aliyuncs.com\n"
                  "• 硅基流动: https://cloud.siliconflow.cn\n"
                  "• 本地Ollama: http://localhost:11434/v1",
            error="LLM服务不可用"
        )

    try:
        # 转换消息格式
        messages = [{"role": m.role, "content": m.content} for m in req.messages]

        reply = llm_service.chat(
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens
        )
        return ChatResponse(success=True, reply=reply)
    except Exception as e:
        return ChatResponse(success=False, reply=f"请求失败: {str(e)}", error=str(e))


@router.post("/extract")
@limiter.limit("15/minute")
async def extract_ocr_data(request: Request, req: OCRExtractRequest):
    """
    从OCR文本中智能提取碳相关数据

    - ocr_text: OCR识别的原始文本
    - use_llm: 是否使用LLM（false时使用规则引擎）
    """
    if not req.ocr_text or not req.ocr_text.strip():
        raise HTTPException(status_code=400, detail="OCR文本不能为空")

    try:
        if req.use_llm and llm_service.available:
            result = llm_service.extract_ocr_data(req.ocr_text)
        else:
            result = llm_service._mock_extract(req.ocr_text)

        return {
            "success": True,
            "data": result,
            "mode": "llm" if (req.use_llm and llm_service.available) else "rule_engine"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_emission(request: Request, req: AnalyzeRequest):
    """
    分析企业碳排放数据，生成定制化报告

    - company_data: 企业基本信息
    - emission_records: 碳排放记录列表
    """
    try:
        report = llm_service.analyze_company_emission(
            company_data=req.company_data,
            emission_records=req.emission_records
        )
        return {
            "success": True,
            "report": report,
            "mode": "llm" if llm_service.available else "basic"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
