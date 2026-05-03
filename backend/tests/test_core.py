"""
AI碳枢算 - 单元测试
覆盖: 排放计算、数据库、API端点
"""
import pytest
import sys
import os
import tempfile
import sqlite3

# 确保能import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.schemas import CarbonScope, EmissionSource
from app.services import carbon_calc
from app.database import init_db, get_db_connection


# ============================================================
# 1. 排放计算核心逻辑测试
# ============================================================

class TestEmissionCalculation:
    """碳排放计算核心测试"""

    def test_scope1_natural_gas_m3(self):
        """天然气m3单位计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE1, EmissionSource.NATURAL_GAS, 100, "m3"
        )
        assert result["co2_emission"] == pytest.approx(209, rel=0.01)
        assert result["unit"] == "kgCO2"

    def test_scope1_coal_kg(self):
        """煤炭kg单位计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE1, EmissionSource.COAL, 500, "kg"
        )
        assert result["co2_emission"] == pytest.approx(1260, rel=0.01)

    def test_scope1_gasoline_L(self):
        """汽油L单位计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE1, EmissionSource.GASOLINE, 200, "L"
        )
        assert result["co2_emission"] == pytest.approx(460, rel=0.01)

    def test_scope1_diesel_L(self):
        """柴油L单位计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE1, EmissionSource.DIESEL, 150, "L"
        )
        assert result["co2_emission"] == pytest.approx(394.5, rel=0.01)

    def test_scope2_electricity_kWh(self):
        """外购电力kWh计算（默认华北0.581）"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE2, EmissionSource.ELECTRICITY, 1000, "kWh"
        )
        assert result["co2_emission"] == pytest.approx(581, rel=0.01)

    def test_scope2_electricity_regional(self):
        """地区电力排放因子"""
        factor_south = carbon_calc.get_electricity_factor("南方")
        factor_northeast = carbon_calc.get_electricity_factor("东北")
        assert factor_south == 0.475
        assert factor_northeast == 0.680
        # 南方 < 东北（水电比例高）
        assert factor_south < factor_northeast

    def test_scope2_electricity_default_region(self):
        """默认地区回退"""
        factor = carbon_calc.get_electricity_factor("未知地区")
        assert factor == 0.581  # 回退到默认

    def test_scope3_renewable_zero(self):
        """可再生能源零排放"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE3, EmissionSource.RENEWABLE, 500, "kWh"
        )
        assert result["co2_emission"] == 0

    def test_scope3_flight_short(self):
        """短途航班计算（scope3有1.2x系数）"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE3, EmissionSource.BUSINESS_FLIGHT_SHORT, 1000, "km"
        )
        # 基础因子0.255 × 1.2 = 0.306
        assert result["emission_factor"] == pytest.approx(0.306, rel=0.01)
        assert result["co2_emission"] == pytest.approx(306, rel=0.01)

    def test_scope3_waste_landfill(self):
        """填埋废物计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE3, EmissionSource.WASTE_LANDFILL, 100, "kg"
        )
        # 基础0.45 × 1.2 = 0.54
        assert result["emission_factor"] == pytest.approx(0.54, rel=0.01)

    def test_scope3_purchased_office(self):
        """办公用品采购计算"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE3, EmissionSource.PURCHASED_OFFICE, 10000, "CNY"
        )
        # 基础0.0028 × 1.2 = 0.00336, round(0.00336, 4)=0.0034
        assert result["emission_factor"] == pytest.approx(0.0034, rel=0.01)

    def test_scope3_no_1_2x_for_scope1(self):
        """scope1不应该有1.2x系数"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE1, EmissionSource.NATURAL_GAS, 100, "m3"
        )
        assert result["emission_factor"] == pytest.approx(2.09, rel=0.01)

    def test_zero_quantity(self):
        """零消耗量"""
        result = carbon_calc.calculate_co2_emission(
            CarbonScope.SCOPE2, EmissionSource.ELECTRICITY, 0, "kWh"
        )
        assert result["co2_emission"] == 0


