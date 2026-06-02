"""
AI碳枢算 V2.0 - 碳足迹3D追踪API
对标阳光电源iCarbon - 产品LCA建模+碳足迹分析
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

router = APIRouter()


@router.get("/lca-chain/{product_id}")
async def get_lca_chain(product_id: str):
    """获取产品LCA全链条数据（用于3D碳足迹追踪）"""
    chain_nodes = [
        {"id": "raw_1", "name": "原材料采购", "stage": "raw_material", "emissions": 45.2, "percentage": 22.3, "cumulative": 45.2, "status": "normal", "detail": "钢材/塑料/电子元件"},
        {"id": "raw_2", "name": "原材料运输", "stage": "transport", "emissions": 28.7, "percentage": 14.2, "cumulative": 73.9, "status": "normal", "detail": "平均运距820km"},
        {"id": "prod_1", "name": "零部件加工", "stage": "production", "emissions": 38.4, "percentage": 19.0, "cumulative": 112.3, "status": "warning", "detail": "机加工车间A区"},
        {"id": "prod_2", "name": "产品组装", "stage": "production", "emissions": 25.1, "percentage": 12.4, "cumulative": 137.4, "status": "normal", "detail": "组装线B"},
        {"id": "prod_3", "name": "质检包装", "stage": "production", "emissions": 12.6, "percentage": 6.2, "cumulative": 150.0, "status": "normal", "detail": "包装材料碳排放"},
        {"id": "trans_1", "name": "成品运输", "stage": "transport", "emissions": 18.3, "percentage": 9.1, "cumulative": 168.3, "status": "warning", "detail": "全国分销网络"},
        {"id": "use_1", "name": "产品使用", "stage": "use", "emissions": 8.5, "percentage": 4.2, "cumulative": 176.8, "status": "normal", "detail": "预计使用寿命5年"},
        {"id": "disp_1", "name": "报废回收", "stage": "disposal", "emissions": 6.2, "percentage": 3.1, "cumulative": 183.0, "status": "normal", "detail": "回收率78%"},
    ]
    flow_links = [
        {"from": "raw_1", "to": "raw_2", "value": 45.2},
        {"from": "raw_2", "to": "prod_1", "value": 73.9},
        {"from": "prod_1", "to": "prod_2", "value": 112.3},
        {"from": "prod_2", "to": "prod_3", "value": 137.4},
        {"from": "prod_3", "to": "trans_1", "value": 150.0},
        {"from": "trans_1", "to": "use_1", "value": 168.3},
        {"from": "use_1", "to": "disp_1", "value": 176.8},
    ]
    waterfall_data = [
        {"name": "原材料", "value": 45.2},
        {"name": "原料运输", "value": 28.7},
        {"name": "零部件加工", "value": 38.4},
        {"name": "产品组装", "value": 25.1},
        {"name": "质检包装", "value": 12.6},
        {"name": "成品运输", "value": 18.3},
        {"name": "产品使用", "value": 8.5},
        {"name": "报废回收", "value": 6.2},
    ]
    return {
        "product_id": product_id,
        "product_name": "智能碳核算终端 v2.0",
        "total_footprint": 183.0,
        "unit": "kgCO2e",
        "chain_nodes": chain_nodes,
        "flow_links": flow_links,
        "waterfall_data": waterfall_data,
        "benchmark": {"industry_avg": 210.5, "best_practice": 155.0, "rank_percentile": 72},
        "update_time": datetime.now().isoformat(),
    }


@router.post("/lca-calculate")
async def calculate_lca(body: Dict[str, Any]):
    """计算产品碳足迹LCA"""
    material = body.get("material", {})
    weight = body.get("weight", 1.0)
    transport_dist = body.get("transport_distance", 100)
    
    raw_emission = material.get("carbon_factor", 2.5) * weight
    transport_emission = transport_dist * 0.00018 * weight
    production_emission = weight * 12.8
    use_emission = weight * 1.2
    disposal_emission = weight * 0.8
    total = raw_emission + transport_emission + production_emission + use_emission + disposal_emission
    
    return {
        "product_name": body.get("product_name", "未命名产品"),
        "weight_kg": weight,
        "total_footprint": round(total, 2),
        "unit": "kgCO2e",
        "breakdown": {
            "raw_material": round(raw_emission, 2),
            "transport": round(transport_emission, 2),
            "production": round(production_emission, 2),
            "use_phase": round(use_emission, 2),
            "disposal": round(disposal_emission, 2),
        },
        "benchmark": {"industry_avg": round(total * 1.15, 2), "rank": "优于行业平均"},
    }
