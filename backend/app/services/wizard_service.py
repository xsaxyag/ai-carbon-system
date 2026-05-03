"""
AI碳枢算 - 智能填报向导服务
根据行业特征自动推荐排放源组合、典型消耗量、单位
支持一键生成填报模板
"""
from app.database import get_db_connection
from typing import Optional


# ========== 行业→排放源推荐映射 ==========

INDUSTRY_PROFILES = {
    "制造业": {
        "name": "制造业",
        "icon": "🏭",
        "description": "涵盖机械制造、电子制造、纺织制造等",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "natural_gas",
                "label": "天然气（生产加热）",
                "unit": "m3",
                "typical_quantity": 50000,
                "quantity_range": [5000, 500000],
                "tip": "用于生产过程中的加热、烘干工序",
            },
            {
                "scope": "scope1",
                "emission_source": "diesel",
                "label": "柴油（厂内运输/发电机）",
                "unit": "L",
                "typical_quantity": 5000,
                "quantity_range": [500, 50000],
                "tip": "厂内叉车、物流车、备用发电机",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（生产用电）",
                "unit": "kWh",
                "typical_quantity": 200000,
                "quantity_range": [20000, 2000000],
                "tip": "生产线设备、照明、空调等",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "一般废弃物（填埋）",
                "unit": "kg",
                "typical_quantity": 2000,
                "quantity_range": [200, 20000],
                "tip": "生产废料、包装废弃物",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_equipment",
                "label": "设备采购",
                "unit": "CNY",
                "typical_quantity": 500000,
                "quantity_range": [50000, 5000000],
                "tip": "生产设备、工具采购支出",
            },
        ],
    },
    "信息技术": {
        "name": "信息技术",
        "icon": "💻",
        "description": "软件开发、互联网服务、数据中心",
        "typical_sources": [
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（办公+机房）",
                "unit": "kWh",
                "typical_quantity": 100000,
                "quantity_range": [10000, 1000000],
                "tip": "服务器机房、办公区空调照明",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_office",
                "label": "办公用品采购",
                "unit": "CNY",
                "typical_quantity": 50000,
                "quantity_range": [5000, 500000],
                "tip": "办公耗材、文具、IT外设",
            },
            {
                "scope": "scope3",
                "emission_source": "business_flight_short",
                "label": "商务出差（短途航班）",
                "unit": "km",
                "typical_quantity": 10000,
                "quantity_range": [1000, 50000],
                "tip": "国内短途商务出行",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "办公废弃物",
                "unit": "kg",
                "typical_quantity": 500,
                "quantity_range": [50, 5000],
                "tip": "办公垃圾、废旧电子设备",
            },
            {
                "scope": "scope3",
                "emission_source": "renewable",
                "label": "绿电采购",
                "unit": "kWh",
                "typical_quantity": 30000,
                "quantity_range": [5000, 500000],
                "tip": "购买绿色电力证书或直接采购绿电",
            },
        ],
    },
    "零售业": {
        "name": "零售业",
        "icon": "🛒",
        "description": "商超零售、电商平台、连锁门店",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "natural_gas",
                "label": "天然气（门店供暖/烹饪）",
                "unit": "m3",
                "typical_quantity": 10000,
                "quantity_range": [1000, 100000],
                "tip": "门店冬季供暖、食品加工区",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（照明+冷链）",
                "unit": "kWh",
                "typical_quantity": 80000,
                "quantity_range": [10000, 500000],
                "tip": "门店照明、空调、冷藏柜",
            },
            {
                "scope": "scope3",
                "emission_source": "business_car",
                "label": "物流配送车辆",
                "unit": "km",
                "typical_quantity": 30000,
                "quantity_range": [5000, 200000],
                "tip": "配送中心→门店的物流车辆",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_office",
                "label": "商品采购",
                "unit": "CNY",
                "typical_quantity": 2000000,
                "quantity_range": [200000, 20000000],
                "tip": "商品进货成本（用于估算供应链排放）",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "包装废弃物",
                "unit": "kg",
                "typical_quantity": 3000,
                "quantity_range": [300, 30000],
                "tip": "商品包装、运输填充物",
            },
        ],
    },
    "金融业": {
        "name": "金融业",
        "icon": "🏦",
        "description": "银行、保险、证券、基金",
        "typical_sources": [
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（办公用电）",
                "unit": "kWh",
                "typical_quantity": 50000,
                "quantity_range": [5000, 300000],
                "tip": "办公楼照明、空调、IT设备",
            },
            {
                "scope": "scope3",
                "emission_source": "business_flight_medium",
                "label": "商务出差（中途航班）",
                "unit": "km",
                "typical_quantity": 20000,
                "quantity_range": [2000, 100000],
                "tip": "跨省商务出行、客户拜访",
            },
            {
                "scope": "scope3",
                "emission_source": "business_train",
                "label": "商务出行（高铁）",
                "unit": "km",
                "typical_quantity": 15000,
                "quantity_range": [2000, 80000],
                "tip": "区域内高铁商务出行",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_office",
                "label": "办公采购",
                "unit": "CNY",
                "typical_quantity": 20000,
                "quantity_range": [2000, 200000],
                "tip": "办公耗材、文具、打印",
            },
        ],
    },
    "教育": {
        "name": "教育",
        "icon": "🎓",
        "description": "高校、培训机构、在线教育",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "natural_gas",
                "label": "天然气（食堂/供暖）",
                "unit": "m3",
                "typical_quantity": 20000,
                "quantity_range": [2000, 200000],
                "tip": "学校食堂烹饪、冬季供暖锅炉",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（教学+办公）",
                "unit": "kWh",
                "typical_quantity": 120000,
                "quantity_range": [15000, 800000],
                "tip": "教室照明、空调、实验室设备",
            },
            {
                "scope": "scope3",
                "emission_source": "business_train",
                "label": "教职工差旅（火车）",
                "unit": "km",
                "typical_quantity": 8000,
                "quantity_range": [1000, 50000],
                "tip": "学术会议、调研出差",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "校园废弃物",
                "unit": "kg",
                "typical_quantity": 5000,
                "quantity_range": [500, 30000],
                "tip": "食堂厨余、办公垃圾",
            },
        ],
    },
    "医疗健康": {
        "name": "医疗健康",
        "icon": "🏥",
        "description": "医院、诊所、医药企业",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "natural_gas",
                "label": "天然气（消毒/供暖）",
                "unit": "m3",
                "typical_quantity": 30000,
                "quantity_range": [5000, 300000],
                "tip": "医疗设备消毒、供暖锅炉",
            },
            {
                "scope": "scope1",
                "emission_source": "gasoline",
                "label": "汽油（救护车）",
                "unit": "L",
                "typical_quantity": 2000,
                "quantity_range": [200, 20000],
                "tip": "救护车、公务用车",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（医疗设备+照明）",
                "unit": "kWh",
                "typical_quantity": 150000,
                "quantity_range": [20000, 1000000],
                "tip": "CT/MRI等大型设备、手术室、ICU",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_incineration",
                "label": "医疗废物（焚烧）",
                "unit": "kg",
                "typical_quantity": 3000,
                "quantity_range": [300, 30000],
                "tip": "感染性废物、损伤性废物须焚烧处理",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_equipment",
                "label": "医疗设备采购",
                "unit": "CNY",
                "typical_quantity": 1000000,
                "quantity_range": [100000, 10000000],
                "tip": "医疗器械、耗材采购支出",
            },
        ],
    },
    "建筑业": {
        "name": "建筑业",
        "icon": "🏗️",
        "description": "建筑施工、工程承包、建材生产",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "diesel",
                "label": "柴油（工程机械）",
                "unit": "L",
                "typical_quantity": 20000,
                "quantity_range": [2000, 200000],
                "tip": "挖掘机、推土机、起重机等",
            },
            {
                "scope": "scope1",
                "emission_source": "coal",
                "label": "煤炭（建材生产）",
                "unit": "kg",
                "typical_quantity": 10000,
                "quantity_range": [1000, 100000],
                "tip": "水泥/砖窑烧制用煤",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（施工用电）",
                "unit": "kWh",
                "typical_quantity": 80000,
                "quantity_range": [10000, 500000],
                "tip": "工地临时用电、混凝土搅拌",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "建筑废弃物（填埋）",
                "unit": "kg",
                "typical_quantity": 10000,
                "quantity_range": [1000, 100000],
                "tip": "施工废料、装修废料",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_equipment",
                "label": "建材采购",
                "unit": "CNY",
                "typical_quantity": 3000000,
                "quantity_range": [300000, 30000000],
                "tip": "钢材、水泥、玻璃等建材",
            },
        ],
    },
    "交通运输": {
        "name": "交通运输",
        "icon": "🚛",
        "description": "物流运输、客运、仓储",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "diesel",
                "label": "柴油（货运车辆）",
                "unit": "L",
                "typical_quantity": 80000,
                "quantity_range": [10000, 500000],
                "tip": "货车、牵引车、工程车辆",
            },
            {
                "scope": "scope1",
                "emission_source": "gasoline",
                "label": "汽油（客运车辆）",
                "unit": "L",
                "typical_quantity": 30000,
                "quantity_range": [5000, 200000],
                "tip": "出租车、公交、商务车",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（仓储+充电桩）",
                "unit": "kWh",
                "typical_quantity": 60000,
                "quantity_range": [10000, 500000],
                "tip": "仓库照明、电动车充电桩",
            },
            {
                "scope": "scope3",
                "emission_source": "renewable",
                "label": "绿电采购",
                "unit": "kWh",
                "typical_quantity": 20000,
                "quantity_range": [5000, 200000],
                "tip": "碳中和目标下的绿电采购",
            },
        ],
    },
    "餐饮住宿": {
        "name": "餐饮住宿",
        "icon": "🏨",
        "description": "餐饮、酒店、民宿",
        "typical_sources": [
            {
                "scope": "scope1",
                "emission_source": "natural_gas",
                "label": "天然气（厨房烹饪）",
                "unit": "m3",
                "typical_quantity": 8000,
                "quantity_range": [1000, 50000],
                "tip": "餐饮烹饪、锅炉热水",
            },
            {
                "scope": "scope2",
                "emission_source": "electricity",
                "label": "外购电力（空调+照明）",
                "unit": "kWh",
                "typical_quantity": 40000,
                "quantity_range": [5000, 200000],
                "tip": "中央空调、客房照明、厨房设备",
            },
            {
                "scope": "scope3",
                "emission_source": "waste_landfill",
                "label": "厨余垃圾（填埋）",
                "unit": "kg",
                "typical_quantity": 2000,
                "quantity_range": [200, 10000],
                "tip": "餐厨废弃物",
            },
            {
                "scope": "scope3",
                "emission_source": "purchased_office",
                "label": "食材采购",
                "unit": "CNY",
                "typical_quantity": 300000,
                "quantity_range": [30000, 3000000],
                "tip": "食材、酒水进货成本",
            },
        ],
    },
}