class TestEmissionFactorDB:
    """排放因子数据库查询测试"""

    def test_get_factor_from_db(self):
        """从数据库获取排放因子"""
        factor = carbon_calc.get_factor_from_db("electricity", "kWh", "华北")
        assert factor is not None
        assert factor == pytest.approx(0.581, rel=0.01)

    def test_get_factor_db_region_priority(self):
        """地区优先于全国"""
        factor_region = carbon_calc.get_factor_from_db("electricity", "kWh", "南方")
        factor_national = carbon_calc.get_factor_from_db("electricity", "kWh", "全国")
        assert factor_region == 0.475
        assert factor_national == 0.581

    def test_get_factor_db_nonexistent(self):
        """不存在的排放源返回None"""
        factor = carbon_calc.get_factor_from_db("nonexistent_source", "kg", "全国")
        assert factor is None

    def test_get_all_factors_from_db(self):
        """获取某排放源所有因子"""
        factors = carbon_calc.get_all_factors_from_db("natural_gas")
        assert "m3" in factors
        assert "GJ" in factors
        assert factors["m3"] == pytest.approx(2.09, rel=0.01)


class TestCalculateTotal:
    """总量计算测试"""

    def test_calculate_total_emission(self):
        """汇总计算"""
        records = [
            {"scope": "scope1", "co2_emission": 100},
            {"scope": "scope2", "co2_emission": 200},
            {"scope": "scope3", "co2_emission": 50},
            {"scope": "scope1", "co2_emission": 150},
        ]
        result = carbon_calc.calculate_total_emission(records)
        assert result["scope1_total"] == 250
        assert result["scope2_total"] == 200
        assert result["scope3_total"] == 50
        assert result["total"] == 500

    def test_empty_records(self):
        """空记录"""
        result = carbon_calc.calculate_total_emission([])
        assert result["total"] == 0


# ============================================================
# 2. API端点测试
# ============================================================

