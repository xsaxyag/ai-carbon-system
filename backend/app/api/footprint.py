"""
AI碳枢算 - 碳足迹追踪API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.services.footprint_service import (
    create_product_footprint, add_footprint_stage, calculate_product_footprint,
    list_product_footprints, get_product_footprint_detail, delete_product_footprint,
    compare_products, LIFE_CYCLE_STAGES
)
from app.api.auth import require_auth

router = APIRouter()


class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    product_code: Optional[str] = Field(None, max_length=100, description="产品编号")
    category: Optional[str] = Field(None, max_length=50, description="产品类别")
    functional_unit: str = Field("件", max_length=20, description="功能单位")
    lifespan_years: float = Field(1.0, ge=0, description="生命周期年数")
    description: Optional[str] = Field(None, description="产品描述")

    @field_validator("functional_unit")
    @classmethod
    def validate_unit(cls, v):
        return v or "件"


class StageAdd(BaseModel):
    stage: str = Field(..., description="生命周期阶段")
    material_name: str = Field(..., min_length=1, max_length=100, description="物料名称")
    quantity: float = Field(..., gt=0, description="用量")
    unit: str = Field(..., min_length=1, max_length=20, description="单位")
    emission_factor: Optional[float] = Field(None, ge=0, description="排放因子(kgCO2/unit)")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v):
        valid = list(LIFE_CYCLE_STAGES.keys())
        if v not in valid:
            raise ValueError(f"stage must be one of: {valid}")
        return v


class ProductCompareRequest(BaseModel):
    product_ids: List[int] = Field(..., min_length=2, max_length=10, description="产品ID列表")


# ─── 产品管理 ───────────────────────────────────────────

@router.post("/products", summary="创建产品碳足迹档案")
async def create_product(req: ProductCreate, current_user: dict = Depends(require_auth)):
    """创建新产品碳足迹记录"""
    try:
        result = create_product_footprint(
            company_id=current_user.get("company_id", 1),
            product_name=req.product_name,
            product_code=req.product_code,
            category=req.category,
            functional_unit=req.functional_unit,
            lifespan_years=req.lifespan_years,
            description=req.description
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", summary="产品碳足迹列表")
async def list_products(company_id: Optional[int] = None, current_user: dict = Depends(require_auth)):
    """列出产品碳足迹档案"""
    cid = company_id or current_user.get("company_id", 1)
    products = list_product_footprints(cid)
    return {"success": True, "data": products, "count": len(products)}


@router.get("/products/{product_id}", summary="产品碳足迹详情")
async def get_product(product_id: int, current_user: dict = Depends(require_auth)):
    """获取产品碳足迹详情（含所有阶段）"""
    try:
        result = get_product_footprint_detail(product_id)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/products/{product_id}", summary="删除产品碳足迹")
async def delete_product(product_id: int, current_user: dict = Depends(require_auth)):
    """删除产品碳足迹档案及所有关联阶段"""
    deleted = delete_product_footprint(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="产品不存在")
    return {"success": True, "message": "产品碳足迹已删除"}


# ─── 生命周期阶段 ───────────────────────────────────────

@router.post("/products/{product_id}/stages", summary="添加生命周期阶段")
async def add_stage(product_id: int, req: StageAdd, current_user: dict = Depends(require_auth)):
    """为产品添加生命周期阶段的排放数据"""
    try:
        result = add_footprint_stage(
            product_id=product_id,
            stage=req.stage,
            material_name=req.material_name,
            quantity=req.quantity,
            unit=req.unit,
            emission_factor=req.emission_factor,
            source=req.source,
            notes=req.notes
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── 计算 ───────────────────────────────────────────────

@router.post("/products/{product_id}/calculate", summary="计算产品碳足迹")
async def calculate_footprint(product_id: int, current_user: dict = Depends(require_auth)):
    """汇总计算产品碳足迹，返回各阶段分布和总排放量"""
    try:
        result = calculate_product_footprint(product_id)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/products/compare", summary="产品碳足迹对比")
async def compare(req: ProductCompareRequest, current_user: dict = Depends(require_auth)):
    """对比多个产品的碳足迹，找出最优/最差"""
    result = compare_products(req.product_ids)
    return {"success": True, "data": result}


# ─── 枚举 ───────────────────────────────────────────────

@router.get("/stages", summary="生命周期阶段枚举")
async def list_stages():
    """返回所有可选的生命周期阶段"""
    return {"success": True, "data": LIFE_CYCLE_STAGES}