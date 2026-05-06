FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（OCR相关）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p uploads data

# Railway 使用 PORT 环境变量（Railway 自动设置）
# 不要设置默认值，让 Railway 自己决定端口
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
