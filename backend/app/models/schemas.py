"""
碳数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CarbonScope(str, Enum):
    """碳排放范围"""
    SCOPE1 = "scope1"   # 直接排放
    SCOPE2 = "scope2"   # 间接排放（电力）
    SCOPE3 = "scope3"   # 其他间接排放

class EmissionSource(str, Enum):
    """排放源类型"""
    NATURAL_GAS = "natural_gas"     # 天然气
    COAL = "coal"               # 煤炭
    ELECTRICITY = "electricity" # 外购电力
    GASOLINE = "gasoline"       # 汽油
    DIESEL = "diesel"          # 柴油
    RENEWABLE = "renewable"     # 可再生能源（绿电）
    # Scope3: 商务差旅
    BUSINESS_FLIGHT_SHORT = "business_flight_short"   # 短途飞机
    BUSINESS_FLIGHT_MEDIUM = "business_flight_medium" # 中途飞机
    BUSINESS_FLIGHT_LONG = "business_flight_long"    # 长途飞机
    BUSINESS_TRAIN = "business_train"                # 火车
    BUSINESS_CAR = "business_car"                    # 公务汽车
    # Scope3: 废物处理
    WASTE_LANDFILL = "waste_landfill"    # 填埋
    WASTE_INCINERATION = "waste_incineration"  # 焚烧
    WASTE_COMPOSTING = "waste_composting"      # 堆肥
    # Scope3: 采购商品
    PURCHASED_OFFICE = "purchased_office"      # 办公用品
    PURCHASED_EQUIPMENT = "purchased_equipment"  # 设备采购

class CompanyBase(BaseModel):
    """企业基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="企业名称")
    registration_no: Optional[str] = Field(None, min_length=1, max_length=50, description="统一社会信用代码")
    industry: Optional[str] = Field(None, min_length=1, max_length=50, description="所属行业")
    address: Optional[str] = Field(None, min_length=1, max_length=200, description="企业地址")

class CompanyCreate(CompanyBase):
    """创建企业"""
    pass

class Company(CompanyBase):
    """企业信息"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

import re

class CarbonRecordBase(BaseModel):
    """碳排放记录基础"""
    company_id: int = Field(..., gt=0, description="企业ID")
    record_date: str = Field(..., pattern=r'^\d{4}-(0[1-9]|1[0-2])$', description="记录日期 YYYY-MM")
    scope: CarbonScope = Field(..., description="碳排放范围")
    emission_source: EmissionSource = Field(..., description="排放源类型")
    quantity: float = Field(..., gt=0, description="消耗量（必须大于0）")
    unit: str = Field(..., min_length=1, max_length=20, description="单位")

class CarbonRecordCreate(CarbonRecordBase):
    """创建碳排放记录"""
    pass

class CarbonRecord(CarbonRecordBase):
    """碳排放记录"""
    id: int
    co2_emission: float = Field(..., description="碳排放量(kgCO2)")
    emission_factor: float = Field(..., description="排放因子")
    created_at: datetime
    
    class Config:
        from_attributes = True

class CarbonSummary(BaseModel):
    """碳排放汇总"""
    company_id: int
    total_scope1: float = Field(0, description="范围1总排放")
    total_scope2: float = Field(0, description="范围2总排放")
    total_scope3: float = Field(0, description="范围3总排放")
    total_emission: float = Field(0, description="总排放量")
    record_count: int = Field(0, description="记录数")

class OCRResult(BaseModel):
    """OCR识别结果"""
    success: bool
    image_name: str
    extracted_data: dict
    confidence: float = Field(0, description="置信度")

class CarbonCalculateRequest(BaseModel):
    """碳排放计算请求"""
    scope: CarbonScope
    emission_source: EmissionSource
    quantity: float = Field(..., gt=0, description="消耗量（必须大于0）")
    unit: str = Field(..., min_length=1, max_length=20, description="单位")

class CarbonCalculateResponse(BaseModel):
    """碳排放计算响应"""
    co2_emission: float
    emission_factor: float
    unit: str