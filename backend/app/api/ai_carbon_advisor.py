"""
AI碳枢算 - AI智能碳顾问API（增强版）
支持对话式碳管理：一句话指令完成LCA建模、碳报告生成、减排建议
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from app.services.llm_service import llm_service

router = APIRouter()


# === 请求/响应模型 ===

class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应"""
    reply: str
    action: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class LCA建模Request(BaseModel):
    """LCA建模请求"""
    product_name: str
    description: Optional[str] = None
    materials: Optional[List[Dict[str, Any]]] = None
    manufacturing_process: Optional[List[str]] = None
    transport_distance: Optional[float] = None


class OneCommandRequest(BaseModel):
    """一句话指令请求"""
    command: str
    params: Optional[Dict[str, Any]] = None


# === 意图识别 ===

INTENT_PATTERNS = {
    "lca_modeling": [
        r"建模.*LCA|LCA.*建模",
        r"产品碳足迹.*计算|计算.*产品碳足迹",
        r"帮我.*LCA|分析.*产品.*碳",
        r"生命周期.*分析|生命周期评价",
        r"(碳足迹|排放).*建模"
    ],
    "carbon_report": [
        r"生成.*碳.*报告|碳.*报告.*生成",
        r"导出.*报告|下载.*报告",
        r"(月度|年度|季度).*报告",
        r"ISO.*14064|14064.*报告"
    ],
    "emission_analysis": [
        r"分析.*排放|排放.*分析",
        r"企业.*碳.*情况|碳排放.*如何",
        r"scope.*分析|范围.*排放"
    ],
    "reduction_advice": [
        r"减排.*建议|如何.*减排",
        r"降碳.*方案|碳.*下降",
        r"优化.*能源|节能.*建议"
    ],
    "carbon_asset": [
        r"碳资产|CCER|VCS|碳信用",
        r"碳交易|碳市场|碳价",
        r"绿证|I-REC"
    ],
    "policy_inquiry": [
        r"碳.*政策|政策.*解读",
        r"碳中和.*目标|双碳.*政策",
        r"GB/T.*32150|ISO.*标准"
    ],
    "data_entry": [
        r"录入.*数据|添加.*排放",
        r"上传.*发票|导入.*数据"
    ]
}


def detect_intent(message: str) -> str:
    """识别用户意图"""
    message_lower = message.lower()
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return intent
    
    return "general_qa"


# === 功能实现 ===

