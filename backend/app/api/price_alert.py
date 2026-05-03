"""
碳价实时预警API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.services.price_alert_service import (
    fetch_realtime_price,
    get_all_alerts,
    get_price_history,
    save_price_history,
    check_quota_risk,
    analyze_trend
)

router = APIRouter()

@router.get("/price")
async def get_current_price():
    """获取当前碳价"""
    price = await fetch_realtime_price()
    save_price_history(price)
    return price

@router.get("/price/history")
async def get_price_history_endpoint(days: int = Query(7, ge=1, le=30)):
    """获取碳价历史"""
    history = get_price_history(days)
    return {
        "history": history,
        "count": len(history),
        "days": days
    }

@router.get("/alerts")
async def get_alerts(company_id: Optional[int] = None):
    """获取所有预警（价格预警 + 配额风险）"""
    result = await get_all_alerts(company_id)
    return result

@router.get("/alerts/company/{company_id}")
async def get_company_alerts(company_id: int, year: Optional[int] = None):
    """获取企业专属预警"""
    if not year:
        year = datetime.now().year
    
    # 价格预警
    price = await fetch_realtime_price()
    save_price_history(price)
    
    # 配额风险
    quota_alerts = await check_quota_risk(company_id, year)
    
    # 趋势
    trend = await analyze_trend()
    
    return {
        "company_id": company_id,
        "year": year,
        "current_price": price,
        "quota_alerts": quota_alerts,
        "trend": trend,
        "alert_count": len(quota_alerts),
        "generated_at": datetime.now().isoformat()
    }

@router.get("/trend")
async def get_price_trend():
    """获取碳价趋势分析"""
    trend = await analyze_trend()
    history = get_price_history(7)
    
    return {
        "trend": trend,
        "recent_history": history,
        "generated_at": datetime.now().isoformat()
    }

@router.post("/simulate")
async def simulate_price_change(change_percent: float):
    """模拟碳价变化（用于测试）"""
    from app.services.price_alert_service import _price_cache, generate_mock_price
    
    # 获取当前价格
    current = await fetch_realtime_price()
    
    # 应用变化
    new_price = current["price"] * (1 + change_percent / 100)
    new_price = max(30, min(120, new_price))  # 限制范围
    
    simulated = {
        "market": "CET",
        "price": round(new_price, 2),
        "change": round(new_price - current["price"], 2),
        "change_percent": round(change_percent, 2),
        "volume": current["volume"],
        "source": "模拟数据",
        "update_time": datetime.now().isoformat(),
        "is_real": False,
        "is_simulated": True
    }
    
    save_price_history(simulated)
    
    return {
        "before": current,
        "after": simulated,
        "applied_change_percent": change_percent
    }
