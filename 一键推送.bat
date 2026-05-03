@echo off
chcp 65001 >nul
echo ========================================
echo   AI碳枢算 - 一键推送到 GitHub
echo ========================================
echo.
cd /d D:\ai-carbon-system
echo 正在添加修改...
git add .
echo 正在提交...
git commit -m "取消登录验证"
echo 正在推送...
git push github main
echo.
if %errorlevel%==0 (
    echo ✅ 推送成功！
    echo Netlify 会自动重新构建，1-2分钟后刷新页面即可
) else (
    echo ❌ 推送失败
)
echo.
pause
