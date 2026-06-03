"""
AI碳枢算 - 碳资产管理API
支持CCER、VCS、GS、I-REC等碳信用开发、评估、交易辅助
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import math

router = APIRouter()

# 碳信用类型配置
CARBON_CREDIT_TYPES = {
    "CCER": {
        "name": "中国核证自愿减排量",
        "standard": "China Certified Emission Reduction",
        "registry": "中国自愿减排交易信息中心",
        "verification_period": "1-3年",
        "min_project_size": 10000,  # tCO2e
        "typical_price_range": [20, 80],  # 元/tCO2e
        "sectors": ["可再生能源", "林业碳汇", "甲烷利用", "节能改造"]
    },
    "VCS": {
        "name": "Verified Carbon Standard",
        "standard": "Verra VCS",
        "registry": "Verra Registry",
        "verification_period": "1-5年",
        "min_project_size": 5000,
        "typical_price_range": [5, 30],  # USD/tCO2e
        "sectors": ["林业", "可再生能源", "农业", "工业节能"]
    },
    "GS": {
        "name": "Gold Standard",
        "standard": "Gold Standard for Global Goals",
        "registry": "Gold Standard Registry",
        "verification_period": "2-5年",
        "min_project_size": 5000,
        "typical_price_range": [10, 50],  # USD/tCO2e
        "sectors": ["可再生能源", "清洁炉灶", "林业", "水资源"]
    },
    "I-REC": {
        "name": "国际可再生能源证书",
        "standard": "International REC Standard",
        "registry": "I-REC Standard Foundation",
        "verification_period": "1年",
        "min_project_size": 1000,  # MWh
        "typical_price_range": [5, 30],  # 元/MWh
        "sectors": ["光伏", "风电", "水电", "生物质发电"]
    }
}

# 碳资产开发阶段
DEVELOPMENT_STAGES = [
    {"id": "identification", "name": "项目识别", "duration_days": 30, "success_rate": 0.9},
    {"id": "validation", "name": "项目审定", "duration_days": 60, "success_rate": 0.85},
    {"id": "registration", "name": "项目注册", "duration_days": 45, "success_rate": 0.95},
    {"id": "monitoring", "name": "监测期", "duration_days": 365, "success_rate": 0.9},
    {"id": "verification", "name": "核查期", "duration_days": 60, "success_rate": 0.85},
    {"id": "issuance", "name": "签发", "duration_days": 30, "success_rate": 0.95}
]


@router.get("/types")
async def get_carbon_credit_types():
    """获取支持的碳信用类型"""
    return {
        "types": [
            {
                "id": k,
                "name": v["name"],
                "standard": v["standard"],
                "registry": v["registry"],
                "verification_period": v["verification_period"],
                "min_project_size": v["min_project_size"],
                "typical_price_range": v["typical_price_range"],
                "sectors": v["sectors"]
            }
            for k, v in CARBON_CREDIT_TYPES.items()
        ],
        "update_time": datetime.now().isoformat()
    }


@router.get("/price/{credit_type}")
async def get_carbon_credit_price(credit_type: str):
    """获取碳信用实时价格（模拟）"""
    if credit_type.upper() not in CARBON_CREDIT_TYPES:
        raise HTTPException(status_code=404, detail="不支持的碳信用类型")
    
    credit_config = CARBON_CREDIT_TYPES[credit_type.upper()]
    price_range = credit_config["typical_price_range"]
    
    # 模拟价格波动
    base_price = (price_range[0] + price_range[1]) / 2
    current_price = base_price * (1 + random.uniform(-0.1, 0.1))
    
    # 生成30天历史价格
    history = []
    for i in range(30):
        day_price = base_price * (1 + random.uniform(-0.15, 0.15))
        history.append({
            "date": (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d"),
            "price": round(day_price, 2),
            "volume": random.randint(1000, 50000)
        })
    
    return {
        "credit_type": credit_type.upper(),
        "credit_name": credit_config["name"],
        "current_price": round(current_price, 2),
        "unit": "USD/tCO2e" if credit_type.upper() in ["VCS", "GS"] else "元/tCO2e" if credit_type.upper() == "CCER" else "元/MWh",
        "change_24h": round(random.uniform(-5, 5), 2),
        "change_30d": round(random.uniform(-10, 10), 2),
        "volume_24h": random.randint(10000, 100000),
        "history": history,
        "update_time": datetime.now().isoformat()
    }


@router.post("/project/assess")
async def assess_carbon_project(project_data: Dict[str, Any]):
    """
    评估碳资产项目开发潜力
    
    输入参数：
    - project_type: 项目类型（renewable_energy/forestry/methane/energy_efficiency）
    - sector: 行业
    - scale: 规模（MW for renewable, ha for forestry）
    - location: 地点
    - estimated_annual_emission_reduction: 预计年减排量（tCO2e）
    """
    project_type = project_data.get("project_type", "renewable_energy")
    scale = project_data.get("scale", 100)
    annual_reduction = project_data.get("estimated_annual_emission_reduction", 1000)
    location = project_data.get("location", "华东")
    
    # 推荐最适合的碳信用类型
    recommendations = []
    
    # CCER适合中国境内项目
    if location in ["华东", "华北", "华南", "西南", "西北", "东北"]:
        ccerv = annual_reduction * random.uniform(30, 60)  # 预估收益
        recommendations.append({
            "type": "CCER",
            "name": "中国核证自愿减排量",
            "suitability_score": random.uniform(0.8, 0.95),
            "estimated_annual_credits": int(annual_reduction * 0.9),  # 考虑损耗
            "estimated_annual_revenue": int(ccerv),
            "development_period_months": random.randint(18, 24),
            "development_cost": int(annual_reduction * random.uniform(5, 15)),
            "roi": round(ccerv / (annual_reduction * 10) * 100, 1),
            "pros": ["国内认可度高", "交易便捷", "政策支持"],
            "cons": ["价格波动大", "审定周期长"]
        })
    
    # VCS适合国际项目
    if scale >= 10:  # 10MW以上项目适合VCS
        vcs_value = annual_reduction * random.uniform(8, 20)  # USD
        recommendations.append({
            "type": "VCS",
            "name": "Verified Carbon Standard",
            "suitability_score": random.uniform(0.7, 0.85),
            "estimated_annual_credits": int(annual_reduction * 0.85),
            "estimated_annual_revenue": int(vcs_value * 7),  # 汇率转换
            "development_period_months": random.randint(12, 18),
            "development_cost": int(annual_reduction * random.uniform(3, 8)),
            "roi": round(vcs_value * 7 / (annual_reduction * 5) * 100, 1),
            "pros": ["国际认可", "市场流动性好", "审核相对快"],
            "cons": ["需第三方机构", "汇率风险"]
        })
    
    # Gold Standard适合可持续发展项目
    if project_type in ["renewable_energy", "forestry", "clean_cooking"]:
        gs_value = annual_reduction * random.uniform(15, 35)  # USD
        recommendations.append({
            "type": "GS",
            "name": "Gold Standard",
            "suitability_score": random.uniform(0.75, 0.9),
            "estimated_annual_credits": int(annual_reduction * 0.88),
            "estimated_annual_revenue": int(gs_value * 7),
            "development_period_months": random.randint(14, 20),
            "development_cost": int(annual_reduction * random.uniform(4, 10)),
            "roi": round(gs_value * 7 / (annual_reduction * 7) * 100, 1),
            "pros": ["溢价高", "可持续发展认证", "品牌价值"],
            "cons": ["审核严格", "周期较长"]
        })
    
    # I-REC适合可再生能源项目
    if project_type == "renewable_energy":
        irec_credits = annual_reduction / 0.5  # 假设0.5tCO2e/MWh
        irec_value = irec_credits * random.uniform(8, 25)  # 元/MWh
        recommendations.append({
            "type": "I-REC",
            "name": "国际可再生能源证书",
            "suitability_score": random.uniform(0.85, 0.95),
            "estimated_annual_credits": int(irec_credits),
            "estimated_annual_revenue": int(irec_value),
            "development_period_months": random.randint(6, 12),
            "development_cost": int(irec_credits * random.uniform(0.5, 1.5)),
            "roi": round(irec_value / (irec_credits * 1) * 100, 1),
            "pros": ["开发周期短", "成本低", "国际认可"],
            "cons": ["价格相对低", "仅限可再生能源"]
        })
    
    # 按适合度排序
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    return {
        "project_data": project_data,
        "recommendations": recommendations,
        "summary": {
            "best_option": recommendations[0]["type"] if recommendations else None,
            "total_estimated_revenue": sum(r["estimated_annual_revenue"] for r in recommendations[:2]),
            "total_estimated_credits": sum(r["estimated_annual_credits"] for r in recommendations[:2])
        },
        "assessment_time": datetime.now().isoformat()
    }


@router.get("/project/stages")
async def get_development_stages():
    """获取碳资产开发流程阶段"""
    return {
        "stages": DEVELOPMENT_STAGES,
        "total_duration_days": sum(s["duration_days"] for s in DEVELOPMENT_STAGES),
        "total_success_rate": round(math.prod([s["success_rate"] for s in DEVELOPMENT_STAGES]) * 100, 1)
    }


@router.get("/portfolio")
async def get_carbon_asset_portfolio():
    """获取企业碳资产组合（模拟数据）"""
    # 模拟企业持有的碳资产
    assets = [
        {
            "id": "ASSET001",
            "type": "CCER",
            "project_name": "安徽光伏发电项目",
            "total_credits": 15000,
            "remaining_credits": 12500,
            "vintage_year": 2024,
            "issue_date": "2024-03-15",
            "expiry_date": "2027-03-14",
            "purchase_price": 35.5,
            "current_value": 12500 * 45,  # 当前价格
            "status": "active"
        },
        {
            "id": "ASSET002",
            "type": "I-REC",
            "project_name": "浙江风电项目",
            "total_credits": 8500,
            "remaining_credits": 8500,
            "vintage_year": 2025,
            "issue_date": "2025-01-20",
            "expiry_date": "2026-01-19",
            "purchase_price": 12.0,
            "current_value": 8500 * 18,
            "status": "active"
        },
        {
            "id": "ASSET003",
            "type": "VCS",
            "project_name": "云南林业碳汇",
            "total_credits": 20000,
            "remaining_credits": 18000,
            "vintage_year": 2023,
            "issue_date": "2023-08-10",
            "expiry_date": "2028-08-09",
            "purchase_price": 8.5,  # USD
            "current_value": 18000 * 12 * 7,  # USD转人民币
            "status": "active"
        }
    ]
    
    total_value = sum(a["current_value"] for a in assets)
    total_credits = sum(a["remaining_credits"] for a in assets)
    
    return {
        "portfolio": assets,
        "summary": {
            "total_assets": len(assets),
            "total_credits": total_credits,
            "total_value": total_value,
            "avg_price_per_credit": round(total_value / total_credits, 2) if total_credits > 0 else 0,
            "breakdown_by_type": {
                "CCER": sum(a["remaining_credits"] for a in assets if a["type"] == "CCER"),
                "VCS": sum(a["remaining_credits"] for a in assets if a["type"] == "VCS"),
                "I-REC": sum(a["remaining_credits"] for a in assets if a["type"] == "I-REC")
            }
        },
        "update_time": datetime.now().isoformat()
    }


@router.post("/trade/simulate")
async def simulate_carbon_trade(trade_data: Dict[str, Any]):
    """
    模拟碳信用交易
    
    输入参数：
    - trade_type: buy/sell
    - credit_type: CCER/VCS/GS/I-REC
    - volume: 数量
    """
    trade_type = trade_data.get("trade_type", "buy")
    credit_type = trade_data.get("credit_type", "CCER")
    volume = trade_data.get("volume", 1000)
    
    if credit_type.upper() not in CARBON_CREDIT_TYPES:
        raise HTTPException(status_code=404, detail="不支持的碳信用类型")
    
    credit_config = CARBON_CREDIT_TYPES[credit_type.upper()]
    price_range = credit_config["typical_price_range"]
    current_price = (price_range[0] + price_range[1]) / 2 * (1 + random.uniform(-0.1, 0.1))
    
    # 模拟交易
    total_amount = volume * current_price
    service_fee = total_amount * 0.03  # 3%手续费
    
    return {
        "trade_type": trade_type,
        "credit_type": credit_type.upper(),
        "volume": volume,
        "price_per_credit": round(current_price, 2),
        "total_amount": round(total_amount, 2),
        "service_fee": round(service_fee, 2),
        "final_amount": round(total_amount + service_fee if trade_type == "buy" else total_amount - service_fee, 2),
        "estimated_settlement_days": random.randint(3, 7),
        "platforms": ["上海环境能源交易所", "北京绿色交易所", "深圳排放权交易所"],
        "simulation_time": datetime.now().isoformat()
    }
