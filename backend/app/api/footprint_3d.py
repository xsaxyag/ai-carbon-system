"""
AI碳枢算 V2.0 - 碳足迹3D追踪API
对标阳光电源iCarbon - 产品LCA建模+碳足迹分析
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

router = APIRouter()

# 产品数据库（模拟多产品支持）
products_db = {
    "prod_001": {
        "name": "智能碳核算终端 v2.0",
        "total_footprint": 183.0,
        "unit": "kgCO2e",
        "chain_nodes": [
            {"id": "raw_1", "name": "原材料采购", "stage": "raw_material", "emissions": 45.2, "percentage": 22.3, "cumulative": 45.2, "status": "normal", "detail": "钢材/塑料/电子元件"},
            {"id": "raw_2", "name": "原材料运输", "stage": "transport", "emissions": 28.7, "percentage": 14.2, "cumulative": 73.9, "status": "normal", "detail": "平均运距820km"},
            {"id": "prod_1", "name": "零部件加工", "stage": "production", "emissions": 38.4, "percentage": 19.0, "cumulative": 112.3, "status": "warning", "detail": "机加工车间A区"},
            {"id": "prod_2", "name": "产品组装", "stage": "production", "emissions": 25.1, "percentage": 12.4, "cumulative": 137.4, "status": "normal", "detail": "组装线B"},
            {"id": "prod_3", "name": "质检包装", "stage": "production", "emissions": 12.6, "percentage": 6.2, "cumulative": 150.0, "status": "normal", "detail": "包装材料碳排放"},
            {"id": "trans_1", "name": "成品运输", "stage": "transport", "emissions": 18.3, "percentage": 9.1, "cumulative": 168.3, "status": "warning", "detail": "全国分销网络"},
            {"id": "use_1", "name": "产品使用", "stage": "use", "emissions": 8.5, "percentage": 4.2, "cumulative": 176.8, "status": "normal", "detail": "预计使用寿命5年"},
            {"id": "disp_1", "name": "报废回收", "stage": "disposal", "emissions": 6.2, "percentage": 3.1, "cumulative": 183.0, "status": "normal", "detail": "回收率78%"},
        ],
        "flow_links": [
            {"from": "raw_1", "to": "raw_2", "value": 45.2},
            {"from": "raw_2", "to": "prod_1", "value": 73.9},
            {"from": "prod_1", "to": "prod_2", "value": 112.3},
            {"from": "prod_2", "to": "prod_3", "value": 137.4},
            {"from": "prod_3", "to": "trans_1", "value": 150.0},
            {"from": "trans_1", "to": "use_1", "value": 168.3},
            {"from": "use_1", "to": "disp_1", "value": 176.8},
        ],
        "waterfall_data": [
            {"name": "原材料", "value": 45.2},
            {"name": "原料运输", "value": 28.7},
            {"name": "零部件加工", "value": 38.4},
            {"name": "产品组装", "value": 25.1},
            {"name": "质检包装", "value": 12.6},
            {"name": "成品运输", "value": 18.3},
            {"name": "产品使用", "value": 8.5},
            {"name": "报废回收", "value": 6.2},
        ],
        "benchmark": {"industry_avg": 210.5, "best_practice": 155.0, "rank_percentile": 72},
    },
    "prod_002": {
        "name": "工业碳排放监测仪",
        "total_footprint": 245.6,
        "unit": "kgCO2e",
        "chain_nodes": [
            {"id": "raw_1", "name": "传感器采购", "stage": "raw_material", "emissions": 68.3, "percentage": 27.8, "cumulative": 68.3, "status": "normal", "detail": "高精度NDIR传感器"},
            {"id": "raw_2", "name": "电子元件运输", "stage": "transport", "emissions": 35.2, "percentage": 14.3, "cumulative": 103.5, "status": "normal", "detail": "平均运距650km"},
            {"id": "prod_1", "name": "PCB组装", "stage": "production", "emissions": 52.1, "percentage": 21.2, "cumulative": 155.6, "status": "warning", "detail": "SMT生产线"},
            {"id": "prod_2", "name": "外壳加工", "stage": "production", "emissions": 28.7, "percentage": 11.7, "cumulative": 184.3, "status": "normal", "detail": "铝合金CNC加工"},
            {"id": "prod_3", "name": "产品校准", "stage": "production", "emissions": 15.3, "percentage": 6.2, "cumulative": 199.6, "status": "normal", "detail": "校准设备能耗"},
            {"id": "trans_1", "name": "成品运输", "stage": "transport", "emissions": 22.5, "percentage": 9.2, "cumulative": 222.1, "status": "normal", "detail": "区域分销"},
            {"id": "use_1", "name": "产品使用", "stage": "use", "emissions": 18.2, "percentage": 7.4, "cumulative": 240.3, "status": "normal", "detail": "预计使用寿命8年"},
            {"id": "disp_1", "name": "报废回收", "stage": "disposal", "emissions": 5.3, "percentage": 2.2, "cumulative": 245.6, "status": "normal", "detail": "电子元件回收率82%"},
        ],
        "flow_links": [
            {"from": "raw_1", "to": "raw_2", "value": 68.3},
            {"from": "raw_2", "to": "prod_1", "value": 103.5},
            {"from": "prod_1", "to": "prod_2", "value": 155.6},
            {"from": "prod_2", "to": "prod_3", "value": 184.3},
            {"from": "prod_3", "to": "trans_1", "value": 199.6},
            {"from": "trans_1", "to": "use_1", "value": 222.1},
            {"from": "use_1", "to": "disp_1", "value": 240.3},
        ],
        "waterfall_data": [
            {"name": "传感器采购", "value": 68.3},
            {"name": "电子元件运输", "value": 35.2},
            {"name": "PCB组装", "value": 52.1},
            {"name": "外壳加工", "value": 28.7},
            {"name": "产品校准", "value": 15.3},
            {"name": "成品运输", "value": 22.5},
            {"name": "产品使用", "value": 18.2},
            {"name": "报废回收", "value": 5.3},
        ],
        "benchmark": {"industry_avg": 280.0, "best_practice": 210.0, "rank_percentile": 68},
    },
}


@router.get("/lca-chain/{product_id}")
async def get_lca_chain(product_id: str):
    """获取产品LCA全链条数据（用于3D碳足迹追踪）"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    product = products_db[product_id]
    
    return {
        "product_id": product_id,
        "product_name": product["name"],
        "total_footprint": product["total_footprint"],
        "unit": product["unit"],
        "chain_nodes": product["chain_nodes"],
        "flow_links": product["flow_links"],
        "waterfall_data": product["waterfall_data"],
        "benchmark": product["benchmark"],
        "update_time": datetime.now().isoformat(),
    }