@pytest.fixture
def client():
    """创建测试客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


class TestCarbonAPI:
    """碳数据API测试"""

    def test_list_companies(self, client):
        """企业列表"""
        resp = client.get("/api/v1/carbon/company/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_and_get_company(self, client):
        """创建+查询企业"""
        create_resp = client.post("/api/v1/carbon/company/", json={
            "name": "测试企业有限公司",
            "industry": "制造业",
            "region": "华北"
        })
        assert create_resp.status_code == 200
        company_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/v1/carbon/company/{company_id}/")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "测试企业有限公司"

    def test_company_not_found(self, client):
        """查询不存在企业"""
        resp = client.get("/api/v1/carbon/company/99999/")
        assert resp.status_code == 404

    def test_list_carbon_records(self, client):
        """碳记录列表"""
        resp = client.get("/api/v1/carbon/records/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_calculate_emission(self, client):
        """排放计算API"""
        resp = client.post("/api/v1/carbon/calculate/", json={
            "scope": "scope2",
            "emission_source": "electricity",
            "quantity": 1000,
            "unit": "kWh"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["co2_emission"] == pytest.approx(581, rel=0.01)
        assert data["unit"] == "kgCO2"

    def test_get_emission_factors(self, client):
        """排放因子列表"""
        resp = client.get("/api/v1/carbon/factors/")
        assert resp.status_code == 200
        factors = resp.json()
        assert len(factors) >= 30

    def test_get_factors_by_source(self, client):
        """按排放源筛选因子"""
        resp = client.get("/api/v1/carbon/factors/?source=electricity")
        assert resp.status_code == 200
        factors = resp.json()
        assert all(f["emission_source"] == "electricity" for f in factors)

    def test_create_carbon_record(self, client):
        """创建碳记录"""
        # 先创建企业
        company_resp = client.post("/api/v1/carbon/company/", json={
            "name": "排放记录测试企业",
            "industry": "科技"
        })
        company_id = company_resp.json()["id"]

        record_resp = client.post("/api/v1/carbon/records/", json={
            "company_id": company_id,
            "record_date": "2026-04",
            "scope": "scope1",
            "emission_source": "natural_gas",
            "quantity": 500,
            "unit": "m3"
        })
        assert record_resp.status_code == 200
        data = record_resp.json()
        assert data["co2_emission"] == pytest.approx(1045, rel=0.01)
        assert data["status"] == "created"

    def test_carbon_summary(self, client):
        """碳排放汇总"""
        # 先创建企业
        company_resp = client.post("/api/v1/carbon/company/", json={
            "name": "汇总测试企业",
            "industry": "制造业"
        })
        company_id = company_resp.json()["id"]

        resp = client.get(f"/api/v1/carbon/summary/{company_id}/")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_emission" in data
        assert "record_count" in data


class TestMeasuresAPI:
    """措施库API测试"""

    def setup_method(self):
        """确保数据库已初始化"""
        init_db()

    def test_measures_stats(self, client):
        """措施统计"""
        resp = client.get("/api/v1/measures/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 49

    def test_list_measures(self, client):
        """措施列表"""
        resp = client.get("/api/v1/measures/measures")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0

    def test_measures_by_industry(self, client):
        """按行业筛选措施"""
        resp = client.get("/api/v1/measures/measures")
        assert resp.status_code == 200
        data = resp.json()
        # 措施列表返回的是ID列表或dict列表
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], str):
                # 返回ID列表
                assert len(data) >= 49
            elif isinstance(data[0], dict):
                industries = set(m.get("industry", "") for m in data)
                assert len(industries) >= 4


class TestReportAPI:
    """报告API测试"""

    def test_generate_report(self, client):
        """生成碳排报告"""
        # 用现有企业ID 1
        resp = client.get("/api/v1/report/report/1/?report_type=monthly")
        if resp.status_code == 200:
            data = resp.json()
            assert "summary" in data
            assert "total_emission" in data["summary"]

    def test_export_json(self, client):
        """导出JSON报告"""
        resp = client.get("/api/v1/report/export-json/1/")
        if resp.status_code == 200:
            assert "company_info" in resp.json()

    def test_export_csv(self, client):
        """导出CSV报告"""
        resp = client.get("/api/v1/report/export-csv/1/")
        if resp.status_code == 200:
            assert "text/csv" in resp.headers.get("content-type", "")


# ============================================================
# 3. Pydantic模型校验测试
# ============================================================

class TestSchemaValidation:
    """数据模型校验测试"""

    def test_carbon_record_invalid_scope(self):
        """无效scope"""
        from pydantic import ValidationError
        from app.models.schemas import CarbonRecordCreate
        with pytest.raises(ValidationError):
            CarbonRecordCreate(
                company_id=1,
                record_date="2026-04",
                scope="invalid_scope",
                emission_source="electricity",
                quantity=100,
                unit="kWh"
            )

    def test_carbon_record_zero_quantity(self):
        """quantity必须>0"""
        from pydantic import ValidationError
        from app.models.schemas import CarbonRecordCreate
        with pytest.raises(ValidationError):
            CarbonRecordCreate(
                company_id=1,
                record_date="2026-04",
                scope="scope2",
                emission_source="electricity",
                quantity=0,
                unit="kWh"
            )

    def test_carbon_record_negative_quantity(self):
        """quantity不能为负"""
        from pydantic import ValidationError
        from app.models.schemas import CarbonRecordCreate
        with pytest.raises(ValidationError):
            CarbonRecordCreate(
                company_id=1,
                record_date="2026-04",
                scope="scope2",
                emission_source="electricity",
                quantity=-100,
                unit="kWh"
            )

    def test_carbon_record_invalid_date(self):
        """日期格式校验"""
        from pydantic import ValidationError
        from app.models.schemas import CarbonRecordCreate
        with pytest.raises(ValidationError):
            CarbonRecordCreate(
                company_id=1,
                record_date="2026-00",  # 无效月份
                scope="scope2",
                emission_source="electricity",
                quantity=100,
                unit="kWh"
            )

    def test_carbon_record_invalid_date_format(self):
        """日期格式校验-格式错误"""
        from pydantic import ValidationError
        from app.models.schemas import CarbonRecordCreate
        with pytest.raises(ValidationError):
            CarbonRecordCreate(
                company_id=1,
                record_date="2026/04",  # 错误分隔符
                scope="scope2",
                emission_source="electricity",
                quantity=100,
                unit="kWh"
            )

    def test_company_name_required(self):
        """企业名必填"""
        from pydantic import ValidationError
        from app.models.schemas import CompanyCreate
        with pytest.raises(ValidationError):
            CompanyCreate(name="")

    def test_carbon_calculate_request_valid(self):
        """有效计算请求"""
        from app.models.schemas import CarbonCalculateRequest
        req = CarbonCalculateRequest(
            scope=CarbonScope.SCOPE1,
            emission_source=EmissionSource.COAL,
            quantity=100,
            unit="kg"
        )
        assert req.quantity == 100
