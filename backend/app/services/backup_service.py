"""
AI碳枢算 - 数据备份与恢复服务
支持SQLite数据库备份、恢复、导出、清理
"""
import sqlite3
import shutil
import json
import csv
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "carbon.db"
BACKUP_DIR = DB_PATH.parent / "backups"


def _ensure_backup_dir():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup(note: Optional[str] = None) -> dict:
    """创建数据库备份"""
    _ensure_backup_dir()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"carbon_backup_{timestamp}.db"
    backup_path = BACKUP_DIR / backup_filename

    # 使用SQLite在线备份API确保数据一致性
    source_conn = sqlite3.connect(str(DB_PATH))
    dest_conn = sqlite3.connect(str(backup_path))

    with dest_conn:
        source_conn.backup(dest_conn)

    dest_conn.close()
    source_conn.close()

    # 记录备份元数据
    meta = {
        "filename": backup_filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "size_bytes": backup_path.stat().st_size,
        "note": note
    }

    meta_path = BACKUP_DIR / f"carbon_backup_{timestamp}.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


def restore_backup(backup_filename: str) -> dict:
    """从备份恢复数据库"""
    backup_path = BACKUP_DIR / backup_filename
    if not backup_path.exists():
        raise FileNotFoundError(f"备份文件不存在: {backup_filename}")

    # 先备份当前数据库
    pre_restore_backup = create_backup(note="恢复前自动备份")

    # 替换当前数据库
    shutil.copy2(str(backup_path), str(DB_PATH))

    return {
        "restored_from": backup_filename,
        "pre_restore_backup": pre_restore_backup["filename"],
        "message": "数据库已恢复"
    }


def list_backups() -> list:
    """列出所有备份"""
    _ensure_backup_dir()
    backups = []
    for meta_file in sorted(BACKUP_DIR.glob("*.json"), reverse=True):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            # 验证对应db文件存在
            db_path = BACKUP_DIR / meta["filename"]
            meta["exists"] = db_path.exists()
            meta["size_mb"] = round(db_path.stat().st_size / 1024 / 1024, 2) if db_path.exists() else 0
            backups.append(meta)
        except Exception:
            continue
    return backups


def delete_backup(backup_filename: str) -> bool:
    """删除备份"""
    db_path = BACKUP_DIR / backup_filename
    meta_name = backup_filename.replace('.db', '.json')
    meta_path = BACKUP_DIR / meta_name

    deleted = False
    if db_path.exists():
        db_path.unlink()
        deleted = True
    if meta_path.exists():
        meta_path.unlink()
        deleted = True

    return deleted


def export_all_json() -> dict:
    """导出全部数据为JSON"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    result = {
        "export_time": datetime.now(timezone.utc).isoformat(),
        "tables": {}
    }

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        result["tables"][table] = {
            "count": len(rows),
            "data": [dict(row) for row in rows]
        }

    conn.close()
    return result


def import_all_json(data: dict) -> dict:
    """从JSON导入数据（清空后导入）"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    imported = {}

    for table_name, table_data in data.get("tables", {}).items():
        rows = table_data.get("data", [])
        if not rows:
            continue

        # 清空表
        cursor.execute(f"DELETE FROM {table_name}")

        # 获取列名
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_str = ", ".join(columns)

        for row in rows:
            values = [row.get(col) for col in columns]
            cursor.execute(f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})", values)

        imported[table_name] = len(rows)

    conn.commit()
    conn.close()

    return {
        "imported": imported,
        "total_tables": len(imported),
        "total_rows": sum(imported.values())
    }


def get_db_stats() -> dict:
    """获取数据库统计信息"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    stats = {
        "db_size_mb": round(DB_PATH.stat().st_size / 1024 / 1024, 2),
        "tables": {}
    }

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats["tables"][table] = count

    conn.close()
    return stats


def cleanup_old_backups(keep_count: int = 10) -> dict:
    """清理旧备份，保留最近N个"""
    backups = list_backups()
    if len(backups) <= keep_count:
        return {"deleted": 0, "kept": len(backups)}

    to_delete = backups[keep_count:]
    deleted = 0
    for backup in to_delete:
        if delete_backup(backup["filename"]):
            deleted += 1

    return {"deleted": deleted, "kept": keep_count}
