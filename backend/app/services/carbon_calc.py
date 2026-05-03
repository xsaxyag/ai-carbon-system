"""
碳排放计算服务
基于国家发改委及GB/T 32150标准
优先从数据库读取排放因子，回退到硬编码
"""
from app.models.schemas import CarbonScope, EmissionSource
from app.database import get_db_connection
from typing import Optional

# 碳排放因子数据库（单位：kgCO2/单位）
# 数据来源：GB/T 32150-2015、IPCC 2019
EMISSION_FACTORS = {
    # 范围1：直接排放
    EmissionSource.NATURAL_GAS: {
        "m3": 2.09,    # 天然气 m3 -> kgCO2
        "GJ": 56.84,   # 天然气 GJ -> kgCO2
    },
    EmissionSource.COAL: {
        "kg": 2.52,    # 煤炭 kg -> kgCO2
        "t": 2512,     # 煤炭 吨 -> kgCO2
    },
    EmissionSource.GASOLINE: {
        "L": 2.30,     # 汽油 L -> kgCO2
        "kg": 3.10,    # 汽油 kg -> kgCO2
    },
    EmissionSource.DIESEL: {
        "L": 2.63,     # 柴油 L -> kgCO2
        "kg": 2.98,    # 柴油 kg -> kgCO2
    },
    # 范围2：外购电力
    EmissionSource.ELECTRICITY: {
        "kWh": 0.581,  # 华北电网排放因子 0.581 kgCO2/kWh (2022年更新)
    },
    # Scope3：其他间接排放（简化估算）
    EmissionSource.RENEWABLE: {
        "kWh": 0,      # 可再生能源(绿电)视为零排放
        "t": 0,
    },
    # Scope3: 商务差旅排放因子（来源：GHG Protocol / IPCC）
    # 短途航班 < 3h (km -> kgCO2e)
    EmissionSource.BUSINESS_FLIGHT_SHORT: {
        "km": 0.255,   # 短途航班排放因子
    },
    # 中途航班 3-6h
    EmissionSource.BUSINESS_FLIGHT_MEDIUM: {
        "km": 0.156,   # 中途航班排放因子
    },
    # 长途航班 > 6h
    EmissionSource.BUSINESS_FLIGHT_LONG: {
        "km": 0.195,   # 长途航班排放因子（含辐射效应）
    },
    # 火车（电力机车）
    EmissionSource.BUSINESS_TRAIN: {
        "km": 0.041,   # 电力火车
    },
    # 公务汽车
    EmissionSource.BUSINESS_CAR: {
        "km": 0.171,   # 汽油车平均
        "L": 2.30,     # 汽油
    },
    # Scope3: 废物处理排放因子
    EmissionSource.WASTE_LANDFILL: {
        "kg": 0.45,    # 填埋 CH4逸散系数
        "t": 450,      # 吨
    },
    EmissionSource.WASTE_INCINERATION: {
        "kg": 0.38,    # 焚烧 CO2排放
        "t": 380,
    },
    EmissionSource.WASTE_COMPOSTING: {
        "kg": 0.02,    # 堆肥（甲烷排放少）
        "t": 20,
    },
    # Scope3: 采购商品（估算均值）
    EmissionSource.PURCHASED_OFFICE: {
        "CNY": 0.0028, # 万元（按采购额×排放系数）
        "¥": 0.0028,
    },
    EmissionSource.PURCHASED_EQUIPMENT: {
        "CNY": 0.0055, # 万元
        "¥": 0.0055,
    },
}

# 额外电力排放因子（按地区）—— 数据库不可用时的回退
REGIONAL_ELECTRICITY_FACTORS = {
    "华北": 0.581,   # 北京、天津、河北、山西、内蒙古
    "东北": 0.680,   # 辽宁、吉林、黑龙江
    "华东": 0.581,   # 上海、江苏、浙江、安徽、福建、山东
    "华中": 0.525,   # 河南、湖北、湖南、江西
    "南方": 0.475,   # 广东、广西、海南、重庆、四川、贵州、云南
    "西北": 0.625,   # 陕西、甘肃、青海、宁夏、新疆
    "默认": 0.581,
}


