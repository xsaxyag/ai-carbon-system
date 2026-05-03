"""
企业管理API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# 模拟数据库
companies_db = []

@router.post("/", response_model=dict)
async def create_company(company: dict):
    """创建企业"""
    company_id = len(companies_db) + 1
    company_data = {
        "id": company_id,
        **company,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    companies_db.append(company_data)
    return company_data

@router.get("/", response_model=List[dict])
async def list_companies(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
):
    """获取企业列表"""
    companies = companies_db
    if status:
        companies = [c for c in companies if c.get("status") == status]
    return companies[skip:skip+limit]

@router.get("/{company_id}", response_model=dict)
async def get_company(company_id: int):
    """获取企业详情"""
    for c in companies_db:
        if c["id"] == company_id:
            return c
    raise HTTPException(status_code=404, detail="企业不存在")

@router.put("/{company_id}", response_model=dict)
async def update_company(company_id: int, company: dict):
    """更新企业信息"""
    for i, c in enumerate(companies_db):
        if c["id"] == company_id:
            companies_db[i] = {
                **c,
                **company,
                "updated_at": datetime.now().isoformat()
            }
            return companies_db[i]
    raise HTTPException(status_code=404, detail="企业不存在")

@router.delete("/{company_id}")
async def delete_company(company_id: int):
    """删除企业"""
    global companies_db
    companies_db = [c for c in companies_db if c["id"] != company_id]
    return {"status": "deleted", "id": company_id}