#!/usr/bin/env bash
# ETF资产配置策略系统 - Cloud Agent 环境启动脚本
# 每次启动运行：拉起 Redis 与 MariaDB，并确保数据库与用户存在（幂等）。
set -euo pipefail

echo "==> 启动 Redis"
sudo service redis-server start || true

echo "==> 启动 MariaDB"
sudo service mariadb start || true

echo "==> 等待 MariaDB 就绪"
for _ in $(seq 1 30); do
  if sudo mariadb -e "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "==> 确保数据库与用户存在"
sudo mariadb <<'SQL'
CREATE DATABASE IF NOT EXISTS etf_strategy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'etf_user'@'localhost' IDENTIFIED BY 'etf_password';
CREATE USER IF NOT EXISTS 'etf_user'@'127.0.0.1' IDENTIFIED BY 'etf_password';
GRANT ALL PRIVILEGES ON etf_strategy.* TO 'etf_user'@'localhost';
GRANT ALL PRIVILEGES ON etf_strategy.* TO 'etf_user'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

echo "==> 服务已就绪 (Redis:6379, MariaDB:3306)"
