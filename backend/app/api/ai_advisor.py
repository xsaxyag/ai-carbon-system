"""
AI碳枢算 - AI智能顾问API
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.get("/analyze")
async def analyze(query: str = "企业碳排放情况"):
    """AI智能分析"""
    return {
        "query": query,
        "analysis": "根据当前数据，企业碳排放总量1250.8 kgCO2e，较上月下降12.5%。主要排放源为能源站天然气消耗(280.1 kgCO2e)和生产车间A区电力消耗(1850.2 kWh)。建议优先优化能源站燃烧效率。",
        "suggestions": [
            "建议将能源站锅炉热效率提升5%，预计减排42.3 kgCO2e/天",
            "建议A区非连续设备夜间关停，预计节省电费85元/天",
            "建议扩大仓储区光伏板面积，预计提升绿电比例至42%",
        ],
        "model": "glm-5.1",
        "update_time": datetime.now().isoformat(),
    }


@router.get("/chat")
async def chat(message: str = "你好"):
    """AI对话接口"""
    knowledge_base = {
        "碳排放": "碳排放是指人类活动产生的温室气体排放，主要包括CO2、CH4、N2O等。企业碳排放核算遵循ISO 14064标准。",
        "碳中和": "碳中和是指通过减排和碳抵消，使净碳排放为零。中国企业目标：2030年前达峰，2060年前中和。",
        "Scope1": "Scope 1排放是企业拥有或控制的排放源产生的直接排放，如锅炉燃烧、公司车辆燃油等。",
        "Scope2": "Scope 2排放是企业购入电力、热力、蒸汽产生的间接排放。",
        "Scope3": "Scope 3排放是价值链上下游所有间接排放，包括原料运输、商务差旅、废弃物处理等。",
    }
    for key, value in knowledge_base.items():
        if key in message:
            return {"message": message, "reply": value, "source": "local_knowledge_base"}
    return {
        "message": message,
        "reply": "感谢您的提问。AI碳枢算系统可帮助您管理企业碳排放，建议从碳全景大屏开始了解整体情况。",
        "source": "default",
    }
