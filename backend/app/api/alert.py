"""
碳排放预警API
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from app.services.alert_service import AlertService

router = APIRouter()


class ThresholdUpdate(BaseModel):
    """阈值更新"""
    monthly_total: Optional[float] = Field(None, gt=0, description="月度总排放阈值(kgCO2)")
    scope1_ratio: Optional[float] = Field(None, gt=0, le=1, description="范围1占比上限")
    scope2_ratio: Optional[float] = Field(None, gt=0, le=1, description="范围2占比上限")
    mom_increase: Optional[float] = Field(None, gt=0, le=5, description="环比增长上限")
    yoy_increase: Optional[float] = Field(None, gt=0, le=5, description="同比增长上限")


@router.get("/check/{company_id}/")
async def check_alerts(company_id: int):
    """检查企业碳排放预警"""
    # 获取企业自定义阈值
    custom_thresholds = AlertService.get_company_thresholds(company_id)
    result = AlertService.check_alerts(company_id, custom_thresholds)
    # 保存预警历史
    AlertService.save_alerts(company_id, result)
    return result


@router.get("/thresholds/{company_id}/")
async def get_thresholds(company_id: int):
    """获取企业预警阈值"""
    return AlertService.get_company_thresholds(company_id)


@router.put("/thresholds/{company_id}/")
async def update_thresholds(company_id: int, thresholds: ThresholdUpdate):
    """更新企业预警阈值"""
    update_data = {k: v for k, v in thresholds.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="无更新字段")
    return AlertService.set_company_thresholds(company_id, update_data)


@router.get("/history/{company_id}/")
async def get_alert_history(company_id: int, limit: int = 30):
    """获取预警历史"""
    return AlertService.get_alert_history(company_id, limit)


@router.get("/default-thresholds/")
async def get_default_thresholds():
    """获取默认预警阈值"""
    return AlertService.DEFAULT_THRESHOLDS
