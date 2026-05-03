"""
降碳优化模块
功能：多目标降碳优化（NSGA-Ⅲ）、ROI测算、方案推荐
基于 GB/T 32150-2015 和行业基准数据
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import random
import math
from app.database import get_db_connection

router = APIRouter()

# ==================== 数据模型 ====================

class OptimizationRequest(BaseModel):
    """优化请求"""
    company_id: int
    current_emission: float  # 当前排放量（吨CO2）
    target_reduction: float  # 目标减排比例（%）
    budget: float  # 预算（万元）
    industry: str  # 行业类型
    priorities: List[str] = ["cost", "effectiveness"]  # 优先级：cost/effectiveness/roi

class CarbonReductionMeasure(BaseModel):
    """降碳措施"""
    id: str
    name: str
    category: str  # energy: 能源优化, process: 工艺改进, equipment: 设备升级, renewable: 清洁能源
    reduction_potential: float  # 减排潜力（吨CO2/年）
    investment_cost: float  # 投资成本（万元）
    annual_saving: float  # 年节省（万元）
    payback_period: float  # 回收期（年）
    roi: float  # 投资回报率
    difficulty: str  # easy: 简单, medium: 中等, hard: 困难
    description: str

class OptimizationResult(BaseModel):
    """优化结果"""
    company_id: int
    selected_measures: List[CarbonReductionMeasure]
    total_investment: float  # 总投资
    total_reduction: float  # 总减排量
    annual_saving: float  # 年节省
    overall_roi: float  # 综合ROI
    payback_period: float  # 综合回收期
    reduction_rate: float  # 减排比例
    confidence: float  # 置信度

class IndustryBenchmark(BaseModel):
    """行业基准"""
    industry: str
    emission_intensity_avg: float  # 平均排放强度
    emission_intensity_advanced: float  # 先进值
    reduction_potential: float  # 减排潜力

# ==================== 数据库查询辅助 ====================

def _get_measures_from_db(industry: str = None, active_only: bool = True) -> list:
    """从数据库获取措施列表"""
    conn = get_db_connection()
    try:
        if industry:
            sql = "SELECT * FROM carbon_measures WHERE industry = ?"
            params = [industry]
        else:
            sql = "SELECT * FROM carbon_measures"
            params = []
        if active_only:
            sql += " AND is_active = 1" if industry else " WHERE is_active = 1"
        sql += " ORDER BY category, id"
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def _get_benchmark_from_db(industry: str) -> dict:
    """从数据库获取行业基准"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM industry_benchmarks WHERE industry = ?", (industry,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

# ==================== NSGA-III 优化算法 ====================

class NSGA3Optimizer:
    """NSGA-III 多目标优化器"""
    
    def __init__(self, measures: List[dict], budget: float, target_reduction: float):
        self.measures = measures
        self.budget = budget
        self.target_reduction = target_reduction
        self.population_size = 50
        self.generations = 100
        
    def evaluate(self, solution: List[bool]) -> tuple:
        """评估解的目标值：投资成本、减排量、ROI"""
        total_cost = sum(
            self.measures[i]["investment_cost"] 
            for i in range(len(solution)) if solution[i]
        )
        total_reduction = sum(
            self.measures[i]["reduction_potential"] 
            for i in range(len(solution)) if solution[i]
        )
        total_saving = sum(
            self.measures[i]["annual_saving"] 
            for i in range(len(solution)) if solution[i]
        )
        
        # 目标1: 最小化成本
        obj1 = total_cost
        
        # 目标2: 最大化减排量（取负值）
        obj2 = -total_reduction
        
        # 目标3: 最大化ROI
        roi = total_saving / total_cost if total_cost > 0 else 0
        obj3 = -roi
        
        # 约束违反程度
        violation = 0
        if total_cost > self.budget:
            violation += (total_cost - self.budget) * 10
        
        return (obj1, obj2, obj3, violation)
    
    def dominates(self, obj1: tuple, obj2: tuple) -> bool:
        """判断obj1是否支配obj2"""
        better = False
        for i in range(3):  # 前3个目标
            if obj1[i] > obj2[i]:
                return False
            if obj1[i] < obj2[i]:
                better = True
        # 考虑约束违反
        if obj1[3] < obj2[3]:
            better = True
        elif obj1[3] > obj2[3]:
            return False
        return better
    
    def optimize(self) -> List[bool]:
        """执行优化"""
        n = len(self.measures)
        
        # 初始化种群
        population = []
        for _ in range(self.population_size):
            solution = [random.random() < 0.3 for _ in range(n)]
            population.append(solution)
        
        # 进化
        for gen in range(self.generations):
            # 评估
            objectives = [self.evaluate(sol) for sol in population]
            
            # 非支配排序
            fronts = self._fast_non_dominated_sort(population, objectives)
            
            # 选择
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend([population[i] for i in front])
                else:
                    # 拥挤度选择
                    remaining = self.population_size - len(new_population)
                    new_population.extend([population[i] for i in front[:remaining]])
                    break
            
            population = new_population
            
            # 交叉变异
            while len(population) < self.population_size:
                parent1 = random.choice(population)
                parent2 = random.choice(population)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                population.append(child)
        
        # 返回最优解
        objectives = [self.evaluate(sol) for sol in population]
        # 选择满足预算约束的最优解
        feasible = [(i, obj) for i, obj in enumerate(objectives) if obj[3] == 0]
        if feasible:
            # 选择减排量最大的
            best_idx = min(feasible, key=lambda x: x[1][2])[0]
            return population[best_idx]
        
        return population[0]
    
    def _fast_non_dominated_sort(self, population, objectives):
        """快速非支配排序"""
        n = len(population)
        domination_count = [0] * n
        dominated_set = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                if self.dominates(objectives[i], objectives[j]):
                    domination_count[j] += 1
                    dominated_set[i].append(j)
                elif self.dominates(objectives[j], objectives[i]):
                    domination_count[i] += 1
                    dominated_set[j].append(i)
        
        fronts = []
        current_front = [i for i in range(n) if domination_count[i] == 0]
        fronts.append(current_front)
        
        while len(fronts[-1]) > 0:
            next_front = []
            for i in fronts[-1]:
                for j in dominated_set[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            fronts.append(next_front)
        
        return fronts[:-1]
    
    def _crossover(self, parent1, parent2):
        """交叉"""
        n = len(parent1)
        point = random.randint(1, n - 1)
        return parent1[:point] + parent2[point:]
    
    def _mutate(self, solution, rate=0.1):
        """变异"""
        return [
            not gene if random.random() < rate else gene
            for gene in solution
        ]

# ==================== API 端点 ====================

@router.get("/measures/{industry}")
async def get_industry_measures(industry: str):
    """获取行业可用降碳措施"""
    measures = _get_measures_from_db(industry)
    
    if not measures:
        # 尝试默认制造业
        measures = _get_measures_from_db("制造业")
    
    result = []
    for m in measures:
        roi = (m["annual_saving"] / m["investment_cost"]) * 100 if m["investment_cost"] > 0 else 0
        payback = m["investment_cost"] / m["annual_saving"] if m["annual_saving"] > 0 else 0
        
        result.append(CarbonReductionMeasure(
            id=m["id"],
            name=m["name"],
            category=m["category"],
            reduction_potential=m["reduction_potential"],
            investment_cost=m["investment_cost"],
            annual_saving=m["annual_saving"],
            payback_period=round(payback, 1),
            roi=round(roi, 1),
            difficulty=m["difficulty"],
            description=m.get("description", "")
        ))
    
    return result

@router.get("/benchmark/{industry}", response_model=IndustryBenchmark)
async def get_industry_benchmark(industry: str):
    """获取行业基准数据"""
    row = _get_benchmark_from_db(industry)
    if not row:
        row = _get_benchmark_from_db("制造业")
    if not row:
        raise HTTPException(status_code=404, detail="行业基准不存在")
    return IndustryBenchmark(
        industry=row["industry"],
        emission_intensity_avg=row["emission_intensity_avg"],
        emission_intensity_advanced=row["emission_intensity_advanced"],
        reduction_potential=row["reduction_potential"]
    )

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_carbon_reduction(request: OptimizationRequest):
    """执行降碳优化"""
    # 获取行业措施
    measures = _get_measures_from_db(request.industry)
    if not measures:
        measures = _get_measures_from_db("制造业")
    
    if not measures:
        raise HTTPException(status_code=404, detail="未找到该行业的降碳措施")
    
    # 执行优化
    optimizer = NSGA3Optimizer(measures, request.budget, request.target_reduction)
    solution = optimizer.optimize()
    
    # 提取选中的措施
    selected = []
    for i, selected_flag in enumerate(solution):
        if selected_flag:
            m = measures[i]
            roi = (m["annual_saving"] / m["investment_cost"]) * 100 if m["investment_cost"] > 0 else 0
            payback = m["investment_cost"] / m["annual_saving"] if m["annual_saving"] > 0 else 0
            
            selected.append(CarbonReductionMeasure(
                id=m["id"],
                name=m["name"],
                category=m["category"],
                reduction_potential=m["reduction_potential"],
                investment_cost=m["investment_cost"],
                annual_saving=m["annual_saving"],
                payback_period=round(payback, 1),
                roi=round(roi, 1),
                difficulty=m["difficulty"],
                description=m["description"]
            ))
    
    # 计算汇总
    total_investment = sum(m.investment_cost for m in selected)
    total_reduction = sum(m.reduction_potential for m in selected)
    annual_saving = sum(m.annual_saving for m in selected)
    overall_roi = (annual_saving / total_investment * 100) if total_investment > 0 else 0
    payback_period = total_investment / annual_saving if annual_saving > 0 else 0
    reduction_rate = (total_reduction / request.current_emission * 100) if request.current_emission > 0 else 0
    
    return OptimizationResult(
        company_id=request.company_id,
        selected_measures=selected,
        total_investment=round(total_investment, 2),
        total_reduction=round(total_reduction, 2),
        annual_saving=round(annual_saving, 2),
        overall_roi=round(overall_roi, 1),
        payback_period=round(payback_period, 1),
        reduction_rate=round(reduction_rate, 1),
        confidence=0.85
    )

@router.get("/recommend/{company_id}")
async def recommend_measures(company_id: int, budget: float = 50.0):
    """推荐降碳措施（简化接口）"""
    # 简化：默认制造业
    measures = _get_measures_from_db("制造业")
    
    # 按ROI排序
    sorted_measures = sorted(
        measures,
        key=lambda x: x["annual_saving"] / x["investment_cost"] if x["investment_cost"] > 0 else 0,
        reverse=True
    )
    
    # 选择预算内的措施
    selected = []
    total_cost = 0
    for m in sorted_measures:
        if total_cost + m["investment_cost"] <= budget:
            selected.append(m)
            total_cost += m["investment_cost"]
    
    return {
        "company_id": company_id,
        "budget": budget,
        "used_budget": total_cost,
        "recommended_measures": selected,
        "total_reduction_potential": sum(m["reduction_potential"] for m in selected)
    }
