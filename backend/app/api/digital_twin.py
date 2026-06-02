"""
AI碳枢算 V2.0 - 数字孪生工厂API
对标阳光电源iCarbon - 工厂/园区3D可视化、实时排放
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/factory/zones")
async def get_factory_zones():
    """获取工厂各区域数据（用于3D数字孪生场景）"""
    zones = [
        {"id": "prod_a", "name": "生产车间A区", "type": "production_line", "position": {"x": -30, "y": 0, "z": 20}, "emissions": 320.5, "power_consumption": 1850.2, "status": "operating"},
        {"id": "prod_b", "name": "生产车间B区", "type": "production_line", "position": {"x": 30, "y": 0, "z": 20}, "emissions": 215.3, "power_consumption": 1240.8, "status": "operating"},
        {"id": "warehouse", "name": "仓储物流区", "type": "warehouse", "position": {"x": 0, "y": 0, "z": -40}, "emissions": 128.7, "power_consumption": 320.5, "status": "operating"},
        {"id": "office", "name": "办公区", "type": "office", "position": {"x": -50, "y": 0, "z": -30}, "emissions": 45.2, "power_consumption": 180.3, "status": "operating"},
        {"id": "energy", "name": "能源站", "type": "energy_station", "position": {"x": 40, "y": 0, "z": -20}, "emissions": 280.1, "power_consumption": 2100.0, "status": "alert"},
        {"id": "treatment", "name": "废水处理站", "type": "treatment", "position": {"x": -40, "y": 0, "z": -50}, "emissions": 95.8, "power_consumption": 450.7, "status": "standby"},
    ]
    buildings = [
        {"id": "b_prod_a", "name": "A区厂房", "position": {"x": -30, "y": 0, "z": 20}, "size": {"w": 40, "h": 12, "d": 30}, "color": "#e74c3c", "emission_level": "high"},
        {"id": "b_prod_b", "name": "B区厂房", "position": {"x": 30, "y": 0, "z": 20}, "size": {"w": 35, "h": 10, "d": 25}, "color": "#f39c12", "emission_level": "medium"},
        {"id": "b_warehouse", "name": "智能仓库", "position": {"x": 0, "y": 0, "z": -40}, "size": {"w": 50, "h": 8, "d": 20}, "color": "#2ecc71", "emission_level": "low"},
        {"id": "b_office", "name": "办公楼", "position": {"x": -50, "y": 0, "z": -30}, "size": {"w": 25, "h": 15, "d": 15}, "color": "#2ecc71", "emission_level": "low"},
        {"id": "b_energy", "name": "能源中心", "position": {"x": 40, "y": 0, "z": -20}, "size": {"w": 20, "h": 8, "d": 15}, "color": "#e74c3c", "emission_level": "high"},
        {"id": "b_treatment", "name": "水处理站", "position": {"x": -40, "y": 0, "z": -50}, "size": {"w": 18, "h": 6, "d": 12}, "color": "#f39c12", "emission_level": "medium"},
    ]
    return {"zones": zones, "buildings": buildings, "update_time": datetime.now().isoformat()}


@router.get("/factory/emissions")
async def get_factory_emissions(hours: int = Query(24, ge=1, le=168)):
    """获取工厂实时排放数据（按区域/时间）"""
    now = datetime.now()
    timeline = []
    for i in range(hours):
        t = now - timedelta(hours=i)
        timeline.append({
            "timestamp": t.isoformat(),
            "prod_a": round(320.5 / 24 + random.uniform(-20, 20), 2),
            "prod_b": round(215.3 / 24 + random.uniform(-15, 15), 2),
            "warehouse": round(128.7 / 24 + random.uniform(-8, 8), 2),
            "energy": round(280.1 / 24 + random.uniform(-25, 25), 2),
            "treatment": round(95.8 / 24 + random.uniform(-5, 5), 2),
            "office": round(45.2 / 24 + random.uniform(-3, 3), 2),
        })
    timeline.reverse()
    return {
        "timeline": timeline,
        "summary": {
            "total_24h": round(sum(p["prod_a"] + p["prod_b"] + p["warehouse"] + p["energy"] + p["treatment"] + p["office"] for p in timeline), 2),
            "peak_hour": max(timeline, key=lambda x: sum(x[k] for k in x if k not in ["timestamp"])),
            "alert_zones": ["energy"],
        },
        "update_time": now.isoformat(),
    }


@router.get("/factory/energy-flow")
async def get_energy_flow():
    """获取能源流向数据（用于3D能源流动画）"""
    return {
        "nodes": [
            {"id": "grid", "name": "电网", "type": "source", "value": 2100.0},
            {"id": "solar", "name": "光伏系统", "type": "source", "value": 320.5},
            {"id": "gas_grid", "name": "燃气管网", "type": "source", "value": 580.2},
            {"id": "prod_a", "name": "生产车间A区", "type": "load", "value": 1850.2},
            {"id": "prod_b", "name": "生产车间B区", "type": "load", "value": 1240.8},
            {"id": "warehouse", "name": "仓储物流区", "type": "load", "value": 320.5},
            {"id": "office", "name": "办公区", "type": "load", "value": 180.3},
            {"id": "treatment", "name": "废水处理站", "type": "load", "value": 450.7},
            {"id": "storage", "name": "储能系统", "type": "storage", "value": 800.0, "soc": 72},
        ],
        "links": [
            {"source": "grid", "target": "prod_a", "type": "electric", "value": 1200.0},
            {"source": "grid", "target": "prod_b", "type": "electric", "value": 900.0},
            {"source": "solar", "target": "prod_a", "type": "electric", "value": 320.5},
            {"source": "solar", "target": "storage", "type": "electric", "value": 80.2},
            {"source": "gas_grid", "target": "energy", "type": "gas", "value": 580.2},
            {"source": "energy", "target": "prod_a", "type": "steam", "value": 280.1},
            {"source": "energy", "target": "prod_b", "type": "steam", "value": 180.3},
            {"source": "storage", "target": "prod_a", "type": "electric", "value": 350.0, "direction": "discharge"},
        ],
        "summary": {"green_ratio": 35.2, "self_sufficiency": 42.8},
    }


@router.get("/factory/alerts")
async def get_factory_alerts():
    """工厂级预警信息"""
    return {
        "alerts": [
            {"level": "critical", "zone": "能源站", "message": "天然气消耗异常，今日排放超标42%", "since": "10分钟前", "value": 580.2, "threshold": 400.0},
            {"level": "warning", "zone": "生产车间A区", "message": "电力负荷持续偏高，建议关注", "since": "1小时前", "value": 1850.2, "threshold": 1600.0},
            {"level": "info", "zone": "仓储区", "message": "光伏系统运行正常，今日发电320kWh", "since": "2小时前"},
        ],
        "counts": {"critical": 1, "warning": 1, "info": 1},
    }
