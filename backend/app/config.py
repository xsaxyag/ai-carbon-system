"""
AI碳枢算 - 全局配置
从 .env 文件加载配置，支持环境变量覆盖
"""
import os
import json
from pathlib import Path

# 项目根目录（backend/）
BASE_DIR = Path(__file__).resolve().parent.parent

def _load_env():
    """加载 .env 配置文件（key=value 格式）"""
    env_path = BASE_DIR / ".env"
    data = {}
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        data[key.strip()] = value.strip()
        except Exception:
            pass
    return data

_env = _load_env()

# ========== LLM 配置 ==========
LLM_API_KEY = os.getenv("LLM_API_KEY", _env.get("LLM_API_KEY", "sk-xxx"))
LLM_BASE_URL = os.getenv("LLM_BASE_URL", _env.get("LLM_BASE_URL", "https://api.deepseek.com/v1"))
LLM_MODEL = os.getenv("LLM_MODEL", _env.get("LLM_MODEL", "deepseek-chat"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", _env.get("LLM_MAX_TOKENS", 2048)))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", _env.get("LLM_TEMPERATURE", 0.7)))

# ========== 系统配置 ==========
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
DATABASE_PATH = str(BASE_DIR / "data" / "carbon_system.db")
