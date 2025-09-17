#!/bin/bash

# ETF资产配置策略系统启动脚本

echo "=== ETF资产配置策略系统启动脚本 ==="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "1. 检查配置文件..."

# 检查后端配置文件
if [ ! -f "backend/.env" ]; then
    echo "创建后端配置文件..."
    cp backend/env.example backend/.env
    echo "请编辑 backend/.env 文件，配置数据库和API密钥"
fi

# 检查前端配置文件
if [ ! -f "frontend/.env" ]; then
    echo "创建前端配置文件..."
    cp frontend/env.example frontend/.env
fi

echo "2. 启动服务..."

# 启动Docker服务
echo "启动Docker容器..."
docker-compose up -d

echo "3. 等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

echo "4. 服务访问地址："
echo "前端应用: http://localhost"
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"

echo "=== 启动完成 ==="
echo "如需查看日志，请运行: docker-compose logs -f"
echo "如需停止服务，请运行: docker-compose down"
