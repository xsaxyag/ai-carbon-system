"""
AI碳枢算 - 碳排放报告API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from datetime import datetime
from urllib.parse import quote
from app.database import get_db_connection
from app.services.pdf_report import generate_pdf_report
from app.services.excel_export import generate_excel_report

router = APIRouter()

@router.get("/report/{company_id}/")
async def generate_report(company_id: int, report_type: str = "monthly"):
    """
    生成碳排放报告
    
    Args:
        company_id: 企业ID
        report_type: 报告类型 (monthly/quarterly/annual)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取企业信息
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    company = cursor.fetchone()
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail="企业不存在")
    
    # 获取碳记录
    cursor.execute("""
        SELECT scope, emission_source, quantity, unit, co2_emission, record_date
        FROM carbon_records 
        WHERE company_id = ?
        ORDER BY record_date DESC
    """, (company_id,))
    records = cursor.fetchall()
    conn.close()
    
    # 汇总统计
    scope1_total = sum(r["co2_emission"] for r in records if r["scope"] == "scope1")
    scope2_total = sum(r["co2_emission"] for r in records if r["scope"] == "scope2")
    scope3_total = sum(r["co2_emission"] for r in records if r["scope"] == "scope3")
    
    # 按月统计
    monthly_data = {}
    for r in records:
        month = r["record_date"][:7]  # YYYY-MM
        if month not in monthly_data:
            monthly_data[month] = 0
        monthly_data[month] += r["co2_emission"]
    
    # 按排放源统计
    source_data = {}
    for r in records:
        source = r["emission_source"]
        if source not in source_data:
            source_data[source] = 0
        source_data[source] += r["co2_emission"]
    
    # 减排建议
    suggestions = []
    if scope2_total > 0:
        # 电力排放
        reduction_potential = scope2_total * 0.15
        suggestions.append({
            "type": "scope2",
            "title": "购买绿色电力",
            "potential": round(reduction_potential, 2),
            "description": "通过购买绿电可减少约15%的电力间接排放"
        })
    
    if source_data.get("electricity", 0) > 1000:
        suggestions.append({
            "type": "energy",
            "title": "能效提升",
            "potential": round(source_data["electricity"] * 0.1, 2),
            "description": "通过节能改造可减少约10%的电力消耗"
        })
    
    return {
        "company": dict(company),
        "report_type": report_type,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_emission": round(scope1_total + scope2_total + scope3_total, 4),
            "scope1": round(scope1_total, 4),
            "scope2": round(scope2_total, 4),
            "scope3": round(scope3_total, 4),
            "record_count": len(records)
        },
        "monthly_data": monthly_data,
        "source_data": source_data,
        "suggestions": suggestions
    }

@router.get("/export/{company_id}/")
async def export_report(company_id: int, format: str = "json"):
    """导出报告 (json/csv)"""
    # 获取报告数据
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cr.*, c.name as company_name
        FROM carbon_records cr
        JOIN companies c ON cr.company_id = c.id
        WHERE cr.company_id = ?
        ORDER BY cr.record_date DESC
    """, (company_id,))
    records = cursor.fetchall()
    conn.close()
    
    if format == "csv":
        # 生成CSV
        import csv
        import io
        
        output = io.StringIO()
        if records:
            fieldnames = records[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(dict(r))
        
        return {
            "format": "csv",
            "content": output.getvalue(),
            "filename": f"carbon_report_{company_id}.csv"
        }
    
    return {
        "format": "json",
        "records": [dict(r) for r in records]
    }


@router.get("/export-pdf/{company_id}/")
async def export_pdf_report(company_id: int, report_type: str = "monthly"):
    """导出PDF碳排报告"""
    # 获取报告数据
    report_data = await generate_report(company_id, report_type)
    
    try:
        pdf_bytes = generate_pdf_report(report_data)
        company_name = report_data.get("company", {}).get("name", "unknown")
        filename_ascii = f"carbon_report_{company_id}_{report_type}.pdf"
        filename_utf8 = quote(f"{company_name}_碳排放报告_{report_type}.pdf")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_ascii}\"; filename*=UTF-8''{filename_utf8}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成失败: {str(e)}")


@router.get("/compare/")
async def compare_companies(company_ids: str):
    """
    多企业碳排放对比
    
    Args:
        company_ids: 逗号分隔的企业ID列表，如 "1,2,3"
    """
    try:
        ids = [int(x.strip()) for x in company_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="company_ids 格式错误，应为逗号分隔的数字")
    
    if not ids:
        raise HTTPException(status_code=400, detail="未提供企业ID")
    if len(ids) > 20:
        raise HTTPException(status_code=400, detail="最多支持20家企业同时对比")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = []
    for cid in ids:
        cursor.execute("SELECT id, name, industry, region, employee_count FROM companies WHERE id = ?", (cid,))
        company = cursor.fetchone()
        if not company:
            conn.close()
            raise HTTPException(status_code=404, detail=f"企业ID {cid} 不存在")
        
        cursor.execute("""
            SELECT scope, emission_source, quantity, unit, co2_emission, record_date
            FROM carbon_records WHERE company_id = ?
        """, (cid,))
        records = cursor.fetchall()
        
        s1 = sum(r["co2_emission"] for r in records if r["scope"] == "scope1")
        s2 = sum(r["co2_emission"] for r in records if r["scope"] == "scope2")
        s3 = sum(r["co2_emission"] for r in records if r["scope"] == "scope3")
        total = s1 + s2 + s3
        emp = company["employee_count"] or 1
        
        # 按月统计
        monthly = {}
        for r in records:
            m = r["record_date"][:7]
            if m not in monthly:
                monthly[m] = {"scope1": 0, "scope2": 0, "scope3": 0, "total": 0}
            if r["scope"] == "scope1":
                monthly[m]["scope1"] += r["co2_emission"]
            elif r["scope"] == "scope2":
                monthly[m]["scope2"] += r["co2_emission"]
            elif r["scope"] == "scope3":
                monthly[m]["scope3"] += r["co2_emission"]
            monthly[m]["total"] += r["co2_emission"]
        
        # 按排放源统计
        source_data = {}
        for r in records:
            src = r["emission_source"]
            if src not in source_data:
                source_data[src] = 0
            source_data[src] += r["co2_emission"]
        
        result.append({
            "company_id": cid,
            "name": company["name"],
            "industry": company["industry"] or "未知",
            "region": company["region"] or "默认",
            "employee_count": emp,
            "total_emission": round(total, 2),
            "scope1": round(s1, 2),
            "scope2": round(s2, 2),
            "scope3": round(s3, 2),
            "intensity": round(total / emp, 2),  # 人均碳排放 (kgCO2/人)
            "record_count": len(records),
            "monthly": dict(sorted(monthly.items())),
            "source_data": {k: round(v, 2) for k, v in source_data.items()}
        })
    
    conn.close()
    
    # 排名
    ranked = sorted(result, key=lambda x: x["total_emission"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    
    return {
        "companies": ranked,
        "count": len(result),
        "generated_at": datetime.now().isoformat()
    }

@router.get("/export-excel/{company_id}/")
async def export_excel_report(company_id: int, report_type: str = "monthly"):
    """导出Excel碳排报告"""
    try:
        excel_bytes = generate_excel_report(company_id, report_type)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        conn.close()
        company_name = row["name"] if row else "unknown"
        filename_ascii = f"carbon_report_{company_id}_{report_type}.xlsx"
        filename_utf8 = quote(f"{company_name}_碳排放报告_{report_type}.xlsx")
        
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_ascii}\"; filename*=UTF-8''{filename_utf8}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel生成失败: {str(e)}")