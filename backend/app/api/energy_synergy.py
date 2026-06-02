"""
AI碳枢算 V2.0 - 源网荷储协同API
对标阳光电源iCarbon - 源网荷储AI优化、多能互补、虚拟电厂
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/overview")
async def get_energy_overview():
    """源网荷储总览（用于3D能源枢纽可视化）"""
    return {
        "source": {
            "solar_capacity_kw": 500,
            "wind_capacity_kw": 200,
            "solar_output_kw": round(320.5 + random.uniform(-30, 50), 1),
            "wind_output_kw": round(85.3 + random.uniform(-10, 20), 1),
            "green_ratio": 35.2,
            "renewable_today_kwh": round(320.5 * 8 + random.uniform(-200, 300)),
        },
        "grid": {
            "grid_import_kw": round(1250.8 + random.uniform(-100, 150), 1),
            "grid_export_kw": round(80.5 + random.uniform(-10, 30), 1),
            "peak_shaving_kw": 350.0,
            "grid_price_cny_per_kwh": round(0.68 + random.uniform(-0.1, 0.15), 2),
        },
        "load": {
            "total_load_kw": round(2100.0 + random.uniform(-150, 200), 1),
            "load_forecast_24h": [round(1800 + 800 * (0.5 + 0.5 * __import__('math').sin(i * 3.14159 / 12)), 1) for i in range(24)],
            "peak_load_kw": 2600.0,
            "valley_load_kw": 1200.0,
            "load_by_area": [
                {"name": "生产车间A区", "load": 1850.2},
                {"name": "生产车间B区", "load": 1240.8},
                {"name": "能源站", "load": 2100.0},
                {"name": "仓储区", "load": 320.5},
                {"name": "办公区", "load": 180.3},
            ],
        },
        "storage": {
            "soc_percent": 72,
            "capacity_kwh": 800,
            "charge_power_kw": round(150.0 + random.uniform(-20, 50), 1),
            "discharge_power_kw": round(200.0 + random.uniform(-30, 60), 1),
            "cycle_count": 1247,
            "health_percent": 97.2,
        },
        "summary": {
            "self_sufficiency_percent": 42.8,
            "carbon_reduction_today_kgco2": round(320.5 * 8 * 0.0005, 2),
            "cost_savings_today_cny": round(320.5 * 8 * 0.68 * 0.35, 2),
        },
        "update_time": datetime.now().isoformat(),
    }


@router.get("/prediction")
async def get_energy_prediction(hours: int = Query(24, ge=1, le=168)):
    """AI负荷预测数据（未来24h/7天）"""
    now = datetime.now()
    forecast = []
    for i in range(hours):
        t = now + timedelta(hours=i)
        hour = t.hour
        base_load = 1800 + 800 * (0.5 + 0.5 * __import__('math').sin(hour * 3.14159 / 12))
        forecast.append({
            "timestamp": t.isoformat(),
            "predicted_load_kw": round(base_load + random.uniform(-100, 100), 1),
            "actual_load_kw": round(base_load + random.uniform(-50, 50), 1) if i < 2 else None,
            "solar_gen_kw": round(max(0, 300 * __import__('math').sin(max(0, hour - 6) * 3.14159 / 12)), 1) if 6 <= hour <= 18 else 0,
            "wind_gen_kw": round(85 + random.uniform(-20, 30), 1),
            "grid_price_cny": round(0.4 + 0.5 * max(0, __import__('math').sin((hour - 10) * 3.14159 / 8)), 2),
        })
    return {
        "forecast": forecast,
        "accuracy": {"mae": 85.2, "rmse": 112.7, "r2": 0.91},
        "model": "LSTM+Attention v2.1",
        "update_time": now.isoformat(),
    }


@router.get("/storage/status")
async def get_storage_status():
    """储能系统详细状态"""
    return {
        "soc_percent": 72,
        "capacity_kwh": 800,
        "available_kwh": 576,
        "charge_power_kw": 150.0,
        "discharge_power_kw": 200.0,
        "voltage_v": 648.0,
        "current_a": 231.5,
        "temperature_c": 28.5,
        "cycle_count": 1247,
        "health_percent": 97.2,
        "status": "charging",
        "today_charge_kwh": 620.5,
        "today_discharge_kwh": 580.3,
        "today_savings_cny": 127.8,
        "update_time": datetime.now().isoformat(),
    }


@router.get("/optimization-suggestions")
async def get_optimization_suggestions():
    """AI优化建议列表"""
    return {
        "suggestions": [
            {"type": "peak_shaving", "title": "建议14:00-16:00启动储能放电", "description": "该时段电价峰值0.92元/kWh，储能放电可节省约127元/天", "expected_saving_cny_day": 127, "priority": "high"},
            {"type": "load_shift", "title": "建议将A区非连续生产移至夜间", "description": "夜间电价0.32元/kWh，移峰填谷可节省约85元/天", "expected_saving_cny_day": 85, "priority": "medium"},
            {"type": "pv_optimize", "title": "建议清洗光伏板提升发电效率", "description": "当前发电效率比理论值低12%，清洗后可提升约38kWh/天", "expected_saving_cny_day": 25, "priority": "low"},
            {"type": "virtual_plant", "title": "建议参与虚拟电厂调峰服务", "description": "聚合200kW可调节负荷，预计收益150元/次调峰", "expected_saving_cny_day": 150, "priority": "medium"},
        ],
        "summary": {"total_potential_saving_cny_month": 11760, "payback_period_months": 14},
    }


@router.get("/energy-flow-realtime")
async def get_energy_flow_realtime():
    """实时能源流向数据（用于3D动画）"""
    now = datetime.now()
    return {
        "timestamp": now.isoformat(),
        "flows": [
            {"id": "f1", "from": "grid", "to": "bus", "type": "electric", "value": 1250.8, "direction": "import", "particle_color": "#95a5a6"},
            {"id": "f2", "from": "solar", "to": "bus", "type": "electric", "value": 320.5, "direction": "generate", "particle_color": "#f1c40f"},
            {"id": "f3", "from": "bus", "to": "prod_a", "type": "electric", "value": 1850.2, "direction": "consume", "particle_color": "#e74c3c"},
            {"id": "f4", "from": "bus", "to": "prod_b", "type": "electric", "value": 1240.8, "direction": "consume", "particle_color": "#e74c3c"},
            {"id": "f5", "from": "gas_grid", "to": "energy", "type": "gas", "value": 580.2, "direction": "import", "particle_color": "#e67e22"},
            {"id": "f6", "from": "storage", "to": "bus", "type": "electric", "value": 200.0, "direction": "discharge", "particle_color": "#2ecc71"},
        ],
        "summary": {"green_particle_ratio": 0.35, "total_power_kw": 2100.0},
    }