@router.post("/chat", response_model=ChatResponse)
async def intelligent_chat(request: ChatRequest):
    """
    智能对话入口
    支持一句话指令完成多种碳管理任务
    """
    user_message = request.message
    intent = detect_intent(user_message)
    
    # 构建上下文
    context_str = ""
    if request.context:
        context_str = f"\n\n【用户当前数据】\n{json.dumps(request.context, ensure_ascii=False, indent=2)}"
    
    # 根据意图构建系统提示词
    system_prompts = {
        "lca_modeling": """你是产品碳足迹建模专家。用户会用自然语言描述产品，你需要：
1. 识别产品名称、功能单位、主要原材料、生产工艺
2. 生成LCA建模参数（JSON格式）
3. 给出默认排放因子推荐
4. 询问缺失的关键参数

回复格式：
【识别信息】
- 产品名称：xxx
- 功能单位：xxx
- 系统边界：xxx

【建模参数】（JSON）
{
  "product_name": "xxx",
  "functional_unit": "xxx",
  "materials": [...],
  "processes": [...]
}

【需要补充的信息】
- xxx
- xxx""",

        "carbon_report": """你是碳报告生成专家。用户会要求生成碳排放报告，你需要：
1. 识别报告类型（月度/季度/年度/ISO标准）
2. 确认报告周期和企业信息
3. 生成报告大纲
4. 询问是否需要导出PDF/Excel

回复格式：
【报告信息】
- 报告类型：xxx
- 报告周期：xxx
- 企业名称：xxx

【报告大纲】
1. 企业概述
2. 排放核算结果
3. 排放分析
4. 减排建议

【操作选项】
回复"确认生成"即可导出PDF报告""",

        "emission_analysis": """你是碳排放分析专家。你需要：
1. 分析企业排放数据（Scope1/2/3分布）
2. 识别主要排放源
3. 与行业基准对比
4. 给出减排优先级建议

回复格式：
【排放概况】
- 总排放量：xxx tCO2e
- Scope1：xxx tCO2e (xx%)
- Scope2：xxx tCO2e (xx%)
- Scope3：xxx tCO2e (xx%)

【主要排放源】
1. xxx：xx%
2. xxx：xx%

【行业对比】
贵单位排放强度低于行业平均水平xx%

【减排建议】
1. 优先优化xxx
2. 建议实施xxx""",

        "reduction_advice": """你是碳减排专家。你需要：
1. 分析当前排放源
2. 评估减排潜力
3. 给出成本效益分析
4. 制定减排路径

回复格式：
【减排方案】
| 措施 | 减排量 | 投资 | 回收期 |
|------|--------|------|--------|
| xxx  | xx tCO2e | xx万元 | x年 |

【优先级排序】
1. xxx（高潜力、低成本）
2. xxx（中潜力、中成本）
3. xxx（高潜力、高成本）

【实施路径】
- 近期（1年）：xxx
- 中期（3年）：xxx
- 远期（5年）：xxx""",

        "carbon_asset": """你是碳资产管理专家。你需要：
1. 解释碳信用类型（CCER/VCS/GS/I-REC）
2. 评估项目开发潜力
3. 分析碳价趋势
4. 给出交易建议

回复格式：
【碳资产建议】
- 推荐类型：xxx
- 预计收益：xx万元/年
- 开发周期：xx个月

【市场分析】
当前CCER价格：xx元/tCO2e
价格趋势：上涨/下跌/平稳

【操作建议】
xxx""",

        "policy_inquiry": """你是碳中和政策专家。你需要：
1. 解读国家/地方双碳政策
2. 解释相关标准（GB/T 32150、ISO 14064等）
3. 分析政策对企业的影响
4. 给出合规建议

回复格式：
【政策解读】
xxx

【适用标准】
- xxx
- xxx

【企业应对】
1. xxx
2. xxx""",

        "general_qa": """你是AI碳枢算系统的智能顾问，专精于企业碳排放管理。

你的能力：
1. 碳排放咨询：解答碳排放核算、碳交易、碳足迹等问题
2. 政策解读：解读中国双碳政策法规
3. 减排建议：基于企业数据提供定制化减排方案
4. 合规指导：帮助中小企业了解碳排放报告要求

回答规范：
- 务实具体，给出可执行方案
- 数据引用需注明来源
- 对中小企业场景给出成本效益分析"""
    }
    
    system_prompt = system_prompts.get(intent, system_prompts["general_qa"])
    
    # 构建完整消息
    messages = [
        {"role": "system", "content": system_prompt + context_str},
        {"role": "user", "content": user_message}
    ]
    
    # 调用LLM
    try:
        if llm_service.available:
            reply = await llm_service.chat(messages, temperature=0.7)
        else:
            reply = _fallback_reply(user_message, intent)
    except Exception as e:
        reply = f"抱歉，AI服务暂时不可用。错误：{str(e)}\n\n您可以尝试更具体的问题，或稍后再试。"
    
    # 提取建议操作
    action = None
    action_data = None
    suggestions = None
    
    if intent == "lca_modeling" and "【建模参数】" in reply:
        # 尝试提取JSON参数
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', reply, re.DOTALL)
        if json_match:
            try:
                action_data = json.loads(json_match.group(1))
                action = "create_lca_model"
            except:
                pass
    
    if intent == "carbon_report" and "确认生成" in reply:
        action = "generate_report"
        action_data = {"report_type": "iso14064"}
    
    # 生成建议追问
    suggestions = _generate_suggestions(intent, reply)
    
    return ChatResponse(
        reply=reply,
        action=action,
        action_data=action_data,
        suggestions=suggestions
    )


