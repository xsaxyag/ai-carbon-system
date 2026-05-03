"""
AI碳枢算 - 认证API
注册、登录、获取当前用户、修改密码
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from app.services import auth_service

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ========== 请求模型 ==========

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$', description="用户名（字母数字下划线）")
    password: str = Field(..., min_length=6, max_length=100, description="密码（至少6位）")
    company_name: str = Field(..., min_length=1, max_length=100, description="企业名称")
    industry: Optional[str] = Field(None, max_length=50, description="所属行业")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码（至少6位）")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ========== 认证依赖 ==========

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """从JWT令牌获取当前用户（可选认证，不强制）"""
    if credentials is None:
        return None
    payload = auth_service.decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="令牌格式错误")
    user = auth_service.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.get("is_active", 1):
        raise HTTPException(status_code=401, detail="用户已被禁用")
    return user


async def require_auth(current_user: dict = Depends(get_current_user)) -> dict:
    """强制认证依赖"""
    if current_user is None:
        raise HTTPException(status_code=401, detail="未登录")
    return current_user


# ========== API端点 ==========

@router.post("/register", summary="用户注册")
async def register(req: RegisterRequest, request: Request):
    """注册新用户"""
    try:
        user = auth_service.create_user(
            username=req.username,
            password=req.password,
            company_name=req.company_name,
            industry=req.industry
        )
        # 自动生成token
        token = auth_service.create_access_token(data={"sub": str(user["id"])})
        return {
            "success": True,
            "message": "注册成功",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "company_name": user["company_name"],
                    "industry": user["industry"],
                    "role": user["role"]
                }
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", summary="用户登录")
async def login(req: LoginRequest, request: Request):
    """用户登录"""
    user = auth_service.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = auth_service.create_access_token(data={"sub": str(user["id"])})

    return {
        "success": True,
        "message": "登录成功",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "company_name": user["company_name"],
                "industry": user["industry"],
                "role": user["role"]
            }
        }
    }


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_user: dict = Depends(require_auth)):
    """获取当前登录用户信息"""
    return {
        "success": True,
        "data": {
            "id": current_user["id"],
            "username": current_user["username"],
            "company_name": current_user["company_name"],
            "industry": current_user["industry"],
            "role": current_user["role"],
            "is_active": bool(current_user.get("is_active", 1)),
            "created_at": current_user.get("created_at")
        }
    }


@router.put("/change-password", summary="修改密码")
async def change_password(req: ChangePasswordRequest, current_user: dict = Depends(require_auth)):
    """修改当前用户密码"""
    # 验证旧密码
    if not auth_service.verify_password(req.old_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 更新密码
    success = auth_service.update_user_password(current_user["id"], req.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="密码更新失败")

    return {"success": True, "message": "密码修改成功"}


@router.get("/status", summary="认证状态检查")
async def auth_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """检查当前认证状态"""
    if credentials is None:
        return {"authenticated": False, "user": None}

    payload = auth_service.decode_access_token(credentials.credentials)
    if payload is None:
        return {"authenticated": False, "user": None}

    user_id = payload.get("sub")
    user = auth_service.get_user_by_id(int(user_id))
    if user is None:
        return {"authenticated": False, "user": None}

    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "company_name": user["company_name"],
            "role": user["role"]
        }
    }