@router.post("/lca-calculate")
async def calculate_lca(body: Dict[str, Any]):
    """计算产品碳足迹LCA"""
    material = body.get("material", {})
    weight = body.get("weight", 1.0)
    transport_dist = body.get("transport_distance", 100)
    
    # 更精细的排放因子计算
    raw_factor = material.get("carbon_factor", 2.5)
    raw_emission = raw_factor * weight
    
    # 运输排放：公路运输排放因子 0.00018 kgCO2e/(t·km)
    transport_emission = transport_dist * 0.00018 * weight
    
    # 生产排放：根据产品类型调整
    product_type = body.get("product_type", "electronic")
    production_factors = {
        "electronic": 12.8,  # 电子产品
        "mechanical": 18.5,   # 机械产品
        "chemical": 25.2,      # 化工产品
        "textile": 8.7,        # 纺织产品
    }
    production_emission = weight * production_factors.get(product_type, 12.8)
    
    # 使用阶段排放：根据使用寿命计算
    lifespan_years = body.get("lifespan_years", 5)
    annual_usage_emission = weight * 0.8  # 每年使用排放
    use_emission = annual_usage_emission * lifespan_years
    
    # 报废回收排放：根据回收率计算
    recycling_rate = body.get("recycling_rate", 0.78)
    disposal_emission = weight * 0.8 * (1 - recycling_rate)
    
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