# 所有排放源的中文标签
SOURCE_LABELS = {
    "natural_gas": "天然气",
    "coal": "煤炭",
    "gasoline": "汽油",
    "diesel": "柴油",
    "electricity": "外购电力",
    "renewable": "绿电/可再生能源",
    "business_flight_short": "短途航班（<3h）",
    "business_flight_medium": "中途航班（3-6h）",
    "business_flight_long": "长途航班（>6h）",
    "business_train": "火车/高铁",
    "business_car": "公务汽车",
    "waste_landfill": "废弃物填埋",
    "waste_incineration": "废弃物焚烧",
    "waste_composting": "废弃物堆肥",
    "purchased_office": "办公用品采购",
    "purchased_equipment": "设备采购",
}

# scope中文标签
SCOPE_LABELS = {
    "scope1": "范围1-直接排放",
    "scope2": "范围2-外购电力",
    "scope3": "范围3-其他间接排放",
}

# 地区选项
REGION_OPTIONS = [
    {"value": "华北", "label": "华北（北京/天津/河北/山西/内蒙）"},
    {"value": "东北", "label": "东北（辽宁/吉林/黑龙江）"},
    {"value": "华东", "label": "华东（上海/江苏/浙江/安徽/福建/山东）"},
    {"value": "华中", "label": "华中（河南/湖北/湖南/江西）"},
    {"value": "南方", "label": "南方（广东/广西/海南/重庆/四川/贵州/云南）"},
    {"value": "西北", "label": "西北（陕西/甘肃/青海/宁夏/新疆）"},
]


