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

# 本地知识库 - 当LLM不可用时使用
LOCAL_KNOWLEDGE = {
    "scope1": "Scope 1（直接排放）：企业直接控制的排放源，包括固定燃烧（天然气、煤炭、柴油）、移动燃烧（汽油车、柴油车）、工艺排放等。典型排放源：锅炉、窑炉、自有车辆、制冷剂泄漏。",
    "scope2": "Scope 2（外购电力间接排放）：企业外购电力、热力、蒸汽产生的间接排放。这是大多数中小企业最大的排放来源。减排措施：节能设备、绿电采购、分布式光伏。",
    "scope3": "Scope 3（价值链其他间接排放）：上下游供应链排放，包括商务差旅、员工通勤、采购商品、废物处理、产品使用等。核算复杂度最高，建议从主要类别开始。",
    "reduction": """通用减排建议（按成本效益排序）：
1. **管理优化**（零成本）：建立能耗监测体系，优化空调/照明使用习惯
2. **照明改造**（投资回收期1-2年）：LED替换+智能控制，节能50-70%
3. **电机升级**（回收期2-3年）：一级能效电机+变频控制，节能15-30%
4. **余热回收**（回收期2-4年）：回收废气/废水余热用于预热或供暖
5. **光伏发电**（回收期3-5年）：屋顶分布式光伏，自发自用余电上网
6. **绿电采购**（立即可行）：购买绿色电力证书或参与绿电交易""",
    "calculation": "碳排放计算公式：活动数据 × 排放因子 = CO2排放量。例如：用电10000kWh × 0.581kgCO2/kWh = 5810 kgCO2。排放因子参考GB/T 32150-2015和生态环境部发布的区域电网平均排放因子。",
    "policy": "中国双碳政策框架：2030年前碳达峰，2060年前碳中和。关键政策：《碳排放权交易管理办法》《企业温室气体排放核算与报告指南》（24个行业）。中小企业建议关注所在行业的碳核查要求。",
    "trading": "全国碳市场目前覆盖电力行业（年度排放2.6万吨CO2当量以上），未来将扩展到钢铁、水泥、化工等行业。碳价约80-100元/吨CO2（2024-2025年）。中小企业可通过CCER（国家核证自愿减排量）参与碳交易。",
}

# 关键词匹配规则
KEYWORD_RULES = [
    (["scope", "范围1", "直接排放"], "scope1"),
    (["scope", "范围2", "电力", "间接排放"], "scope2"),
    (["scope", "范围3", "供应链", "价值链"], "scope3"),
    (["减排", "降碳", "减少排放", "降低排放", "怎么减", "如何降低"], "reduction"),
    (["计算", "核算", "公式", "因子", "怎么算", "如何计算"], "calculation"),
    (["政策", "法规", "标准", "合规", "GB/T", "指南"], "policy"),
    (["交易", "碳市场", "碳配额", "CCER", "碳价", "买卖"], "trading"),
]


def _local_reply(user_message: str) -> str:
    """基于关键词匹配的本地知识库回复"""
    msg_lower = user_message.lower()
    
    # 匹配关键词
    matched_topics = []
    for keywords, topic in KEYWORD_RULES:
        if any(kw in msg_lower for kw in keywords):
            matched_topics.append(topic)
    
    if matched_topics:
        # 去重保持顺序
        seen = set()
        unique_topics = [t for t in matched_topics if not (t in seen or seen.add(t))]
        replies = [LOCAL_KNOWLEDGE[t] for t in unique_topics if t in LOCAL_KNOWLEDGE]
        
        reply = "\n\n".join(replies)
        return f"📚 **基于本地知识库的回答**\n\n{reply}\n\n> 💡 提示: 配置有效的AI大模型API Key后可获得更精准的个性化回答"
    
    # 无匹配时的通用回复
    return f"""📚 **AI碳枢算 - 智能顾问**

您好！我是AI碳枢算系统的智能顾问，专精于企业碳排放管理和碳中和咨询。

**我可以帮您解答：**
- 📊 碳排放核算方法（Scope 1/2/3）
- 📉 减排方案和成本效益分析
- 📋 碳中和政策法规解读
- 💱 碳交易和碳市场信息
- 🏭 行业对标和最佳实践

**您的问题涉及**: {user_message}

当前AI大模型服务暂时不可用（可能原因：API余额不足或网络问题），以上回复来自本地知识库。
如需更精准的分析，请在 backend/.env 中配置有效的 LLM_API_KEY 后重启服务。

常用问题可直接问我：
- "什么是Scope 1/2/3排放？"
- "如何降低企业的碳排放？"
- "碳排放怎么计算？"
- "碳交易是什么？\""""


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
    # 取最后一条用户消息
    last_user_msg = ""
    for m in reversed(req.messages):
        if m.role == "user":
            last_user_msg = m.content
            break

    if not llm_service.available:
        return ChatResponse(
            success=True,
            reply=_local_reply(last_user_msg),
            error=None  # 不再报错，而是返回本地知识库答案
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
        error_str = str(e)
        # LLM调用失败时优雅降级到本地知识库
        if "402" in error_str or "Insufficient" in error_str or "balance" in error_str.lower():
            return ChatResponse(
                success=True,
                reply=_local_reply(last_user_msg),
                error=None
            )
        # 其他错误也尝试降级
        return ChatResponse(
            success=True,
            reply=_local_reply(last_user_msg),
            error=f"LLM调用异常已自动降级: {error_str}"
        )


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
        # LLM失败时降级到规则引擎
        result = llm_service._mock_extract(req.ocr_text)
        return {
            "success": True,
            "data": result,
            "mode": "rule_engine_fallback",
            "warning": f"LLM提取失败，已降级为规则引擎: {str(e)}"
        }


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
        # LLM失败时降级到基础分析
        report = llm_service._mock_analysis(req.company_data, req.emission_records)
        return {
            "success": True,
            "report": report,
            "mode": "basic_fallback",
            "warning": f"LLM分析失败，已降级为基础分析: {str(e)}"
        }