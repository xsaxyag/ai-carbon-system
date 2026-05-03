"""
AI碳枢算 - 数据校验服务
异常值检测、环比/同比校验、scope-source匹配、单位合法性校验
"""
from app.database import get_db_connection
from typing import Optional
import statistics


# ========== scope-source 合法映射 ==========

SCOPE_SOURCE_MAP = {
    "scope1": {
        "natural_gas", "coal", "gasoline", "diesel",
    },
    "scope2": {
        "electricity",
    },
    "scope3": {
        "renewable",
        "business_flight_short", "business_flight_medium", "business_flight_long",
        "business_train", "business_car",
        "waste_landfill", "waste_incineration", "waste_composting",
        "purchased_office", "purchased_equipment",
    },
}

# 每种排放源的合法单位
SOURCE_UNITS = {
    "natural_gas": {"m3", "GJ"},
    "coal": {"kg", "t"},
    "gasoline": {"L", "kg"},
    "diesel": {"L", "kg"},
    "electricity": {"kWh", "MWh"},
    "renewable": {"kWh", "MWh"},
    "business_flight_short": {"km", "人次km"},
    "business_flight_medium": {"km", "人次km"},
    "business_flight_long": {"km", "人次km"},
    "business_train": {"km", "人次km"},
    "business_car": {"km", "L"},
    "waste_landfill": {"kg", "t"},
    "waste_incineration": {"kg", "t"},
    "waste_composting": {"kg", "t"},
    "purchased_office": {"CNY"},
    "purchased_equipment": {"CNY"},
}

# 每种排放源的合理消耗量范围（经验值，超出视为可疑）
QUANTITY_RANGES = {
    "natural_gas":        (1, 1_000_000),       # m3/月
    "coal":               (1, 100_000),          # kg/月
    "gasoline":           (1, 100_000),          # L/月
    "diesel":             (1, 100_000),          # L/月
    "electricity":        (1, 10_000_000),       # kWh/月
    "renewable":          (1, 10_000_000),       # kWh/月
    "business_flight_short": (1, 50_000),        # km/月
    "business_flight_medium": (1, 100_000),      # km/月
    "business_flight_long":   (1, 200_000),      # km/月
    "business_train":     (1, 200_000),          # km/月
    "business_car":       (1, 50_000),           # km/月
    "waste_landfill":     (1, 1_000_000),        # kg/月
    "waste_incineration": (1, 500_000),          # kg/月
    "waste_composting":   (1, 100_000),          # kg/月
    "purchased_office":   (1, 10_000_000),       # CNY/月
    "purchased_equipment":(1, 50_000_000),       # CNY/月
}

# 单位自动转换映射
UNIT_CONVERSIONS = {
    # MWh → kWh
    ("electricity", "MWh"): ("kWh", 1000),
    ("renewable", "MWh"): ("kWh", 1000),
    # t → kg
    ("coal", "t"): ("kg", 1000),
    ("waste_landfill", "t"): ("kg", 1000),
    ("waste_incineration", "t"): ("kg", 1000),
    ("waste_composting", "t"): ("kg", 1000),
}


