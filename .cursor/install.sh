#!/usr/bin/env bash
# ETF资产配置策略系统 - Cloud Agent 环境安装脚本
# 幂等：可重复运行。安装系统依赖、Python 3.11 后端依赖与前端依赖。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> 安装系统依赖 (MariaDB / Redis / unixODBC / 构建工具)"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
  redis-server \
  mariadb-server \
  unixodbc \
  unixodbc-dev \
  build-essential \
  pkg-config \
  curl

echo "==> 安装 uv (Python 版本与依赖管理)"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

echo "==> 配置后端 (Python 3.11 虚拟环境 + 依赖)"
pushd backend >/dev/null
if [ ! -x .venv/bin/python ]; then
  uv venv --python 3.11 .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -r requirements.txt
[ -f .env ] || cp env.example .env
mkdir -p logs
deactivate
popd >/dev/null

echo "==> 配置前端 (npm 依赖)"
pushd frontend >/dev/null
npm install
[ -f .env ] || cp env.example .env
popd >/dev/null

echo "==> 安装完成"
