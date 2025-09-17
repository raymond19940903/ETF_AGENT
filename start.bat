@echo off
rem ETF资产配置策略系统启动脚本 (Windows)

echo === ETF资产配置策略系统启动脚本 ===

rem 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo 1. 检查配置文件...

rem 检查后端配置文件
if not exist "backend\.env" (
    echo 创建后端配置文件...
    copy "backend\env.example" "backend\.env"
    echo 请编辑 backend\.env 文件，配置数据库和API密钥
)

rem 检查前端配置文件
if not exist "frontend\.env" (
    echo 创建前端配置文件...
    copy "frontend\env.example" "frontend\.env"
)

echo 2. 启动服务...

rem 启动Docker服务
echo 启动Docker容器...
docker-compose up -d

echo 3. 等待服务启动...
timeout /t 10 /nobreak >nul

rem 检查服务状态
echo 检查服务状态...
docker-compose ps

echo 4. 服务访问地址：
echo 前端应用: http://localhost
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs

echo === 启动完成 ===
echo 如需查看日志，请运行: docker-compose logs -f
echo 如需停止服务，请运行: docker-compose down

pause
