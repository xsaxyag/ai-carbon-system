"""
AI碳枢算 - 认证服务
JWT令牌 + bcrypt密码哈希
"""
import jwt
import sqlite3
import bcrypt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# JWT配置
SECRET_KEY = "ai-carbon-system-jwt-secret-key-2026"  # 生产环境应从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 数据库路径
DB_PATH = Path(__file__).resolve().parent.parent.parent / "carbon.db"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """密码哈希"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_by_username(username: str) -> Optional[dict]:
    """根据用户名获取用户"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """根据ID获取用户"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def create_user(username: str, password: str, company_name: str,
                industry: Optional[str] = None, role: str = "user") -> dict:
    """创建用户"""
    existing = get_user_by_username(username)
    if existing:
        raise ValueError(f"用户名 '{username}' 已存在")

    hashed_password = get_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, hashed_password, company_name, industry, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
    """, (username, hashed_password, company_name, industry, role, now, now))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "username": username,
        "company_name": company_name,
        "industry": industry,
        "role": role,
        "is_active": True,
        "created_at": now
    }


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """验证用户登录"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not user.get("is_active", 1):
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def update_user_password(user_id: int, new_password: str) -> bool:
    """更新用户密码"""
    hashed = get_password_hash(new_password)
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET hashed_password = ?, updated_at = ? WHERE id = ?",
                   (hashed, now, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
