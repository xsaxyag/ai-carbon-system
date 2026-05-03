# AI碳枢算 - OCR库安装脚本
# 网络不稳定时可手动运行: Install-OCR.ps1

Write-Host "开始安装OCR依赖..." -ForegroundColor Cyan

# 尝试安装cnocr (轻量,推荐)
try {
    Write-Host "[1/2] 安装cnocr (轻量级中文OCR)..." -ForegroundColor Yellow
    pip install cnocr -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 60
    Write-Host "cnocr安装成功!" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "cnocr安装失败: $_" -ForegroundColor Red
}

# cnocr失败则尝试EasyOCR
try {
    Write-Host "[2/2] 安装EasyOCR (完整功能)..." -ForegroundColor Yellow
    pip install easyocr -i https://pypi.tuna.tsinghua.edu.cn/simple
    Write-Host "EasyOCR安装成功!" -ForegroundColor Green
} catch {
    Write-Host "EasyOCR安装失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动在命令提示符下运行:" -ForegroundColor Yellow
    Write-Host "  pip install cnocr" -ForegroundColor White
    Write-Host "或" -ForegroundColor White
    Write-Host "  pip install easyocr" -ForegroundColor White
}