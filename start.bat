@echo off
echo ========================================
echo    Hello Vuln 靶场启动脚本 - Windows
echo ========================================

echo 检查Docker是否运行...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Docker，请先安装Docker Desktop
    pause
    exit /b 1
)

echo 正在启动靶场...
docker compose down
docker compose up --build

echo.
echo 如果启动成功，请在浏览器访问: http://localhost:5000
echo 按 Ctrl+C 停止服务
pause