class ValidationService:
    """数据校验服务"""

    # 校验级别
    LEVEL_ERROR = "error"       # 必须修复
    LEVEL_WARNING = "warning"   # 强烈建议修复
    LEVEL_INFO = "info"         # 提示信息

    @staticmethod
    def validate_scope_source(scope: str, emission_source: str) -> dict:
        """校验 scope 和 emission_source 的匹配关系"""
        allowed = SCOPE_SOURCE_MAP.get(scope, set())
        if emission_source not in allowed:
            correct_scope = None
            for s, sources in SCOPE_SOURCE_MAP.items():
                if emission_source in sources:
                    correct_scope = s
                    break
            return {
                "valid": False,
                "level": ValidationService.LEVEL_ERROR,
                "code": "SCOPE_SOURCE_MISMATCH",
                "message": f"排放源 '{emission_source}' 不属于范围 '{scope}'",
                "suggestion": f"该排放源应归类为 '{correct_scope}'" if correct_scope else "请检查排放源类型",
                "correct_scope": correct_scope,
            }
        return {"valid": True}

    @staticmethod
    def validate_unit(emission_source: str, unit: str) -> dict:
        """校验单位合法性"""
        allowed = SOURCE_UNITS.get(emission_source, set())
        if not allowed:
            return {"valid": True, "note": "无预定义单位约束"}

        if unit in allowed:
            return {"valid": True}

        # 检查是否有自动转换
        conv = UNIT_CONVERSIONS.get((emission_source, unit))
        if conv:
            target_unit, factor = conv
            return {
                "valid": True,
                "auto_convert": True,
                "convert_to": target_unit,
                "convert_factor": factor,
                "message": f"单位 '{unit}' 将自动转换为 '{target_unit}'（×{factor}）",
            }

        return {
            "valid": False,
            "level": ValidationService.LEVEL_WARNING,
            "code": "INVALID_UNIT",
            "message": f"排放源 '{emission_source}' 不支持单位 '{unit}'",
            "suggestion": f"可选单位：{', '.join(allowed)}",
            "allowed_units": list(allowed),
        }

    @staticmethod
    def validate_quantity(emission_source: str, quantity: float) -> dict:
        """校验消耗量是否在合理范围内"""
        rng = QUANTITY_RANGES.get(emission_source)
        if not rng:
            return {"valid": True, "note": "无预定义范围约束"}

        lo, hi = rng
        if quantity <= 0:
            return {
                "valid": False,
                "level": ValidationService.LEVEL_ERROR,
                "code": "NEGATIVE_QUANTITY",
                "message": "消耗量必须大于0",
            }

        if quantity < lo:
            return {
                "valid": True,
                "level": ValidationService.LEVEL_INFO,
                "code": "QUANTITY_TOO_LOW",
                "message": f"消耗量 {quantity} 低于常见范围下限 {lo}，请确认是否正确",
            }

        if quantity > hi:
            return {
                "valid": True,
                "level": ValidationService.LEVEL_WARNING,
                "code": "QUANTITY_TOO_HIGH",
                "message": f"消耗量 {quantity} 超出常见范围上限 {hi}，请确认是否正确",
                "suggestion": "如果数据正确，可忽略此警告；如果错误请修正后重新录入",
            }

        return {"valid": True}

    @staticmethod
    def validate_mom(company_id: int, emission_source: str, record_date: str, quantity: float) -> dict:
        """环比校验：与上月同排放源数据比较"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 计算上月日期
        year, month = record_date.split("-")
        prev_month = int(month) - 1
        prev_year = int(year)
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        prev_date = f"{prev_year:04d}-{prev_month:02d}"

        cursor.execute(
            "SELECT quantity, co2_emission FROM carbon_records "
            "WHERE company_id = ? AND emission_source = ? AND record_date = ?",
            (company_id, emission_source, prev_date),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"valid": True, "note": "无上月数据，跳过环比校验"}

        prev_qty = sum(r["quantity"] for r in rows)
        prev_co2 = sum(r["co2_emission"] for r in rows)

        if prev_qty == 0:
            return {"valid": True, "note": "上月消耗量为0，跳过环比"}

        change_ratio = (quantity - prev_qty) / prev_qty

        if abs(change_ratio) > 2.0:
            level = ValidationService.LEVEL_ERROR
            msg = f"环比变化 {change_ratio:+.1%}，波动超过200%，数据极可能异常"
        elif abs(change_ratio) > 1.0:
            level = ValidationService.LEVEL_WARNING
            msg = f"环比变化 {change_ratio:+.1%}，波动超过100%，请确认"
        elif abs(change_ratio) > 0.5:
            level = ValidationService.LEVEL_INFO
            msg = f"环比变化 {change_ratio:+.1%}，波动较大，请留意"
        else:
            return {"valid": True, "change_ratio": round(change_ratio, 4)}

        return {
            "valid": True,
            "level": level,
            "code": "MOM_ANOMALY",
            "message": msg,
            "change_ratio": round(change_ratio, 4),
            "prev_quantity": prev_qty,
            "prev_co2": prev_co2,
            "prev_date": prev_date,
        }

    @staticmethod
    def validate_yoy(company_id: int, emission_source: str, record_date: str, quantity: float) -> dict:
        """同比校验：与去年同月数据比较"""
        conn = get_db_connection()
        cursor = conn.cursor()

        year, month = record_date.split("-")
        prev_date = f"{int(year) - 1:04d}-{month}"

        cursor.execute(
            "SELECT quantity, co2_emission FROM carbon_records "
            "WHERE company_id = ? AND emission_source = ? AND record_date = ?",
            (company_id, emission_source, prev_date),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"valid": True, "note": "无去年同期数据，跳过同比校验"}

        prev_qty = sum(r["quantity"] for r in rows)
        if prev_qty == 0:
            return {"valid": True, "note": "去年同期消耗量为0"}

        change_ratio = (quantity - prev_qty) / prev_qty

        if abs(change_ratio) > 1.0:
            return {
                "valid": True,
                "level": ValidationService.LEVEL_WARNING,
                "code": "YOY_ANOMALY",
                "message": f"同比变化 {change_ratio:+.1%}，与去年同期差异显著",
                "change_ratio": round(change_ratio, 4),
                "prev_quantity": prev_qty,
                "prev_date": prev_date,
            }

        return {"valid": True, "change_ratio": round(change_ratio, 4)}

    @staticmethod
    def validate_duplicate(company_id: int, emission_source: str, record_date: str, quantity: float, unit: str) -> dict:
        """重复数据校验：检测完全相同的记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, quantity, unit, co2_emission FROM carbon_records "
            "WHERE company_id = ? AND emission_source = ? AND record_date = ? AND quantity = ? AND unit = ?",
            (company_id, emission_source, record_date, quantity, unit),
        )
        rows = cursor.fetchall()
        conn.close()

        if rows:
            return {
                "valid": True,
                "level": ValidationService.LEVEL_WARNING,
                "code": "DUPLICATE_RECORD",
                "message": f"发现 {len(rows)} 条完全相同的记录（同企业/同排放源/同月/同数量/同单位）",
                "duplicate_ids": [r["id"] for r in rows],
                "suggestion": "请确认是否为重复录入",
            }

        return {"valid": True}

    @classmethod
    def full_validate(cls, company_id: int, scope: str, emission_source: str,
                      quantity: float, unit: str, record_date: str) -> dict:
        """
        全量校验入口
        
        Returns:
            {
                "passed": bool,         # 是否通过（无error级别问题）
                "errors": list,         # error级别问题
                "warnings": list,       # warning级别问题
                "infos": list,          # info级别问题
                "auto_converts": list,  # 自动转换建议
                "all_checks": list,     # 全部校验结果
            }
        """
        checks = []

        # 1. scope-source 匹配
        r = cls.validate_scope_source(scope, emission_source)
        if not r["valid"]:
            checks.append(r)

        # 2. 单位合法性
        r = cls.validate_unit(emission_source, unit)
        if not r.get("valid", True):
            checks.append(r)
        elif r.get("auto_convert"):
            checks.append(r)

        # 3. 消耗量范围
        r = cls.validate_quantity(emission_source, quantity)
        if r.get("level"):
            checks.append(r)

        # 4. 环比校验
        r = cls.validate_mom(company_id, emission_source, record_date, quantity)
        if r.get("level"):
            checks.append(r)

        # 5. 同比校验
        r = cls.validate_yoy(company_id, emission_source, record_date, quantity)
        if r.get("level"):
            checks.append(r)

        # 6. 重复校验
        r = cls.validate_duplicate(company_id, emission_source, record_date, quantity, unit)
        if r.get("level"):
            checks.append(r)

        errors = [c for c in checks if c.get("level") == cls.LEVEL_ERROR]
        warnings = [c for c in checks if c.get("level") == cls.LEVEL_WARNING]
        infos = [c for c in checks if c.get("level") == cls.LEVEL_INFO]
        auto_converts = [c for c in checks if c.get("auto_convert")]

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "auto_converts": auto_converts,
            "all_checks": checks,
        }
