"""
AI碳枢算 V2.0 - 供应链碳图谱API
对标阳光电源iCarbon - 供应链多层级碳管理
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

router = APIRouter()


@router.get("/network")
async def get_supply_chain_network():
    """获取供应链网络图数据（用于3D力导向图）"""
    nodes = [
        # Tier 1: 核心企业
        {"id": "core", "name": "我司（AI碳枢算）", "tier": 1, "emissions": 1250.8, "carbon_intensity": 1.25, "risk_level": "low", "x": 0, "y": 0, "z": 0},
        # Tier 2: 一级供应商
        {"id": "s1", "name": "鑫达钢材集团", "tier": 2, "emissions": 320.5, "carbon_intensity": 2.10, "risk_level": "high", "x": -60, "y": 0, "z": 30},
        {"id": "s2", "name": "华润塑料科技", "tier": 2, "emissions": 180.3, "carbon_intensity": 1.85, "risk_level": "medium", "x": 60, "y": 0, "z": 30},
        {"id": "s3", "name": "中兴电子元件", "tier": 2, "emissions": 245.7, "carbon_intensity": 1.42, "risk_level": "low", "x": -60, "y": 0, "z": -30},
        {"id": "s4", "name": "顺丰冷链物流", "tier": 2, "emissions": 148.2, "carbon_intensity": 0.95, "risk_level": "medium", "x": 60, "y": 0, "z": -30},
        # Tier 3: 二级供应商
        {"id": "s5", "name": "鞍山铁矿", "tier": 3, "emissions": 580.0, "carbon_intensity": 3.20, "risk_level": "critical", "x": -90, "y": 0, "z": 60},
        {"id": "s6", "name": "中石化原料", "tier": 3, "emissions": 420.3, "carbon_intensity": 2.80, "risk_level": "high", "x": 90, "y": 0, "z": 60},
        {"id": "s7", "name": "台积电芯片", "tier": 3, "emissions": 380.5, "carbon_intensity": 1.65, "risk_level": "medium", "x": -90, "y": 0, "z": -60},
        {"id": "s8", "name": "比亚迪电池", "tier": 3, "emissions": 265.4, "carbon_intensity": 1.30, "risk_level": "low", "x": 90, "y": 0, "z": -60},
    ]
    links = [
        {"source": "s1", "target": "core", "carbon_transfer": 320.5, "material_type": "钢材"},
        {"source": "s2", "target": "core", "carbon_transfer": 180.3, "material_type": "塑料"},
        {"source": "s3", "target": "core", "carbon_transfer": 245.7, "material_type": "电子元件"},
        {"source": "s4", "target": "core", "carbon_transfer": 148.2, "material_type": "物流服务"},
        {"source": "s5", "target": "s1", "carbon_transfer": 580.0, "material_type": "铁矿石"},
        {"source": "s6", "target": "s2", "carbon_transfer": 420.3, "material_type": "石化原料"},
        {"source": "s7", "target": "s3", "carbon_transfer": 380.5, "material_type": "芯片"},
        {"source": "s8", "target": "s3", "carbon_transfer": 265.4, "material_type": "电池"},
    ]
    return {
        "nodes": nodes,
        "links": links,
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "avg_carbon_intensity": round(sum(n["carbon_intensity"] for n in nodes) / len(nodes), 2),
            "high_risk_suppliers": sum(1 for n in nodes if n["risk_level"] in ["high", "critical"]),
        },
        "update_time": datetime.now().isoformat(),
    }


@router.get("/suppliers")
async def get_suppliers(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    """供应商列表（分页）"""
    all_suppliers = [
        {"id": "s1", "name": "鑫达钢材集团", "tier": 2, "emissions": 320.5, "carbon_intensity": 2.10, "risk": "high", "certified": True},
        {"id": "s2", "name": "华润塑料科技", "tier": 2, "emissions": 180.3, "carbon_intensity": 1.85, "risk": "medium", "certified": True},
        {"id": "s3", "name": "中兴电子元件", "tier": 2, "emissions": 245.7, "carbon_intensity": 1.42, "risk": "low", "certified": False},
        {"id": "s4", "name": "顺丰冷链物流", "tier": 2, "emissions": 148.2, "carbon_intensity": 0.95, "risk": "medium", "certified": True},
        {"id": "s5", "name": "鞍山铁矿", "tier": 3, "emissions": 580.0, "carbon_intensity": 3.20, "risk": "critical", "certified": False},
        {"id": "s6", "name": "中石化原料", "tier": 3, "emissions": 420.3, "carbon_intensity": 2.80, "risk": "high", "certified": True},
        {"id": "s7", "name": "台积电芯片", "tier": 3, "emissions": 380.5, "carbon_intensity": 1.65, "risk": "medium", "certified": True},
        {"id": "s8", "name": "比亚迪电池", "tier": 3, "emissions": 265.4, "carbon_intensity": 1.30, "risk": "low", "certified": True},
    ]
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "data": all_suppliers[start:end],
        "total": len(all_suppliers),
        "page": page,
        "page_size": page_size,
    }


@router.get("/supplier/{supplier_id}/detail")
async def get_supplier_detail(supplier_id: str):
    """单个供应商详情"""
    return {
        "id": supplier_id,
        "name": {"s1": "鑫达钢材集团", "s2": "华润塑料科技"}.get(supplier_id, "未知供应商"),
        "tier": 2,
        "emissions": 320.5,
        "carbon_intensity": 2.10,
        "risk_level": "high",
        "certified": False,
        "trend_12m": [round(random.uniform(200, 400), 1) for _ in range(12)],
        "reduction_suggestions": [
            {"step": "更换低碳钢材供应商", "from": "s1", "to": "s5", "potential_reduction": 120.5, "cost": 50000, "difficulty": "medium"},
            {"step": "优化运输路线", "from": "s1", "to": "core", "potential_reduction": 35.2, "cost": 10000, "difficulty": "easy"},
        ],
    }


@router.get("/reduction-paths")
async def get_reduction_paths():
    """碳减排推荐路径"""
    return {
        "paths": [
            {"step": 1, "from": "s5", "to": "s1", "action": "要求鞍山铁矿提供低碳铁矿石", "potential_reduction": 180.5, "cost": 200000, "difficulty": "hard", "priority": 1},
            {"step": 2, "from": "s1", "to": "core", "action": "优化钢材切割工艺减少废料", "potential_reduction": 45.2, "cost": 50000, "difficulty": "medium", "priority": 2},
            {"step": 3, "from": "s4", "to": "core", "action": "切换新能源物流车辆", "potential_reduction": 58.3, "cost": 80000, "difficulty": "medium", "priority": 3},
            {"step": 4, "from": "s2", "to": "core", "action": "使用再生塑料替代原生塑料", "potential_reduction": 72.1, "cost": 60000, "difficulty": "easy", "priority": 4},
        ],
        "total_potential_reduction": 356.1,
        "total_cost": 390000,
        "payback_period_months": 18,
    }
