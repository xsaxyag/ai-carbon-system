"""
AI碳枢算 - 智能填报向导 API
行业模板/排放源选项/快速估算/企业推荐
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.services.wizard_service import WizardService, REGION_OPTIONS
from app.api.auth import require_auth

router = APIRouter(tags=["智能填报向导"])


@router.get("/industries")
async def list_industries():
    """获取行业列表"""
    result = WizardService.get_industry_list()
    return {"success": True, "data": result}


@router.get("/industries/{industry}")
async def get_industry_profile(industry: str):
    """获取行业填报模板"""
    result = WizardService.get_industry_profile(industry)
    if not result:
        raise HTTPException(status_code=404, detail=f"未找到行业 '{industry}' 的模板")
    return {"success": True, "data": result}


@router.get("/sources")
async def list_all_sources():
    """获取所有排放源完整选项（带scope/单位/典型值/排放因子）"""
    result = WizardService.get_all_sources()
    return {"success": True, "data": result}


@router.get("/regions")
async def list_regions():
    """获取地区选项（电力排放因子按地区不同）"""
    return {"success": True, "data": REGION_OPTIONS}


@router.post("/template")
async def generate_template(
    industry: str = Query(..., description="行业名称"),
    company_id: int = Query(..., description="企业ID"),
    record_date: str = Query(..., description="填报月份 YYYY-MM", regex=r"^\d{4}-(0[1-9]|1[0-2])$"),
    region: str = Query("华东", description="地区"),
    user: dict = Depends(require_auth),
):
    """根据行业生成填报模板（含预估值）"""
    result = WizardService.generate_template(industry, company_id, record_date, region)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}


@router.get("/estimate/{industry}")
async def quick_estimate(
    industry: str,
    region: str = Query("华东", description="地区"),
):
    """快速估算行业典型碳排放量级"""
    result = WizardService.quick_estimate(industry, region)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}


@router.get("/recommend/{company_id}")
async def company_recommendation(
    company_id: int,
    user: dict = Depends(require_auth),
):
    """根据企业已有数据推荐下一步填报项"""
    result = WizardService.get_company_recommendation(company_id)
    return {"success": True, "data": result}
