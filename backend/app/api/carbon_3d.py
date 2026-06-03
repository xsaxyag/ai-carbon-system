"""
AI碳枢算 V2.0 - 3D碳全景大屏数据API
对标阳光电源iCarbon能碳平台 - 碳全景一屏总览
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/dashboard")
async def get_3d_dashboard():
    """3D碳全景大屏 - 全局数据"""
    # 月度趋势：模拟减排效果，排放量逐月下降约2%
    monthly_trend = []
    now = datetime.now()
    base_emission = 120.0  # 基准排放量（tCO2e/月）

    for i in range(12):
        month = (now - timedelta(days=30*i)).strftime("%Y-%m")
        # 逐月下降：最近月份排放更低
        month_factor = 1.0 - (11 - i) * 0.02  # 从第1个月到第12个月，下降约24%
        monthly_trend.append({
            "month": month,
            "scope1": round(base_emission * 0.45 * month_factor * random.uniform(0.98, 1.02), 2),
            "scope2": round(base_emission * 0.38 * month_factor * random.uniform(0.98, 1.02), 2),
            "scope3": round(base_emission * 0.17 * month_factor * random.uniform(0.98, 1.02), 2),
        })
    monthly_trend.reverse()

    regional_data = [
        {"id": "zone_a", "name": "生产车间A区", "emissions": 320.5, "level": "high", "trend": "up"},
        {"id": "zone_b", "name": "生产车间B区", "emissions": 215.3, "level": "medium", "trend": "down"},
        {"id": "zone_c", "name": "仓储物流区", "emissions": 128.7, "level": "low", "trend": "stable"},
        {"id": "zone_d", "name": "办公区", "emissions": 45.2, "level": "low", "trend": "down"},
        {"id": "zone_e", "name": "能源站", "emissions": 280.1, "level": "high", "trend": "up"},
        {"id": "zone_f", "name": "废水处理站", "emissions": 95.8, "level": "medium", "trend": "stable"},
    ]

    top_emissions = [
        {"name": "天然气锅炉", "value": 320.5, "percentage": 25.6, "zone": "能源站"},
        {"name": "电力购入", "value": 280.1, "percentage": 22.4, "zone": "全厂"},
        {"name": "柴油叉车", "value": 195.7, "percentage": 15.6, "zone": "仓储物流区"},
        {"name": "原料运输", "value": 148.3, "percentage": 11.8, "zone": "供应链"},
        {"name": "废水处理", "value": 95.8, "percentage": 7.7, "zone": "废水处理站"},
    ]

    alerts = [
        {"level": "critical", "message": "能源站天然气消耗异常，今日排放超标42%", "time": "10分钟前"},
        {"level": "warning", "message": "生产车间A区电力负荷持续偏高", "time": "1小时前"},
        {"level": "info", "message": "仓储区光伏系统运行正常，今日发电320kWh", "time": "2小时前"},
    ]

    return {
        "total_emissions": 1250.8,
        "reduction_rate": 12.5,
        "green_power_ratio": 35.2,
        "carbon_asset_value": 185000,
        "monthly_trend": monthly_trend,
        "scope_distribution": {"scope1": 45.2, "scope2": 38.7, "scope3": 16.1},
        "regional_data": regional_data,
        "top_emissions": top_emissions,
        "alerts": alerts,
        "update_time": datetime.now().isoformat(),
    }


@router.get("/scope-distribution")
async def get_scope_distribution():
    """Scope1/2/3详细分布（用于3D饼图）"""
    return {
        "scope1": {
            "total": 565.2, "percentage": 45.2,
            "categories": [
                {"name": "天然气燃烧", "value": 320.5, "percentage": 56.7},
                {"name": "柴油消耗", "value": 148.3, "percentage": 26.2},
                {"name": "制冷剂泄漏", "value": 65.4, "percentage": 11.6},
                {"name": "其他", "value": 31.0, "percentage": 5.5},
            ],
        },
        "scope2": {
            "total": 483.7, "percentage": 38.7,
            "categories": [
                {"name": "外购电力", "value": 380.2, "percentage": 78.6},
                {"name": "外购热力", "value": 103.5, "percentage": 21.4},
            ],
        },
        "scope3": {
            "total": 201.9, "percentage": 16.1,
            "categories": [
                {"name": "原料运输", "value": 95.8, "percentage": 47.4},
                {"name": "废弃物处理", "value": 48.2, "percentage": 23.9},
                {"name": "商务差旅", "value": 35.6, "percentage": 17.6},
                {"name": "采购商品", "value": 22.3, "percentage": 11.1},
            ],
        }
    }


@router.get("/realtime-emissions")
async def get_realtime_emissions():
    """实时排放数据流（用于3D场景实时更新）"""
    now = datetime.now()
    hour = now.hour

    # 根据时间段调整排放强度
    if 8 <= hour <= 18:  # 工作时间，排放较高
        co2_base = random.uniform(1.5, 2.5)
        power_base = random.uniform(120, 180)
    elif 19 <= hour <= 22:  # 晚间，排放中等
        co2_base = random.uniform(1.0, 2.0)
        power_base = random.uniform(80, 140)
    else:  # 深夜，排放较低
        co2_base = random.uniform(0.5, 1.2)
        power_base = random.uniform(40, 80)

    zone_names = ["生产车间A区", "生产车间B区", "仓储物流区", "办公区", "能源站", "废水处理站"]
    # 各区域排放强度系数（能源站最高，办公区最低）
    zone_factors = [1.2, 0.9, 0.5, 0.2, 1.5, 0.4]
    readings = []
    for i, zname in enumerate(zone_names):
        factor = zone_factors[i]
        co2_rate = round(co2_base * factor * random.uniform(0.9, 1.1), 2)
        readings.append({
            "zone_id": f"zone_{chr(97+i)}",
            "zone_name": zname,
            "co2_rate": co2_rate,
            "power": round(power_base * factor * random.uniform(0.9, 1.1), 1),
            "gas": round(50 * factor * random.uniform(0.9, 1.1), 1),
            "status": "normal" if co2_rate < 2.0 else ("warning" if co2_rate < 2.5 else "critical"),
            "timestamp": now.isoformat(),
        })
    return {
        "readings": readings,
        "total_co2_rate": round(sum(r["co2_rate"] for r in readings), 2),
        "timestamp": now.isoformat(),
    }


@router.get("/heatmap-data")
async def get_heatmap_data():
    """热力图数据网格（用于3D热力效果）"""
    grid_size = 20
    heatmap = []
    for x in range(grid_size):
        for y in range(grid_size):
            dist = ((x - grid_size/2)**2 + (y - grid_size/2)**2)**0.5
            base = max(0, 100 - dist * 5) + random.uniform(-10, 10)
            heatmap.append({
                "x": x, "y": y,
                "value": round(max(0, base), 2),
                "zone": "zone_e" if base > 60 else ("zone_a" if base > 30 else "zone_c"),
            })
    return {
        "grid_size": grid_size, "data": heatmap,
        "max_value": max(p["value"] for p in heatmap),
        "min_value": min(p["value"] for p in heatmap),
    }