class WizardService:
    """智能填报向导服务"""

    @staticmethod
    def get_industry_list() -> list:
        """获取行业列表"""
        result = []
        for key, profile in INDUSTRY_PROFILES.items():
            result.append({
                "industry": key,
                "name": profile["name"],
                "icon": profile["icon"],
                "description": profile["description"],
                "source_count": len(profile["typical_sources"]),
            })
        return result

    @staticmethod
    def get_industry_profile(industry: str) -> Optional[dict]:
        """获取行业填报模板"""
        profile = INDUSTRY_PROFILES.get(industry)
        if not profile:
            return None
        return {
            "industry": industry,
            "name": profile["name"],
            "icon": profile["icon"],
            "description": profile["description"],
            "recommended_sources": profile["typical_sources"],
        }

    @staticmethod
    def get_all_sources() -> list:
        """获取所有排放源完整选项（带scope/单位/典型值）"""
        from app.services.validation_service import SCOPE_SOURCE_MAP, SOURCE_UNITS, QUANTITY_RANGES
        from app.services.carbon_calc import EMISSION_FACTORS

        result = []
        for scope, sources in SCOPE_SOURCE_MAP.items():
            for source in sorted(sources):
                units = list(SOURCE_UNITS.get(source, set()))
                factor_info = EMISSION_FACTORS.get(source, {})
                factors = {u: f for u, f in factor_info.items()}

                qty_range = QUANTITY_RANGES.get(source, (1, 1_000_000))

                # 从行业模板中提取典型值
                typical_quantity = None
                typical_unit = units[0] if units else ""
                for profile in INDUSTRY_PROFILES.values():
                    for s in profile["typical_sources"]:
                        if s["emission_source"] == source and typical_quantity is None:
                            typical_quantity = s["typical_quantity"]
                            typical_unit = s["unit"]

                result.append({
                    "scope": scope,
                    "scope_label": SCOPE_LABELS.get(scope, scope),
                    "emission_source": source,
                    "label": SOURCE_LABELS.get(source, source),
                    "units": units,
                    "default_unit": typical_unit or (units[0] if units else ""),
                    "emission_factors": factors,
                    "quantity_range": list(qty_range),
                    "typical_quantity": typical_quantity,
                })
        return result

    @staticmethod
    def generate_template(industry: str, company_id: int, record_date: str, region: str = "华东") -> dict:
        """
        根据行业生成填报模板
        返回可直接用于批量创建的记录列表
        """
        profile = INDUSTRY_PROFILES.get(industry)
        if not profile:
            return {"error": f"未找到行业 '{industry}' 的模板", "available": list(INDUSTRY_PROFILES.keys())}

        from app.services.carbon_calc import calculate_co2_emission, CarbonScope, EmissionSource

        records = []
        total_estimated = 0.0

        for source_info in profile["typical_sources"]:
            scope_enum = CarbonScope(source_info["scope"])
            source_enum = EmissionSource(source_info["emission_source"])
            quantity = source_info["typical_quantity"]
            unit = source_info["unit"]

            calc = calculate_co2_emission(scope_enum, source_enum, quantity, unit, region)

            records.append({
                "company_id": company_id,
                "scope": source_info["scope"],
                "emission_source": source_info["emission_source"],
                "label": source_info["label"],
                "quantity": quantity,
                "unit": unit,
                "estimated_co2": calc["co2_emission"],
                "emission_factor": calc["emission_factor"],
                "quantity_range": source_info["quantity_range"],
                "tip": source_info["tip"],
            })
            total_estimated += calc["co2_emission"]

        return {
            "industry": industry,
            "company_id": company_id,
            "record_date": record_date,
            "region": region,
            "records": records,
            "total_estimated_co2": round(total_estimated, 2),
            "note": "以上为行业典型值，请根据实际情况修改消耗量后提交",
        }

    @staticmethod
    def quick_estimate(industry: str, region: str = "华东") -> dict:
        """快速估算行业碳排放量级"""
        profile = INDUSTRY_PROFILES.get(industry)
        if not profile:
            return {"error": f"未找到行业 '{industry}'"}

        from app.services.carbon_calc import calculate_co2_emission, CarbonScope, EmissionSource

        scope_totals = {"scope1": 0, "scope2": 0, "scope3": 0}
        details = []

        for source_info in profile["typical_sources"]:
            scope_enum = CarbonScope(source_info["scope"])
            source_enum = EmissionSource(source_info["emission_source"])
            calc = calculate_co2_emission(scope_enum, source_enum, source_info["typical_quantity"], source_info["unit"], region)

            scope_totals[source_info["scope"]] += calc["co2_emission"]
            details.append({
                "source": SOURCE_LABELS.get(source_info["emission_source"], source_info["emission_source"]),
                "scope": source_info["scope"],
                "estimated_co2": calc["co2_emission"],
                "percentage": 0,  # 后面计算
            })

        total = sum(scope_totals.values())
        for d in details:
            d["percentage"] = round(d["estimated_co2"] / total * 100, 1) if total > 0 else 0

        return {
            "industry": industry,
            "region": region,
            "total_estimated": round(total, 2),
            "scope_breakdown": {k: round(v, 2) for k, v in scope_totals.items()},
            "details": details,
        }

    @staticmethod
    def get_company_recommendation(company_id: int) -> dict:
        """根据企业已有数据推荐下一步填报项"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取企业行业
        cursor.execute("SELECT industry FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        industry = row["industry"] if row else None

        # 获取已有记录的排放源
        cursor.execute(
            "SELECT DISTINCT emission_source, scope FROM carbon_records WHERE company_id = ?",
            (company_id,),
        )
        existing = {(r["emission_source"], r["scope"]) for r in cursor.fetchall()}
        conn.close()

        # 根据行业推荐缺失项
        recommended = []
        if industry and industry in INDUSTRY_PROFILES:
            for source_info in INDUSTRY_PROFILES[industry]["typical_sources"]:
                key = (source_info["emission_source"], source_info["scope"])
                if key not in existing:
                    recommended.append({
                        **source_info,
                        "status": "missing",
                        "reason": f"行业'{industry}'典型排放项，尚未填报",
                    })
                else:
                    recommended.append({
                        **source_info,
                        "status": "filled",
                        "reason": "已有记录",
                    })
        else:
            # 无行业信息，推荐最常见组合
            common_sources = [
                {"scope": "scope2", "emission_source": "electricity", "label": "外购电力", "unit": "kWh", "typical_quantity": 50000},
                {"scope": "scope1", "emission_source": "natural_gas", "label": "天然气", "unit": "m3", "typical_quantity": 10000},
                {"scope": "scope3", "emission_source": "waste_landfill", "label": "废弃物填埋", "unit": "kg", "typical_quantity": 1000},
            ]
            for source_info in common_sources:
                key = (source_info["emission_source"], source_info["scope"])
                if key not in existing:
                    recommended.append({**source_info, "status": "missing", "reason": "常见排放项，尚未填报"})
                else:
                    recommended.append({**source_info, "status": "filled", "reason": "已有记录"})

        missing_count = sum(1 for r in recommended if r["status"] == "missing")

        return {
            "company_id": company_id,
            "industry": industry,
            "existing_sources": len(existing),
            "missing_sources": missing_count,
            "recommendations": recommended,
            "suggestion": f"还有 {missing_count} 项行业典型排放源未填报" if missing_count > 0 else "行业典型排放项已填报完整",
        }
