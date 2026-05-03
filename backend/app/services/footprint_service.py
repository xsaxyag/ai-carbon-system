"""
AI碳枢算 - 碳足迹追踪服务
产品碳足迹计算、生命周期评估(LCA)、碳足迹追踪链
"""
import sqlite3
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "carbon.db"

# 产品生命周期阶段
LIFE_CYCLE_STAGES = {
    "raw_material": "原材料获取",
    "production": "生产制造",
    "transport": "运输配送",
    "use": "使用阶段",
    "disposal": "废弃处理"
}

# 默认排放因子（单位：kgCO2/unit）
DEFAULT_PRODUCT_FACTORS = {
    "raw_material": {
        "steel_kg": 2.50, "aluminum_kg": 11.50, "plastic_kg": 3.10,
        "glass_kg": 0.85, "paper_kg": 1.20, "textile_kg": 5.80,
        "circuit_board_kg": 15.00, "battery_kg": 8.50
    },
    "production": {
        "electricity_kwh": 0.581, "natural_gas_m3": 2.09,
        "water_ton": 0.30, "steam_ton": 120.0
    },
    "transport": {
        "truck_ton_km": 0.12, "train_ton_km": 0.041,
        "ship_ton_km": 0.008, "air_ton_km": 0.602
    },
    "use": {
        "electricity_kwh_year": 0.581, "gasoline_l_year": 2.30,
        "diesel_l_year": 2.63
    },
    "disposal": {
        "landfill_kg": 0.45, "recycle_kg": -0.80,
        "incineration_kg": 0.38
    }
}


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_product_footprint(company_id: int, product_name: str,
                             product_code: Optional[str] = None,
                             category: Optional[str] = None,
                             functional_unit: str = "件",
                             lifespan_years: float = 1.0,
                             description: Optional[str] = None) -> dict:
    """创建产品碳足迹记录"""
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO product_footprints 
        (company_id, product_name, product_code, category, functional_unit,
         lifespan_years, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
    """, (company_id, product_name, product_code, category, functional_unit,
          lifespan_years, description, now, now))
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": product_id, "product_name": product_name, "status": "draft"}


def add_footprint_stage(product_id: int, stage: str, material_name: str,
                        quantity: float, unit: str, emission_factor: Optional[float] = None,
                        source: Optional[str] = None, notes: Optional[str] = None) -> dict:
    """添加生命周期阶段排放数据"""
    if stage not in LIFE_CYCLE_STAGES:
        raise ValueError(f"无效阶段: {stage}，可选: {list(LIFE_CYCLE_STAGES.keys())}")

    # 如果未提供排放因子，尝试从默认因子获取
    if emission_factor is None:
        emission_factor = _get_default_factor(stage, unit)
        source = "内置默认因子"
    else:
        source = source or "用户自定义"

    emission = round(quantity * emission_factor, 4)
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO footprint_stages
        (product_id, stage, material_name, quantity, unit, emission_factor, 
         emission, source, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, stage, material_name, quantity, unit, emission_factor,
          emission, source, notes, now))
    stage_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": stage_id,
        "stage": stage,
        "stage_name": LIFE_CYCLE_STAGES[stage],
        "material_name": material_name,
        "quantity": quantity,
        "unit": unit,
        "emission_factor": emission_factor,
        "emission_kgco2": emission
    }


def calculate_product_footprint(product_id: int) -> dict:
    """计算产品碳足迹汇总"""
    conn = _get_conn()
    cursor = conn.cursor()

    # 获取产品信息
    cursor.execute("SELECT * FROM product_footprints WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        raise ValueError(f"产品不存在: {product_id}")

    # 获取各阶段数据
    cursor.execute("SELECT * FROM footprint_stages WHERE product_id = ?", (product_id,))
    stages = cursor.fetchall()

    # 按阶段汇总
    stage_summary = {}
    total_emission = 0.0

    for stage in stages:
        stage_key = stage["stage"]
        if stage_key not in stage_summary:
            stage_summary[stage_key] = {
                "name": LIFE_CYCLE_STAGES.get(stage_key, stage_key),
                "emission": 0.0,
                "items": []
            }
        emission = stage["emission"]
        stage_summary[stage_key]["emission"] += emission
        stage_summary[stage_key]["items"].append({
            "material_name": stage["material_name"],
            "quantity": stage["quantity"],
            "unit": stage["unit"],
            "emission": emission
        })
        total_emission += emission

    total_emission = round(total_emission, 4)

    # 更新产品总排放和状态
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE product_footprints 
        SET total_emission = ?, status = 'calculated', updated_at = ?
        WHERE id = ?
    """, (total_emission, now, product_id))
    conn.commit()
    conn.close()

    # 计算各阶段占比
    stage_percentages = {}
    for key, val in stage_summary.items():
        val["emission"] = round(val["emission"], 4)
        stage_percentages[key] = round(val["emission"] / total_emission * 100, 1) if total_emission > 0 else 0

    return {
        "product_id": product_id,
        "product_name": product["product_name"],
        "functional_unit": product["functional_unit"],
        "lifespan_years": product["lifespan_years"],
        "total_emission_kgco2": total_emission,
        "stage_summary": stage_summary,
        "stage_percentages": stage_percentages,
        "item_count": len(stages)
    }


def list_product_footprints(company_id: Optional[int] = None) -> list:
    """列出产品碳足迹"""
    conn = _get_conn()
    cursor = conn.cursor()
    if company_id:
        cursor.execute("SELECT * FROM product_footprints WHERE company_id = ? ORDER BY created_at DESC", (company_id,))
    else:
        cursor.execute("SELECT * FROM product_footprints ORDER BY created_at DESC")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products


def get_product_footprint_detail(product_id: int) -> dict:
    """获取产品碳足迹详情"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product_footprints WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        raise ValueError(f"产品不存在: {product_id}")

    cursor.execute("SELECT * FROM footprint_stages WHERE product_id = ? ORDER BY stage, id", (product_id,))
    stages = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"product": dict(product), "stages": stages}


def delete_product_footprint(product_id: int) -> bool:
    """删除产品碳足迹及所有阶段数据"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM footprint_stages WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM product_footprints WHERE id = ?", (product_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def compare_products(product_ids: List[int]) -> dict:
    """产品碳足迹对比"""
    results = []
    for pid in product_ids:
        try:
            result = calculate_product_footprint(pid)
            results.append(result)
        except ValueError:
            continue

    return {
        "products": results,
        "comparison": {
            "lowest": min(results, key=lambda x: x["total_emission_kgco2"]) if results else None,
            "highest": max(results, key=lambda x: x["total_emission_kgco2"]) if results else None,
            "average": round(sum(r["total_emission_kgco2"] for r in results) / len(results), 4) if results else 0
        }
    }


def _get_default_factor(stage: str, unit: str) -> float:
    """获取默认排放因子"""
    factor_key = unit.lower().replace("/", "_per_")
    # 直接匹配
    stage_factors = DEFAULT_PRODUCT_FACTORS.get(stage, {})
    for key, val in stage_factors.items():
        if key == factor_key or key.endswith(f"_{factor_key}"):
            return val
    # 单位后缀匹配
    for key, val in stage_factors.items():
        if key.endswith(unit.lower()):
            return val
    return 0.0  # 未知因子默认0
