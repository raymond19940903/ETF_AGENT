# ETF资产配置策略系统

基于LangChain和FastAPI的智能ETF资产配置策略系统，通过AI对话生成个性化投资策略。

## 功能特性

### 🤖 智能对话
- 基于LangChain的智能投顾助手
- 自然语言交互，理解用户投资需求
- 实时对话状态更新和中间结果展示
- WebSocket实时通信

### 📊 策略生成
- 基于用户偏好自动生成ETF配置策略
- 支持多种风险等级：保守、稳健、积极、激进
- 智能资产配置和权重分配
- 策略回测和绩效分析

### 💼 用户管理
- 手机号注册登录
- 新用户/老用户智能识别
- 策略历史管理
- 个人偏好学习

### 📈 数据服务
- Wind数据库集成
- 市场资讯获取
- ETF产品信息查询
- 历史价格数据分析

## 技术架构

### 后端技术栈
- **运行环境**: Python 3.11+
- **Web框架**: FastAPI
- **AI服务**: LangChain + LangGraph
- **数据库**: MySQL 8.0+
- **ORM框架**: SQLAlchemy + Alembic
- **缓存**: Redis
- **任务队列**: Celery + Redis

### 前端技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Redux Toolkit + RTK Query
- **UI组件**: Ant Design
- **图表库**: ECharts
- **构建工具**: Vite
- **样式**: Less + CSS Modules

### 数据服务
- **Wind数据库**: pyodbc + SQL Server
- **资讯API**: HTTP请求 + aiohttp
- **数据处理**: pandas + numpy

### 部署运维
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **监控**: 健康检查

## 项目结构

```
fintech_project/
├── backend/                 # 后端代码
│   ├── app/                # 应用代码
│   │   ├── auth/          # 用户认证模块
│   │   ├── agent/         # 智能体核心模块
│   │   ├── tools/         # LangChain工具模块
│   │   ├── conversation/  # 对话服务模块
│   │   ├── strategy/      # 策略引擎模块
│   │   ├── data/          # 数据服务模块
│   │   ├── cache/         # 缓存服务模块
│   │   ├── models/        # 数据模型
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心组件
│   │   └── utils/         # 工具函数
│   ├── config/            # 配置文件
│   ├── tests/             # 测试文件
│   ├── main.py           # 主程序入口
│   ├── requirements.txt  # Python依赖
│   └── Dockerfile        # Docker配置
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── store/         # Redux状态管理
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── utils/         # 工具函数
│   │   ├── types/         # TypeScript类型
│   │   └── styles/        # 样式文件
│   ├── public/            # 静态资源
│   ├── package.json       # 依赖配置
│   ├── vite.config.ts     # Vite配置
│   ├── nginx.conf         # Nginx配置
│   └── Dockerfile         # Docker配置
└── docker-compose.yml     # Docker Compose配置
```

## 快速开始

### 环境要求
- Node.js 16+
- Python 3.11+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose

### 使用Docker部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd fintech_project
```

2. 配置环境变量
```bash
# 复制并编辑配置文件
cp backend/config/settings.py.example backend/config/settings.py
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 本地开发

#### 后端开发
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000
```

#### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 配置说明

### 后端配置
编辑 `backend/config/settings.py` 文件：

```python
# 数据库配置
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/etf_strategy"

# Redis配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Wind数据库配置
WIND_DB_HOST = "your-wind-server-host"
WIND_DB_USER = "your-wind-username"
WIND_DB_PASSWORD = "your-wind-password"

# 大语言模型配置
LLM_MODEL_TYPE = "local"  # local, openai, qwen
LLM_API_BASE = "http://localhost:11434"  # Ollama地址

# 资讯API配置
NEWS_API_BASE_URL = "https://api.example-news.com"
NEWS_API_KEY = "your-news-api-key"
```

### 前端配置
编辑 `frontend/.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_HOST=localhost:8000
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/conversation/start` - 开始对话
- `WebSocket /api/conversation/ws/{session_id}` - 对话WebSocket
- `POST /api/strategy/save` - 保存策略
- `GET /api/strategy/history` - 获取策略历史

## 系统运作流程

### 新用户流程
1. 用户注册/登录
2. 系统介绍ETF策略
3. 对话收集投资偏好
4. 生成个性化策略
5. 展示策略详情
6. 用户确认保存

### 老用户流程
1. 用户登录
2. 展示历史最佳策略
3. 提供优化建议
4. 用户选择操作
5. 更新或生成新策略

## 注意事项

1. **Wind数据库**: 需要有效的Wind数据库访问权限
2. **大语言模型**: 需要配置本地LLM服务（如Ollama）或API密钥
3. **生产部署**: 请修改默认密钥和数据库密码
4. **资讯API**: 需要配置有效的财经资讯API

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请创建Issue或联系开发团队。
