"""
AI碳枢算 - 碳数据管理API (SQLite版)
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from app.models.schemas import (
    CarbonRecord, CarbonRecordCreate, CarbonSummary,
    CarbonScope, EmissionSource, CarbonCalculateRequest, CarbonCalculateResponse
)
from app.services import carbon_calc
from app.database import get_db_connection, init_db

# 初始化数据库
init_db()

router = APIRouter()

# ========== 企业管理 ==========

@router.post("/company/")
async def create_company(company: dict):
    """创建企业 - 支持前端字段映射"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 前端字段映射：size -> region, employees -> employee_count
    name = company.get("name")
    industry = company.get("industry", "未知")
    region = company.get("region") or company.get("size", "默认")  # 优先用region，否则用size
    employee_count = company.get("employee_count") or company.get("employees")
    
    cursor.execute("""
        INSERT INTO companies (name, industry, region, employee_count)
        VALUES (?, ?, ?, ?)
    """, (name, industry, region, employee_count))
    
    company_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "企业创建成功",
        "data": {
            "id": company_id,
            "name": name,
            "industry": industry,
            "region": region,
            "employee_count": employee_count,
            "status": "active"
        }
    }

@router.get("/company/", response_model=List[dict])
async def list_companies(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """获取企业列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM companies"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.get("/company/{company_id}/", response_model=dict)
async def get_company(company_id: int):
    """获取企业详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="企业不存在")
    return dict(row)

@router.put("/company/{company_id}/", response_model=dict)
async def update_company(company_id: int, company: dict):
    """更新企业"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key in ["name", "industry", "region", "employee_count", "status"]:
        if key in company:
            fields.append(f"{key} = ?")
            values.append(company[key])
    
    if not fields:
        raise HTTPException(status_code=400, detail="无更新字段")
    
    values.append(company_id)
    query = f"UPDATE companies SET {', '.join(fields)} WHERE id = ?"
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    return await get_company(company_id)

@router.delete("/company/{company_id}/")
async def delete_company(company_id: int):
    """删除企业"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": company_id}

# ========== 碳数据管理 ==========

@router.post("/records/")
async def create_carbon_record(record: CarbonRecordCreate, skip_validation: bool = False):
    """创建碳排放记录（自动校验+计算）"""
    from app.services.validation_service import ValidationService

    # 自动校验
    validation = ValidationService.full_validate(
        company_id=record.company_id,
        scope=record.scope.value if isinstance(record.scope, CarbonScope) else record.scope,
        emission_source=record.emission_source.value if isinstance(record.emission_source, EmissionSource) else record.emission_source,
        quantity=record.quantity,
        unit=record.unit,
        record_date=record.record_date,
    )

    # 如果有error级别问题且未跳过校验，拒绝创建
    if not skip_validation and not validation["passed"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "数据校验未通过",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            }
        )

    # 单位自动转换
    actual_quantity = record.quantity
    actual_unit = record.unit
    for conv in validation.get("auto_converts", []):
        actual_quantity = actual_quantity * conv["convert_factor"]
        actual_unit = conv["convert_to"]

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 计算碳排放量
    result = carbon_calc.calculate_co2_emission(
        scope=record.scope,
        emission_source=record.emission_source,
        quantity=actual_quantity,
        unit=actual_unit
    )
    
    cursor.execute("""
        INSERT INTO carbon_records 
        (company_id, record_date, scope, emission_source, quantity, unit, co2_emission, emission_factor, region, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.company_id,
        record.record_date,
        record.scope,
        record.emission_source,
        record.quantity,
        record.unit,
        result["co2_emission"],
        result["emission_factor"],
        record.region if hasattr(record, 'region') else "默认",
        record.notes if hasattr(record, 'notes') else None
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "碳排放记录已保存",
        "data": {
            "id": record_id,
            **record.model_dump(),
            "co2_emission": result["co2_emission"],
            "emission_factor": result["emission_factor"],
            "actual_quantity": actual_quantity,
            "actual_unit": actual_unit,
            "status": "created",
            "validation": {
                "passed": validation["passed"],
                "warnings_count": len(validation["warnings"]),
                "warnings": validation["warnings"],
                "infos": validation["infos"],
            }
        }
    }

@router.get("/records/", response_model=List[dict])
async def list_carbon_records(company_id: int = None, skip: int = 0, limit: int = 100):
    """获取碳排放记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM carbon_records"
    params = []
    if company_id:
        query += " WHERE company_id = ?"
        params.append(company_id)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.get("/records/{record_id}/", response_model=dict)
async def get_carbon_record(record_id: int):
    """获取记录详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carbon_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    return dict(row)

@router.delete("/records/{record_id}/")
async def delete_carbon_record(record_id: int):
    """删除记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carbon_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": record_id}

# ========== 碳排放计算 ==========

@router.post("/calculate/", response_model=CarbonCalculateResponse)
async def calculate_carbon(request: CarbonCalculateRequest):
    """计算碳排放量"""
    result = carbon_calc.calculate_co2_emission(
        scope=request.scope,
        emission_source=request.emission_source,
        quantity=request.quantity,
        unit=request.unit
    )
    return CarbonCalculateResponse(**result)

@router.get("/summary/{company_id}/", response_model=CarbonSummary)
async def get_carbon_summary(company_id: int):
    """获取企业碳排放汇总"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查企业是否存在
    cursor.execute("SELECT id FROM companies WHERE id = ?", (company_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="企业不存在")
    
    # 获取该企业的所有记录
    cursor.execute("""
        SELECT scope, co2_emission 
        FROM carbon_records 
        WHERE company_id = ?
    """, (company_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return CarbonSummary(company_id=company_id)
    
    scope1_total = sum(r["co2_emission"] for r in rows if r["scope"] == "scope1")
    scope2_total = sum(r["co2_emission"] for r in rows if r["scope"] == "scope2")
    scope3_total = sum(r["co2_emission"] for r in rows if r["scope"] == "scope3")
    
    return CarbonSummary(
        company_id=company_id,
        total_scope1=round(scope1_total, 4),
        total_scope2=round(scope2_total, 4),
        total_scope3=round(scope3_total, 4),
        total_emission=round(scope1_total + scope2_total + scope3_total, 4),
        record_count=len(rows)
    )

@router.get("/factors/")
async def get_emission_factors(source: Optional[str] = None, region: Optional[str] = None):
    """获取碳排放因子（从数据库读取）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM emission_factors WHERE is_active = 1"
        params = []
        if source:
            query += " AND emission_source = ?"
            params.append(source)
        if region:
            query += " AND region = ?"
            params.append(region)
        query += " ORDER BY emission_source, unit, year DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return [dict(r) for r in rows]
    except Exception:
        pass
    # 回退到硬编码
    return carbon_calc.EMISSION_FACTORS