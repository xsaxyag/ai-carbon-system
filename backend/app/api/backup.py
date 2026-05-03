"""
AI碳枢算 - 数据备份API
备份、恢复、导出、导入、统计
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.services import backup_service
from app.api.auth import require_auth

router = APIRouter()


class RestoreRequest(BaseModel):
    filename: str = Field(..., description="备份文件名")


class ImportRequest(BaseModel):
    data: dict = Field(..., description="JSON导出数据")


class CleanupRequest(BaseModel):
    keep_count: int = Field(10, ge=1, le=100, description="保留备份数量")


@router.post("/create", summary="创建备份")
async def create_backup(request: Request, note: Optional[str] = None, current_user: dict = Depends(require_auth)):
    """创建数据库备份"""
    try:
        result = backup_service.create_backup(note=note)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


@router.post("/restore", summary="恢复备份")
async def restore_backup(req: RestoreRequest, request: Request, current_user: dict = Depends(require_auth)):
    """从备份恢复数据库"""
    try:
        result = backup_service.restore_backup(req.filename)
        return {"success": True, "data": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@router.get("/list", summary="备份列表")
async def list_backups(request: Request, current_user: dict = Depends(require_auth)):
    """列出所有备份"""
    backups = backup_service.list_backups()
    return {"success": True, "data": backups, "count": len(backups)}


@router.delete("/{filename}", summary="删除备份")
async def delete_backup(filename: str, request: Request, current_user: dict = Depends(require_auth)):
    """删除指定备份"""
    deleted = backup_service.delete_backup(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="备份文件不存在")
    return {"success": True, "message": "备份已删除"}


@router.get("/stats", summary="数据库统计")
async def db_stats(request: Request, current_user: dict = Depends(require_auth)):
    """获取数据库统计信息"""
    stats = backup_service.get_db_stats()
    return {"success": True, "data": stats}


@router.get("/export", summary="导出全部数据")
async def export_data(request: Request, current_user: dict = Depends(require_auth)):
    """导出全部数据为JSON"""
    data = backup_service.export_all_json()
    return JSONResponse(content=data)


@router.post("/import", summary="导入数据")
async def import_data(req: ImportRequest, request: Request, current_user: dict = Depends(require_auth)):
    """从JSON导入数据"""
    try:
        result = backup_service.import_all_json(req.data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/cleanup", summary="清理旧备份")
async def cleanup_backups(req: CleanupRequest, request: Request, current_user: dict = Depends(require_auth)):
    """清理旧备份，保留最近N个"""
    result = backup_service.cleanup_old_backups(req.keep_count)
    return {"success": True, "data": result}
