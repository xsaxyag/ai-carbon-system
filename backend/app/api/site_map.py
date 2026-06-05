"""
园区地图碳排放API
提供建筑级碳排放数据，用于3D园区可视化
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter(prefix="/api/v1/site-map", tags=["园区地图"])

# 碳排放因子库 (kgCO2/kWh)
CARBON_INTENSITY = {
    "production": 0.85,   # 生产车间
    "warehouse": 0.45,    # 仓储
    "office": 0.60,       # 办公
    "lab": 0.75,          # 实验室
    "other": 0.55         # 其他
}

# 能源消耗系数 (kWh/m²)
ENERGY_CONSUMPTION = {
    "production": 280,
    "warehouse": 45,
    "office": 85,
    "lab": 180,
    "other": 60
}


class BuildingData(BaseModel):
    """建筑数据模型"""
    id: int
    name: str
    type: str
    area: float  # 面积 m²
    carbon_emission: float  # 碳排放量 tCO2
    energy_consumption: float  # 能耗 kWh
    carbon_intensity: float  # 碳排放强度 kgCO2/m²
    energy_type: str  # 能源类型
    green_energy_ratio: float  # 绿电比例 %
    reduction_potential: float  # 减排潜力 %
    rank: int  # 碳排放排名
    month: str  # 数据月份
    data_source: str  # 数据来源


class CarbonTrend(BaseModel):
    """碳排放趋势"""
    month: str
    emission: float
    energy: float
    green_ratio: float


class OptimizationSuggestion(BaseModel):
    """优化建议"""
    type: str
    title: str
    description: str
    estimated_reduction: float  # 预计减排量 tCO2
    investment: float  # 投资万元
    roi: float  # 投资回报率


@router.get("/buildings", response_model=dict)
async def get_building_carbon_data(
    company_id: int = 1,
    month: str = None
):
    """
    获取园区建筑碳排放数据
    
    - company_id: 企业ID (默认1)
    - month: 数据月份，格式YYYY-MM (默认当前月份)
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    
    # 模拟企业建筑数据
    buildings = [
        {
            "id": 1,
            "name": "综合生产车间A",
            "type": "production",
            "area": 3500,
            "carbon_emission": 1250.5,
            "energy_consumption": 980000,
            "carbon_intensity": 35.73,
            "energy_type": "电力+天然气",
            "green_energy_ratio": 15.2,
            "reduction_potential": 22.5,
            "rank": 1,
            "month": month,
            "data_source": "能耗监测系统"
        },
        {
            "id": 2,
            "name": "精密制造车间B",
            "type": "production",
            "area": 2800,
            "carbon_emission": 980.3,
            "energy_consumption": 784000,
            "carbon_intensity": 35.01,
            "energy_type": "电力",
            "green_energy_ratio": 8.5,
            "reduction_potential": 28.3,
            "rank": 2,
            "month": month,
            "data_source": "能耗监测系统"
        },
        {
            "id": 3,
            "name": "原材料仓储中心",
            "type": "warehouse",
            "area": 4200,
            "carbon_emission": 189.0,
            "energy_consumption": 189000,
            "carbon_intensity": 4.50,
            "energy_type": "电力",
            "green_energy_ratio": 25.0,
            "reduction_potential": 35.8,
            "rank": 6,
            "month": month,
            "data_source": "电表抄表"
        },
        {
            "id": 4,
            "name": "行政办公楼",
            "type": "office",
            "area": 1600,
            "carbon_emission": 136.0,
            "energy_consumption": 136000,
            "carbon_intensity": 8.50,
            "energy_type": "电力",
            "green_energy_ratio": 45.0,
            "reduction_potential": 18.2,
            "rank": 5,
            "month": month,
            "data_source": "能耗监测系统"
        },
        {
            "id": 5,
            "name": "研发中心",
            "type": "lab",
            "area": 1200,
            "carbon_emission": 216.0,
            "energy_consumption": 216000,
            "carbon_intensity": 18.00,
            "energy_type": "电力+蒸汽",
            "green_energy_ratio": 30.0,
            "reduction_potential": 25.5,
            "rank": 4,
            "month": month,
            "data_source": "能耗监测系统"
        },
        {
            "id": 6,
            "name": "成品仓库",
            "type": "warehouse",
            "area": 3800,
            "carbon_emission": 171.0,
            "energy_consumption": 171000,
            "carbon_intensity": 4.50,
            "energy_type": "电力",
            "green_energy_ratio": 20.0,
            "reduction_potential": 32.1,
            "rank": 7,
            "month": month,
            "data_source": "电表抄表"
        },
        {
            "id": 7,
            "name": "员工宿舍楼",
            "type": "other",
            "area": 2200,
            "carbon_emission": 121.0,
            "energy_consumption": 132000,
            "carbon_intensity": 5.50,
            "energy_type": "电力+燃气",
            "green_energy_ratio": 12.0,
            "reduction_potential": 28.9,
            "rank": 8,
            "month": month,
            "data_source": "能耗监测系统"
        },
        {
            "id": 8,
            "name": "污水处理站",
            "type": "other",
            "area": 450,
            "carbon_emission": 89.5,
            "energy_consumption": 67500,
            "carbon_intensity": 19.89,
            "energy_type": "电力",
            "green_energy_ratio": 0.0,
            "reduction_potential": 45.2,
            "rank": 9,
            "month": month,
            "data_source": "设备监测"
        }
    ]
    
    # 计算总计
    total_emission = sum(b["carbon_emission"] for b in buildings)
    total_energy = sum(b["energy_consumption"] for b in buildings)
    total_area = sum(b["area"] for b in buildings)
    
    return {
        "success": True,
        "company_id": company_id,
        "month": month,
        "total_buildings": len(buildings),
        "total_carbon_emission": round(total_emission, 2),
        "total_energy_consumption": round(total_energy, 2),
        "average_intensity": round(total_emission * 1000 / total_area, 2),
        "buildings": buildings,
        "summary": {
            "high_carbon_buildings": len([b for b in buildings if b["carbon_intensity"] > 20]),
            "medium_carbon_buildings": len([b for b in buildings if 10 <= b["carbon_intensity"] <= 20]),
            "low_carbon_buildings": len([b for b in buildings if b["carbon_intensity"] < 10]),
            "green_energy_coverage": round(
                sum(b["area"] * b["green_energy_ratio"] for b in buildings) / total_area, 1
            )
        }
    }