@router.post("/lca/model")
async def create_lca_model(request: LCA建模Request):
    """
    创建LCA模型
    一句话指令："帮我建模iPhone 15 Pro的LCA"
    """
    # 构建建模prompt
    prompt = f"""请为以下产品创建LCA碳足迹模型：

产品名称：{request.product_name}
产品描述：{request.description or '（用户未提供）'}
主要原材料：{json.dumps(request.materials, ensure_ascii=False) if request.materials else '（用户未提供，请推荐常见材料）'}
生产工艺：{request.manufacturing_process or '（用户未提供，请推荐常见工艺）'}
运输距离：{request.transport_distance or '（用户未提供）'}

请输出：
1. 产品信息摘要
2. LCA建模参数（JSON格式）
3. 各阶段碳排放估算
4. 数据质量评估
5. 改进建议
"""
    
    try:
        if llm_service.available:
            result = await llm_service.chat([
                {"role": "system", "content": "你是产品LCA建模专家，精通ISO 14067标准。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
        else:
            result = _fallback_lca_model(request)
        
        return {
            "product_name": request.product_name,
            "model_result": result,
            "status": "success",
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LCA建模失败：{str(e)}")


@router.get("/quick-commands")
async def get_quick_commands():
    """获取快捷指令列表"""
    return {
        "commands": [
            {
                "id": "lca_model",
                "command": "帮我建模{name}的LCA",
                "description": "快速创建产品LCA模型",
                "example": "帮我建模iPhone 15 Pro的LCA",
                "category": "建模"
            },
            {
                "id": "carbon_report",
                "command": "生成{period}碳报告",
                "description": "生成碳排放报告",
                "example": "生成2025年度碳报告",
                "category": "报告"
            },
            {
                "id": "emission_analysis",
                "command": "分析企业碳排放情况",
                "description": "分析当前排放数据",
                "example": "分析企业碳排放情况",
                "category": "分析"
            },
            {
                "id": "reduction_advice",
                "command": "如何降低碳排放",
                "description": "获取减排建议",
                "example": "如何降低碳排放",
                "category": "减排"
            },
            {
                "id": "carbon_price",
                "command": "当前CCER价格多少",
                "description": "查询碳价信息",
                "example": "当前CCER价格多少",
                "category": "碳资产"
            },
            {
                "id": "policy_brief",
                "command": "解读{policy}",
                "description": "政策解读",
                "example": "解读双碳政策",
                "category": "政策"
            },
            {
                "id": "scope_guide",
                "command": "什么是Scope{1/2/3}",
                "description": "排放范围解释",
                "example": "什么是Scope1排放",
                "category": "知识"
            },
            {
                "id": "export_report",
                "command": "导出ISO 14064报告",
                "description": "导出标准格式报告",
                "example": "导出ISO 14064报告",
                "category": "导出"
            }
        ]
    }


@router.post("/one-command")
async def execute_one_command(request: OneCommandRequest):
    """
    一句话指令执行入口
    示例：
    - "帮我建模iPhone的LCA"
    - "生成2025年碳报告"
    - "分析企业排放"
    - "如何降低碳排放"
    """
    command = request.command
    params = request.params
    intent = detect_intent(command)
    
    # 根据意图执行对应操作
    if intent == "lca_modeling":
        # 提取产品名称
        product_match = re.search(r"建模(.+?)的?LCA|(.+?)的LCA", command)
        product_name = product_match.group(1) or product_match.group(2) if product_match else "未知产品"
        
        return {
            "intent": intent,
            "action": "create_lca_model",
            "params": {"product_name": product_name.strip()},
            "message": f"正在为「{product_name.strip()}」创建LCA模型..."
        }
    
    elif intent == "carbon_report":
        # 提取报告类型
        period_match = re.search(r"(\d{4})年?|月度|季度|年度", command)
        period = period_match.group(0) if period_match else "年度"
        
        return {
            "intent": intent,
            "action": "generate_carbon_report",
            "params": {"period": period},
            "message": f"正在生成{period}碳排放报告..."
        }
    
    elif intent == "emission_analysis":
        return {
            "intent": intent,
            "action": "analyze_emissions",
            "params": {},
            "message": "正在分析企业碳排放数据..."
        }
    
    elif intent == "reduction_advice":
        return {
            "intent": intent,
            "action": "get_reduction_advice",
            "params": {},
            "message": "正在生成减排建议..."
        }
    
    elif intent == "carbon_asset":
        return {
            "intent": intent,
            "action": "query_carbon_asset",
            "params": {},
            "message": "正在查询碳资产信息..."
        }
    
    else:
        # 通用问答
        return {
            "intent": "general_qa",
            "action": "chat",
            "params": {"message": command},
            "message": "正在思考..."
        }


# === 辅助函数 ===

def _fallback_reply(message: str, intent: str) -> str:
    """LLM不可用时的降级回复"""
    fallback_replies = {
        "lca_modeling": """【产品碳足迹建模】

请提供以下信息以完成LCA建模：
1. 产品名称
2. 功能单位（如：1件、1kg、100km等）
3. 主要原材料（名称、用量）
4. 生产工艺流程
5. 运输方式及距离

示例：
- 产品名称：锂电池
- 功能单位：1kWh
- 原材料：锂 0.1kg、钴 0.05kg
- 工艺：配料→涂布→卷绕→注液""",

        "carbon_report": """【碳排放报告生成】

请确认以下信息：
1. 报告类型：月度/季度/年度
2. 报告周期：如2025年1月
3. 是否需要ISO 14064标准格式

确认后可导出PDF/Excel报告。""",

        "emission_analysis": """【排放分析】

当前系统已记录以下排放数据：
- Scope 1（直接排放）：暂无数据
- Scope 2（间接排放）：暂无数据
- Scope 3（其他间接）：暂无数据

建议先录入能源消耗数据后再进行分析。""",

        "reduction_advice": """【减排建议】

常见减排措施：
1. 节能改造：LED照明、变频空调、高效电机
2. 绿色能源：光伏发电、购买绿电
3. 工艺优化：减少废品率、精益生产
4. 碳抵消：购买CCER、碳汇林

请提供具体排放数据，以获得定制化建议。""",

        "carbon_asset": """【碳资产信息】

当前支持：
- CCER（中国核证自愿减排量）
- VCS（国际核证碳标准）
- GS（黄金标准）
- I-REC（国际可再生能源证书）

请提供项目信息（类型、规模、地点），以评估开发潜力。""",

        "policy_inquiry": """【政策参考】

中国双碳目标：
- 2030年前碳达峰
- 2060年前碳中和

主要政策：
- 《碳排放权交易管理办法》
- GB/T 32150-2015 工业企业温室气体排放核算通则
- ISO 14064 组织碳核算标准
- ISO 14067 产品碳足迹标准""",

        "general_qa": """您好！我是AI碳枢算智能顾问。

我可以帮您：
1. 产品碳足迹LCA建模
2. 企业碳排放分析
3. 生成ISO标准报告
4. 减排方案建议
5. 碳资产管理咨询

请问有什么可以帮您的？"""
    }
    
    return fallback_replies.get(intent, fallback_replies["general_qa"])


def _fallback_lca_model(request: LCA建模Request) -> str:
    """降级LCA建模"""
    return f"""【LCA建模结果】

产品名称：{request.product_name}

一、系统边界
采用"摇篮到大门"边界，包含原材料获取、生产制造阶段。

二、建模参数
- 功能单位：1件
- 系统边界：摇篮到大门
- 数据质量：中等（部分数据为行业平均值）

三、各阶段排放估算
| 阶段 | 排放量(kgCO2e) | 占比 |
|------|----------------|------|
| 原材料 | 待补充 | ~50% |
| 生产 | 待补充 | ~30% |
| 运输 | 待补充 | ~20% |

四、改进建议
1. 补充原材料用量数据
2. 提供生产能耗数据
3. 确认运输距离和方式

请补充以上数据以提高建模精度。"""


def _generate_suggestions(intent: str, reply: str) -> List[str]:
    """生成追问建议"""
    suggestions_map = {
        "lca_modeling": [
            "查看排放因子库",
            "补充原材料数据",
            "生成产品碳足迹报告"
        ],
        "carbon_report": [
            "确认生成报告",
            "修改报告周期",
            "查看报告模板"
        ],
        "emission_analysis": [
            "查看排放源详情",
            "对比历史数据",
            "生成减排方案"
        ],
        "reduction_advice": [
            "评估投资回报",
            "制定实施计划",
            "申请绿色金融支持"
        ],
        "carbon_asset": [
            "评估项目潜力",
            "查询实时碳价",
            "模拟碳交易"
        ],
        "policy_inquiry": [
            "下载政策文件",
            "查看合规清单",
            "咨询专家"
        ]
    }
    
    return suggestions_map.get(intent, [
        "了解更多",
        "查看数据",
        "联系专家"
    ])
