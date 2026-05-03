"""
降碳措施库 CRUD 管理
支持动态增删改查措施 + 行业基准管理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import get_db_connection

router = APIRouter()


# ==================== 数据模型 ====================

class MeasureCreate(BaseModel):
    """创建措施"""
    id: str
    industry: str
    name: str
    category: str  # energy / process / equipment / renewable
    reduction_potential: float
    investment_cost: float
    annual_saving: float
    difficulty: str  # easy / medium / hard
    description: Optional[str] = ""


class MeasureUpdate(BaseModel):
    """更新措施（所有字段可选）"""
    industry: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    reduction_potential: Optional[float] = None
    investment_cost: Optional[float] = None
    annual_saving: Optional[float] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None


class BenchmarkCreate(BaseModel):
    """创建行业基准"""
    industry: str
    emission_intensity_avg: float
    emission_intensity_advanced: float
    reduction_potential: float


class BenchmarkUpdate(BaseModel):
    """更新行业基准"""
    emission_intensity_avg: Optional[float] = None
    emission_intensity_advanced: Optional[float] = None
    reduction_potential: Optional[float] = None


# ==================== 措施 CRUD ====================

@router.get("/measures")
async def list_measures(
    industry: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_active: Optional[int] = 1,
    limit: int = 100,
    offset: int = 0
):
    """查询措施列表，支持筛选"""
    conn = get_db_connection()
    try:
        conditions = []
        params = []

        if industry:
            conditions.append("industry = ?")
            params.append(industry)
        if category:
            conditions.append("category = ?")
            params.append(category)
        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)
        if is_active is not None:
            conditions.append("is_active = ?")
            params.append(is_active)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 总数
        cursor = conn.execute(f"SELECT COUNT(*) FROM carbon_measures{where}", params)
        total = cursor.fetchone()[0]

        # 分页
        cursor = conn.execute(
            f"SELECT * FROM carbon_measures{where} ORDER BY industry, category, id LIMIT ? OFFSET ?",
            params + [limit, offset]
        )
        rows = [dict(row) for row in cursor.fetchall()]

        return {"total": total, "limit": limit, "offset": offset, "data": rows}
    finally:
        conn.close()


@router.get("/measures/{measure_id}")
async def get_measure(measure_id: str):
    """获取单条措施"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM carbon_measures WHERE id = ?", (measure_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="措施不存在")
        return dict(row)
    finally:
        conn.close()


@router.post("/measures", status_code=201)
async def create_measure(measure: MeasureCreate):
    """创建措施"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO carbon_measures 
            (id, industry, name, category, reduction_potential, investment_cost, annual_saving, difficulty, description)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (measure.id, measure.industry, measure.name, measure.category,
             measure.reduction_potential, measure.investment_cost, measure.annual_saving,
             measure.difficulty, measure.description)
        )
        conn.commit()
        return {"message": "创建成功", "id": measure.id}
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=409, detail="措施ID已存在")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.put("/measures/{measure_id}")
async def update_measure(measure_id: str, measure: MeasureUpdate):
    """更新措施"""
    conn = get_db_connection()
    try:
        # 检查存在
        cursor = conn.execute("SELECT id FROM carbon_measures WHERE id = ?", (measure_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="措施不存在")

        # 构建动态UPDATE
        fields = []
        params = []
        for key, value in measure.model_dump(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return {"message": "无更新内容"}

        fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(measure_id)

        conn.execute(
            f"UPDATE carbon_measures SET {', '.join(fields)} WHERE id = ?",
            params
        )
        conn.commit()
        return {"message": "更新成功", "id": measure_id}
    finally:
        conn.close()


@router.delete("/measures/{measure_id}")
async def delete_measure(measure_id: str, hard: bool = False):
    """删除措施（默认软删除）"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT id FROM carbon_measures WHERE id = ?", (measure_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="措施不存在")

        if hard:
            conn.execute("DELETE FROM carbon_measures WHERE id = ?", (measure_id,))
        else:
            conn.execute(
                "UPDATE carbon_measures SET is_active = 0, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), measure_id)
            )
        conn.commit()
        return {"message": "删除成功", "id": measure_id, "hard_delete": hard}
    finally:
        conn.close()


# ==================== 行业基准 CRUD ====================

@router.get("/benchmarks")
async def list_benchmarks():
    """获取所有行业基准"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM industry_benchmarks ORDER BY industry")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/benchmarks/{industry}")
async def get_benchmark(industry: str):
    """获取行业基准"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM industry_benchmarks WHERE industry = ?", (industry,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="行业基准不存在")
        return dict(row)
    finally:
        conn.close()


@router.post("/benchmarks", status_code=201)
async def create_benchmark(benchmark: BenchmarkCreate):
    """创建行业基准"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO industry_benchmarks 
            (industry, emission_intensity_avg, emission_intensity_advanced, reduction_potential)
            VALUES (?,?,?,?)""",
            (benchmark.industry, benchmark.emission_intensity_avg,
             benchmark.emission_intensity_advanced, benchmark.reduction_potential)
        )
        conn.commit()
        return {"message": "创建成功", "industry": benchmark.industry}
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=409, detail="行业基准已存在")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.put("/benchmarks/{industry}")
async def update_benchmark(industry: str, benchmark: BenchmarkUpdate):
    """更新行业基准"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT industry FROM industry_benchmarks WHERE industry = ?", (industry,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="行业基准不存在")

        fields = []
        params = []
        for key, value in benchmark.model_dump(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return {"message": "无更新内容"}

        fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(industry)

        conn.execute(
            f"UPDATE industry_benchmarks SET {', '.join(fields)} WHERE industry = ?",
            params
        )
        conn.commit()
        return {"message": "更新成功", "industry": industry}
    finally:
        conn.close()


@router.delete("/benchmarks/{industry}")
async def delete_benchmark(industry: str):
    """删除行业基准"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT industry FROM industry_benchmarks WHERE industry = ?", (industry,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="行业基准不存在")

        conn.execute("DELETE FROM industry_benchmarks WHERE industry = ?", (industry,))
        conn.commit()
        return {"message": "删除成功", "industry": industry}
    finally:
        conn.close()


# ==================== 统计 ====================

@router.get("/stats")
async def measures_stats():
    """措施库统计"""
    conn = get_db_connection()
    try:
        # 按行业统计
        cursor = conn.execute(
            "SELECT industry, COUNT(*) as count, is_active FROM carbon_measures GROUP BY industry, is_active"
        )
        industry_stats = {}
        for row in cursor.fetchall():
            d = dict(row)
            ind = d["industry"]
            if ind not in industry_stats:
                industry_stats[ind] = {"active": 0, "inactive": 0, "total": 0}
            if d["is_active"]:
                industry_stats[ind]["active"] = d["count"]
            else:
                industry_stats[ind]["inactive"] = d["count"]
            industry_stats[ind]["total"] += d["count"]

        # 按类别统计
        cursor = conn.execute(
            "SELECT category, COUNT(*) as count FROM carbon_measures WHERE is_active = 1 GROUP BY category"
        )
        category_stats = {dict(row)["category"]: dict(row)["count"] for row in cursor.fetchall()}

        # 总数
        cursor = conn.execute("SELECT COUNT(*) FROM carbon_measures")
        total = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM carbon_measures WHERE is_active = 1")
        active = cursor.fetchone()[0]

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_industry": industry_stats,
            "by_category": category_stats
        }
    finally:
        conn.close()