@router.get("/carbon-trend", response_model=dict)
async def get_carbon_trend(
    company_id: int = 1,
    months: int = 12
):
    """获取碳排放月度趋势"""
    current_month = datetime.now()
    trend = []
    
    for i in range(months - 1, -1, -1):
        # 计算历史月份
        month_date = datetime(
            current_month.year - (current_month.month - 1 - i <= 0 and (i > current_month.month - 1 and 1 or 0) or 0),
            ((current_month.month - 1 - i - 1) % 12) + 1,
            1
        )
        month_str = month_date.strftime("%Y-%m")
        
        # 模拟季节性波动 (冬季高、夏季低)
        month_num = month_date.month
        seasonal_factor = 1 + 0.15 * (1 if month_num in [12, 1, 2] else -0.1 if month_num in [6, 7, 8] else 0)
        trend_factor = 0.95 + (months - i) * 0.005  # 总体下降趋势
        
        base_emission = 3200
        base_energy = 2400000
        base_green = 18
        
        trend.append({
            "month": month_str,
            "emission": round(base_emission * seasonal_factor * trend_factor, 2),
            "energy": round(base_energy * seasonal_factor * trend_factor, 0),
            "green_ratio": round(min(base_green + (months - i) * 0.8, 35), 1)
        })
    
    return {
        "success": True,
        "company_id": company_id,
        "trend": trend,
        "analysis": {
            "yoy_change": round((trend[-1]["emission"] - trend[0]["emission"]) / trend[0]["emission"] * 100, 2),
            "mom_change": round((trend[-1]["emission"] - trend[-2]["emission"]) / trend[-2]["emission"] * 100, 2),
            "green_energy_progress": round(trend[-1]["green_ratio"] - trend[0]["green_ratio"], 1)
        }
    }


@router.get("/optimization-suggestions", response_model=dict)
async def get_optimization_suggestions(
    company_id: int = 1
):
    """获取减排优化建议"""
    suggestions = [
        {
            "type": "屋顶光伏",
            "title": "厂房屋顶分布式光伏建设",
            "description": "在综合生产车间A和精密制造车间B屋顶安装3.5MWp分布式光伏系统",
            "estimated_reduction": 385.5,
            "investment": 280.0,
            "roi": 4.2,
            "priority": 1
        },
        {
            "type": "绿电采购",
            "title": "扩大绿电采购比例至40%",
            "description": "与风电、光伏电站签订绿电采购协议，优先使用可再生能源",
            "estimated_reduction": 520.0,
            "investment": 0,
            "roi": -1,
            "priority": 2
        },
        {
            "type": "空压机节能",
            "title": "空压机系统节能改造",
            "description": "更换高效变频空压机+余热回收系统，降低压缩空气系统能耗20%",
            "estimated_reduction": 156.8,
            "investment": 85.0,
            "roi": 3.1,
            "priority": 3
        },
        {
            "type": "LED照明",
            "title": "全厂LED照明改造",
            "description": "将传统灯具更换为智能LED灯+光照感应控制系统",
            "estimated_reduction": 48.2,
            "investment": 32.0,
            "roi": 3.8,
            "priority": 4
        },
        {
            "type": "能源管理",
            "title": "智慧能源管理系统升级",
            "description": "部署AI驱动的能源管理平台，实现用能设备智能调度",
            "estimated_reduction": 128.5,
            "investment": 95.0,
            "roi": 4.5,
            "priority": 5
        },
        {
            "type": "储能系统",
            "title": "工商业储能系统配置",
            "description": "配置2MWh电化学储能系统，实现峰谷套利和备用电源",
            "estimated_reduction": 95.0,
            "investment": 320.0,
            "roi": 2.8,
            "priority": 6
        }
    ]
    
    total_reduction = sum(s["estimated_reduction"] for s in suggestions)
    
    return {
        "success": True,
        "company_id": company_id,
        "total_potential_reduction": total_reduction,
        "suggestions": suggestions
    }


@router.post("/export-data", response_model=dict)
async def export_site_map_data(
    company_id: int = 1,
    format: str = "json"
):
    """
    导出园区地图碳排放数据
    
    - format: 导出格式 (json/csv/excel)
    """
    # 获取建筑数据
    buildings_data = await get_building_carbon_data(company_id)
    trend_data = await get_carbon_trend(company_id)
    suggestions_data = await get_optimization_suggestions(company_id)
    
    export_data = {
        "export_time": datetime.now().isoformat(),
        "company_id": company_id,
        "buildings": buildings_data,
        "trend": trend_data,
        "optimization": suggestions_data
    }
    
    return {
        "success": True,
        "format": format,
        "data": export_data,
        "message": f"数据已准备好，可导出为{format.upper()}格式"
    }
