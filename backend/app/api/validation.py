"""
AI碳枢算 - 数据校验API
提供录入前校验、批量校验、校验规则查询
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.validation_service import ValidationService, SCOPE_SOURCE_MAP, SOURCE_UNITS

router = APIRouter()


class ValidateRequest(BaseModel):
    """单条数据校验请求"""
    company_id: int = Field(..., gt=0, description="企业ID")
    scope: str = Field(..., description="碳排放范围 scope1/scope2/scope3")
    emission_source: str = Field(..., description="排放源类型")
    quantity: float = Field(..., gt=0, description="消耗量")
    unit: str = Field(..., min_length=1, description="单位")
    record_date: str = Field(..., pattern=r'^\d{4}-(0[1-9]|1[0-2])$', description="记录月份 YYYY-MM")


class BatchValidateRequest(BaseModel):
    """批量校验请求"""
    records: List[ValidateRequest] = Field(..., min_length=1, max_length=100, description="待校验记录列表")


class QuickCheckRequest(BaseModel):
    """快速校验请求（不查数据库，仅格式校验）"""
    scope: str = Field(..., description="碳排放范围")
    emission_source: str = Field(..., description="排放源类型")
    quantity: float = Field(..., gt=0, description="消耗量")
    unit: str = Field(..., min_length=1, description="单位")


@router.post("/validate/")
async def validate_record(req: ValidateRequest):
    """全量校验单条碳数据记录（含环比/同比/重复检测）"""
    result = ValidationService.full_validate(
        company_id=req.company_id,
        scope=req.scope,
        emission_source=req.emission_source,
        quantity=req.quantity,
        unit=req.unit,
        record_date=req.record_date,
    )
    return {
        "success": True,
        "data": result,
    }


@router.post("/validate/batch/")
async def batch_validate(req: BatchValidateRequest):
    """批量校验多条碳数据记录"""
    results = []
    for i, record in enumerate(req.records):
        result = ValidationService.full_validate(
            company_id=record.company_id,
            scope=record.scope,
            emission_source=record.emission_source,
            quantity=record.quantity,
            unit=record.unit,
            record_date=record.record_date,
        )
        results.append({"index": i, **result})

    total_errors = sum(len(r.get("errors", [])) for r in results)
    total_warnings = sum(len(r.get("warnings", [])) for r in results)

    return {
        "success": True,
        "data": {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": results,
        },
    }


@router.post("/validate/quick/")
async def quick_validate(req: QuickCheckRequest):
    """快速校验（仅格式/范围校验，不查数据库）"""
    checks = []

    # scope-source 匹配
    r = ValidationService.validate_scope_source(req.scope, req.emission_source)
    if not r["valid"]:
        checks.append(r)

    # 单位合法性
    r = ValidationService.validate_unit(req.emission_source, req.unit)
    if not r.get("valid", True) or r.get("auto_convert"):
        checks.append(r)

    # 消耗量范围
    r = ValidationService.validate_quantity(req.emission_source, req.quantity)
    if r.get("level"):
        checks.append(r)

    errors = [c for c in checks if c.get("level") == ValidationService.LEVEL_ERROR]
    warnings = [c for c in checks if c.get("level") == ValidationService.LEVEL_WARNING]
    infos = [c for c in checks if c.get("level") == ValidationService.LEVEL_INFO]

    return {
        "success": True,
        "data": {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "all_checks": checks,
        },
    }


@router.get("/rules/")
async def get_validation_rules():
    """获取校验规则说明（前端展示用）"""
    return {
        "success": True,
        "data": {
            "scope_source_map": {k: list(v) for k, v in SCOPE_SOURCE_MAP.items()},
            "source_units": SOURCE_UNITS,
            "description": {
                "SCOPE_SOURCE_MISMATCH": "排放源与范围不匹配（error级别，必须修正）",
                "INVALID_UNIT": "排放源不支持该单位（warning级别，建议修正）",
                "QUANTITY_TOO_HIGH": "消耗量超出常见范围上限（warning级别，确认后可提交）",
                "QUANTITY_TOO_LOW": "消耗量低于常见范围下限（info级别，提示注意）",
                "MOM_ANOMALY": "环比波动异常（与上月同源数据对比）",
                "YOY_ANOMALY": "同比波动异常（与去年同期数据对比）",
                "DUPLICATE_RECORD": "检测到完全相同的重复记录",
            },
        },
    }


@router.get("/source-options/")
async def get_source_options(scope: Optional[str] = None):
    """获取排放源选项（含合法单位）"""
    if scope:
        sources = SCOPE_SOURCE_MAP.get(scope, set())
        result = {}
        for s in sources:
            result[s] = {
                "units": list(SOURCE_UNITS.get(s, [])),
                "scope": scope,
            }
        return {"success": True, "data": result}

    # 返回全部
    result = {}
    for s, units in SOURCE_UNITS.items():
        # 找到所属scope
        for scope_name, scope_sources in SCOPE_SOURCE_MAP.items():
            if s in scope_sources:
                result[s] = {"units": list(units), "scope": scope_name}
                break
    return {"success": True, "data": result}
