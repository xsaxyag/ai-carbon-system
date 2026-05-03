"""
碳排放预警服务
支持：阈值预警、趋势预警、环比预警
"""
from app.database import get_db_connection
from typing import Optional, List
from datetime import datetime


class AlertService:
    """碳排放预警服务"""

    # 默认预警阈值（kgCO2/月）
    DEFAULT_THRESHOLDS = {
        "monthly_total": 10000,       # 月度总排放阈值
        "scope1_ratio": 0.5,          # scope1占比上限
        "scope2_ratio": 0.6,          # scope2占比上限
        "mom_increase": 0.2,          # 环比增长上限（20%）
        "yoy_increase": 0.3,          # 同比增长上限（30%）
    }

    @staticmethod
    def check_alerts(company_id: int, custom_thresholds: dict = None) -> dict:
        """
        检查企业碳排放预警
        
        Args:
            company_id: 企业ID
            custom_thresholds: 自定义阈值（覆盖默认值）
        
        Returns:
            {
                "company_id": int,
                "alert_count": int,
                "alerts": [...],
                "current_month": {...},
                "last_month": {...},
                "thresholds_used": {...}
            }
        """
        thresholds = {**AlertService.DEFAULT_THRESHOLDS, **(custom_thresholds or {})}
        alerts = []

        # 获取当前月份和上个月数据
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        last_month_date = now.replace(day=1)
        if last_month_date.month == 1:
            last_month_date = last_month_date.replace(year=last_month_date.year - 1, month=12)
        else:
            last_month_date = last_month_date.replace(month=last_month_date.month - 1)
        last_month = last_month_date.strftime("%Y-%m")

        current_data = AlertService._get_monthly_data(company_id, current_month)
        last_month_data = AlertService._get_monthly_data(company_id, last_month)

        # 1. 月度总排放超阈值
        if current_data["total"] > thresholds["monthly_total"]:
            alerts.append({
                "level": "danger",
                "type": "threshold",
                "message": f"当月碳排放总量 {current_data['total']:.1f} kgCO2 超过预警阈值 {thresholds['monthly_total']} kgCO2",
                "value": current_data["total"],
                "threshold": thresholds["monthly_total"],
                "exceeded_ratio": round(current_data["total"] / thresholds["monthly_total"] - 1, 4)
            })

        # 2. scope1占比过高
        if current_data["total"] > 0:
            scope1_ratio = current_data["scope1"] / current_data["total"]
            if scope1_ratio > thresholds["scope1_ratio"]:
                alerts.append({
                    "level": "warning",
                    "type": "scope1_ratio",
                    "message": f"范围1直接排放占比 {scope1_ratio:.1%} 超过预警线 {thresholds['scope1_ratio']:.1%}，建议关注直接减排措施",
                    "value": round(scope1_ratio, 4),
                    "threshold": thresholds["scope1_ratio"]
                })

        # 3. 环比增长预警
        if last_month_data["total"] > 0 and current_data["total"] > 0:
            mom_change = (current_data["total"] - last_month_data["total"]) / last_month_data["total"]
            if mom_change > thresholds["mom_increase"]:
                alerts.append({
                    "level": "warning",
                    "type": "mom_increase",
                    "message": f"碳排放环比增长 {mom_change:.1%}，超过预警线 {thresholds['mom_increase']:.1%}（上月 {last_month_data['total']:.1f} → 本月 {current_data['total']:.1f} kgCO2）",
                    "value": round(mom_change, 4),
                    "threshold": thresholds["mom_increase"],
                    "last_month": last_month_data["total"],
                    "current_month": current_data["total"]
                })
            elif mom_change < -thresholds["mom_increase"]:
                alerts.append({
                    "level": "info",
                    "type": "mom_decrease",
                    "message": f"碳排放环比下降 {abs(mom_change):.1%}，减排效果显著（上月 {last_month_data['total']:.1f} → 本月 {current_data['total']:.1f} kgCO2）",
                    "value": round(mom_change, 4)
                })

        # 4. 各范围分别环比
        for scope_name, scope_key in [("范围1", "scope1"), ("范围2", "scope2"), ("范围3", "scope3")]:
            if last_month_data[scope_key] > 0 and current_data[scope_key] > 0:
                scope_change = (current_data[scope_key] - last_month_data[scope_key]) / last_month_data[scope_key]
                if scope_change > 0.3:  # 单范围环比增长超30%
                    alerts.append({
                        "level": "info",
                        "type": f"{scope_key}_increase",
                        "message": f"{scope_name}排放环比增长 {scope_change:.1%}（{last_month_data[scope_key]:.1f} → {current_data[scope_key]:.1f} kgCO2）",
                        "value": round(scope_change, 4)
                    })

        # 5. 无数据预警
        if current_data["total"] == 0:
            alerts.append({
                "level": "info",
                "type": "no_data",
                "message": f"当月({current_month})暂无碳排放记录，请及时录入数据"
            })

        return {
            "company_id": company_id,
            "current_month": current_month,
            "alert_count": len(alerts),
            "danger_count": sum(1 for a in alerts if a["level"] == "danger"),
            "warning_count": sum(1 for a in alerts if a["level"] == "warning"),
            "info_count": sum(1 for a in alerts if a["level"] == "info"),
            "alerts": alerts,
            "current_month_data": current_data,
            "last_month_data": last_month_data,
            "thresholds_used": thresholds
        }

    @staticmethod
    def _get_monthly_data(company_id: int, month: str) -> dict:
        """获取指定月份的碳排放汇总"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT scope, SUM(co2_emission) as total
                FROM carbon_records
                WHERE company_id = ? AND record_date = ?
                GROUP BY scope
            """, (company_id, month))
            rows = cursor.fetchall()
            conn.close()

            result = {"scope1": 0, "scope2": 0, "scope3": 0, "total": 0}
            for row in rows:
                scope = row["scope"]
                total = row["total"] or 0
                if scope in result:
                    result[scope] = round(total, 4)
            result["total"] = round(result["scope1"] + result["scope2"] + result["scope3"], 4)
            return result
        except Exception:
            return {"scope1": 0, "scope2": 0, "scope3": 0, "total": 0}

    @staticmethod
    def set_company_thresholds(company_id: int, thresholds: dict) -> dict:
        """设置企业自定义预警阈值"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建预警阈值表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_thresholds (
                company_id INTEGER PRIMARY KEY,
                monthly_total REAL DEFAULT 10000,
                scope1_ratio REAL DEFAULT 0.5,
                scope2_ratio REAL DEFAULT 0.6,
                mom_increase REAL DEFAULT 0.2,
                yoy_increase REAL DEFAULT 0.3,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Upsert
        fields = []
        values = []
        for key in ["monthly_total", "scope1_ratio", "scope2_ratio", "mom_increase", "yoy_increase"]:
            if key in thresholds:
                fields.append(f"{key} = ?")
                values.append(thresholds[key])

        if fields:
            values.append(company_id)
            cursor.execute(
                f"INSERT OR REPLACE INTO alert_thresholds (company_id, {', '.join(k for k in thresholds.keys() if k in ['monthly_total','scope1_ratio','scope2_ratio','mom_increase','yoy_increase'])}, updated_at) "
                f"VALUES (?, {', '.join('?' for _ in fields)}, CURRENT_TIMESTAMP)",
                [company_id] + [thresholds[k] for k in ["monthly_total", "scope1_ratio", "scope2_ratio", "mom_increase", "yoy_increase"] if k in thresholds]
            )
            conn.commit()
        conn.close()

        return {"status": "updated", "company_id": company_id, "thresholds": thresholds}

    @staticmethod
    def get_company_thresholds(company_id: int) -> dict:
        """获取企业预警阈值"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alert_thresholds WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
        except Exception:
            pass
        return AlertService.DEFAULT_THRESHOLDS

    @staticmethod
    def get_alert_history(company_id: int, limit: int = 30) -> List[dict]:
        """获取预警历史记录"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    value REAL,
                    threshold REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            cursor.execute(
                "SELECT * FROM alert_history WHERE company_id = ? ORDER BY created_at DESC LIMIT ?",
                (company_id, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    def save_alerts(company_id: int, alert_result: dict) -> None:
        """保存预警记录到历史表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    value REAL,
                    threshold REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            for alert in alert_result.get("alerts", []):
                if alert["level"] in ("danger", "warning"):  # 只保存重要预警
                    cursor.execute("""
                        INSERT INTO alert_history (company_id, alert_type, alert_level, message, value, threshold)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        company_id,
                        alert["type"],
                        alert["level"],
                        alert["message"],
                        alert.get("value"),
                        alert.get("threshold")
                    ))
            conn.commit()
            conn.close()
        except Exception:
            pass