def get_factor_from_db(emission_source: str, unit: str, region: str = '全国', year: int = None) -> Optional[float]:
    """从数据库获取排放因子"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT factor FROM emission_factors WHERE emission_source = ? AND unit = ? AND is_active = 1"
        params = [emission_source, unit]
        if region and region != '全国':
            # 先查地区，没有再查全国
            cursor.execute(query + " AND region = ? ORDER BY year DESC LIMIT 1", params + [region])
            row = cursor.fetchone()
            if row:
                conn.close()
                return row[0]
        if year:
            cursor.execute(query + " AND region = '全国' AND year = ? LIMIT 1", params + [year])
        else:
            cursor.execute(query + " AND region = '全国' ORDER BY year DESC LIMIT 1", params)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def get_all_factors_from_db(emission_source: str) -> dict:
    """从数据库获取某排放源的所有单位-因子对"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT unit, factor FROM emission_factors WHERE emission_source = ? AND is_active = 1 AND region = '全国' ORDER BY year DESC",
            (emission_source,)
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return {row[0]: row[1] for row in rows}
    except Exception:
        pass
    return {}

def get_electricity_factor(region: str = "默认") -> float:
    """获取地区电力排放因子"""
    return REGIONAL_ELECTRICITY_FACTORS.get(region, REGIONAL_ELECTRICITY_FACTORS["默认"])

def calculate_co2_emission(
    scope: CarbonScope,
    emission_source: EmissionSource,
    quantity: float,
    unit: str,
    region: str = '全国'
) -> dict:
    """
    计算碳排放量（优先从数据库读取排放因子）
    
    Args:
        scope: 碳排放范围（scope1/scope2/scope3）
        emission_source: 排放源类型
        quantity: 消耗量
        unit: 单位
        region: 地区（用于电力排放因子）
    
    Returns:
        dict: {
            "co2_emission": float,    # 碳排放量 (kgCO2)
            "emission_factor": float, # 排放因子
            "unit": str               # 单位
        }
    """
    key = emission_source.value if isinstance(emission_source, EmissionSource) else emission_source
    
    # 优先从数据库获取排放因子
    factor = get_factor_from_db(key, unit, region)
    if factor is None:
        # 回退到硬编码
        factors = EMISSION_FACTORS.get(key, {})
        factor = factors.get(unit)
        if factor is None:
            for u, f in factors.items():
                if unit.lower().startswith(u.lower().strip()):
                    factor = f
                    break
            if factor is None:
                factor = list(factors.values())[0] if factors else 0
    
    # scope3供应链排放系数调整
    if scope == CarbonScope.SCOPE3 and factor > 0:
        factor = round(factor * 1.2, 4)
    
    co2_emission = quantity * factor
    
    return {
        "co2_emission": round(co2_emission, 4),
        "emission_factor": factor,
        "unit": "kgCO2"
    }

def calculate_scope2_electricity(
    electricity_kwh: float,
    region: str = "默认"
) -> dict:
    """
    计算外购电力碳排放（范围2）
    
    Args:
        electricity_kwh: 用电量 (kWh)
        region: 地区
    
    Returns:
        dict: 碳排放计算结果
    """
    factor = get_electricity_factor(region)
    co2_emission = electricity_kwh * factor
    
    return {
        "co2_emission": round(co2_emission, 4),
        "emission_factor": factor,
        "unit": "kgCO2"
    }

def calculate_total_emission(records: list) -> dict:
    """
    计算企业碳排放总量
    
    Args:
        records: 碳排放记录列表
    
    Returns:
        dict: {
            "scope1_total": float,
            "scope2_total": float,
            "scope3_total": float,
            "total": float
        }
    """
    scope1_total = 0.0
    scope2_total = 0.0
    scope3_total = 0.0
    
    for record in records:
        scope = record.get("scope")
        co2 = record.get("co2_emission", 0)
        
        if scope == "scope1":
            scope1_total += co2
        elif scope == "scope2":
            scope2_total += co2
        elif scope == "scope3":
            scope3_total += co2
    
    return {
        "scope1_total": round(scope1_total, 4),
        "scope2_total": round(scope2_total, 4),
        "scope3_total": round(scope3_total, 4),
        "total": round(scope1_total + scope2_total + scope3_total, 4)
    }

def get_unit_options(source: EmissionSource) -> list:
    """获取排放源可选单位"""
    key = source.value if isinstance(source, EmissionSource) else source
    factors = EMISSION_FACTORS.get(key, {})
    return list(factors.keys())
