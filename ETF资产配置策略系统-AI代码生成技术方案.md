# ETF资产配置策略系统 - AI代码生成技术方案

> **文档目标**: 为AI代码生成器提供精确、完整、可执行的技术实施指南
> **适用对象**: 大模型驱动的Code Agent
> **输出要求**: 完整、可运行、生产级别的代码实现

## 📋 项目总览

### 🎯 项目定义
**项目名称**: ETF资产配置策略系统
**项目类型**: 对话式AI金融科技产品
**核心价值**: 通过智能对话生成个性化ETF投资策略
**技术特征**: 前后端分离 + AI驱动 + 实时交互

### 🏗️ 系统架构
```
┌─────────────────────────────────────────────────────────────┐
│                    ETF资产配置策略系统                        │
├─────────────────────────────────────────────────────────────┤
│  前端层 (React + TypeScript)                               │
│  ├── 用户认证模块 (登录/注册)                                │
│  ├── 对话交互模块 (WebSocket实时通信)                        │
│  ├── 策略展示模块 (自研图表组件)                             │
│  └── 历史管理模块 (策略CRUD)                                │
├─────────────────────────────────────────────────────────────┤
│  后端层 (Python + FastAPI)                                 │
│  ├── 用户认证服务 (JWT + 手机号验证)                         │
│  ├── 智能体核心服务 (LangChain + LangGraph)                  │
│  ├── 对话管理服务 (WebSocket + 状态管理)                     │
│  ├── 策略引擎服务 (策略生成 + 回测)                          │
│  ├── 数据服务层 (Wind数据 + 新闻API)                         │
│  ├── 内容安全审查 (敏感内容过滤)                             │
│  └── 缓存服务 (Redis)                                       │
├─────────────────────────────────────────────────────────────┤
│  数据层                                                     │
│  ├── MySQL数据库 (结构化数据存储)                            │
│  ├── 文件存储 (配置文件 + 用户档案)                          │
│  └── Redis缓存 (会话 + 数据缓存)                             │
├─────────────────────────────────────────────────────────────┤
│  外部服务                                                   │
│  ├── Wind数据库 (ETF数据源)                                  │
│  ├── 新闻API (市场资讯)                                      │
│  └── 本地大模型 (LangChain集成)                              │
└─────────────────────────────────────────────────────────────┘
```

### 🎨 UI设计风格
- **设计理念**: 现代科技感金融产品界面
- **主色调**: #1890FF (科技蓝)
- **设计风格**: 简洁大气、科技感、互联网风格
- **交互特征**: 渐变效果、微动画、毛玻璃效果

## 🛠️ 技术栈规范

### 前端技术栈
```yaml
runtime:
  framework: "React 18.2.0"
  language: "TypeScript 5.0+"
  build_tool: "Vite 4.0+"
  
state_management:
  core: "Redux Toolkit 1.9+"
  middleware: "Redux-Thunk"
  api_cache: "自研API缓存管理器"
  
ui_framework:
  components: "自研组件库"
  styling: "CSS Modules + 原生CSS"
  charts: "自研图表组件 (Canvas + SVG)"
  icons: "自研SVG图标库"
  
routing:
  library: "React Router v6"
  
networking:
  http: "axios 1.4+"
  websocket: "原生WebSocket API"
  
development:
  linting: "ESLint + Prettier"
  testing: "Jest + React Testing Library"
```

### 后端技术栈
```yaml
runtime:
  language: "Python 3.11+"
  framework: "FastAPI 0.100+"
  
ai_framework:
  core: "LangChain 0.1+"
  orchestration: "LangGraph"
  tools: "自定义LangChain Tools"
  
database:
  primary: "MySQL 8.0+"
  orm: "SQLAlchemy 2.0+"
  migrations: "Alembic"
  cache: "Redis 7.0+"
  
async_processing:
  task_queue: "Celery 5.3+"
  message_broker: "Redis"
  
data_processing:
  scientific: "pandas 2.0+ + numpy 1.24+"
  database_connector: "pyodbc (Wind数据)"
  http_client: "httpx 0.24+"
  
development:
  validation: "Pydantic 2.0+"
  testing: "pytest + pytest-asyncio"
  linting: "black + isort + mypy"
```

### 部署技术栈
```yaml
containerization:
  engine: "Docker + Docker Compose"
  
reverse_proxy:
  server: "Nginx"
  
monitoring:
  logging: "Python logging + 文件轮转"
  
security:
  authentication: "JWT"
  password_hashing: "bcrypt"
  input_validation: "Pydantic"
```

## 📁 项目结构规范

### 完整目录结构
```
etf-strategy-system/
├── README.md                          # 项目说明文档
├── docker-compose.yml                 # Docker编排配置
├── .env.example                       # 环境变量示例
├── .gitignore                         # Git忽略文件
├── 
├── frontend/                          # 前端项目目录
│   ├── package.json                   # 依赖管理
│   ├── tsconfig.json                  # TypeScript配置
│   ├── vite.config.ts                 # Vite构建配置
│   ├── index.html                     # HTML入口文件
│   ├── .env.example                   # 前端环境变量
│   ├── 
│   ├── public/                        # 静态资源
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── 
│   ├── src/                           # 源代码目录
│   │   ├── main.tsx                   # 应用入口
│   │   ├── App.tsx                    # 根组件
│   │   ├── 
│   │   ├── types/                     # TypeScript类型定义
│   │   │   ├── index.ts               # 通用类型
│   │   │   ├── api.ts                 # API相关类型
│   │   │   ├── user.ts                # 用户相关类型
│   │   │   ├── strategy.ts            # 策略相关类型
│   │   │   └── conversation.ts        # 对话相关类型
│   │   ├── 
│   │   ├── store/                     # Redux状态管理
│   │   │   ├── index.ts               # Store配置
│   │   │   ├── authSlice.ts           # 用户认证状态
│   │   │   ├── conversationSlice.ts   # 对话状态
│   │   │   └── strategySlice.ts       # 策略状态
│   │   ├── 
│   │   ├── services/                  # 服务层
│   │   │   ├── api.ts                 # HTTP API服务
│   │   │   ├── websocket.ts           # WebSocket服务
│   │   │   └── cache.ts               # 自研API缓存
│   │   ├── 
│   │   ├── components/                # 通用组件
│   │   │   ├── ui/                    # 基础UI组件
│   │   │   │   ├── Button/
│   │   │   │   │   ├── index.tsx
│   │   │   │   │   └── Button.module.css
│   │   │   │   ├── Input/
│   │   │   │   ├── Card/
│   │   │   │   ├── Modal/
│   │   │   │   └── Table/
│   │   │   ├── 
│   │   │   ├── charts/                # 自研图表组件
│   │   │   │   ├── PieChart/
│   │   │   │   │   ├── index.tsx
│   │   │   │   │   └── PieChart.module.css
│   │   │   │   ├── LineChart/
│   │   │   │   └── MetricCard/
│   │   │   ├── 
│   │   │   ├── business/              # 业务组件
│   │   │   │   ├── ConversationPanel/
│   │   │   │   ├── StrategyDisplay/
│   │   │   │   └── StrategyHistory/
│   │   │   └── 
│   │   │   └── layout/                # 布局组件
│   │   │       ├── Header/
│   │   │       ├── Sidebar/
│   │   │       └── Layout/
│   │   ├── 
│   │   ├── pages/                     # 页面组件
│   │   │   ├── LoginPage/
│   │   │   ├── RegisterPage/
│   │   │   └── MainPage/
│   │   ├── 
│   │   ├── hooks/                     # 自定义Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useStrategy.ts
│   │   │   └── useConversation.ts
│   │   ├── 
│   │   ├── utils/                     # 工具函数
│   │   │   ├── format.ts              # 格式化工具
│   │   │   ├── validation.ts          # 验证工具
│   │   │   └── constants.ts           # 常量定义
│   │   ├── 
│   │   └── styles/                    # 全局样式
│   │       ├── global.css             # 全局样式
│   │       ├── variables.css          # CSS变量
│   │       └── themes.css             # 主题样式
│   ├── 
│   ├── Dockerfile                     # 前端Docker配置
│   └── nginx.conf                     # Nginx配置
├── 
├── backend/                           # 后端项目目录
│   ├── requirements.txt               # Python依赖
│   ├── pyproject.toml                 # 项目配置
│   ├── main.py                        # FastAPI应用入口
│   ├── .env.example                   # 后端环境变量
│   ├── 
│   ├── config/                        # 配置文件
│   │   ├── settings.py                # 应用配置
│   │   ├── database.py                # 数据库配置
│   │   ├── redis.py                   # Redis配置
│   │   └── logging.py                 # 日志配置
│   ├── 
│   ├── app/                           # 应用代码目录
│   │   ├── __init__.py
│   │   ├── 
│   │   ├── core/                      # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # 数据库连接
│   │   │   ├── security.py            # 安全工具
│   │   │   ├── dependencies.py        # 依赖注入
│   │   │   └── exceptions.py          # 异常处理
│   │   ├── 
│   │   ├── models/                    # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 基础模型
│   │   │   ├── user.py                # 用户模型
│   │   │   ├── strategy.py            # 策略模型
│   │   │   ├── conversation.py        # 对话模型
│   │   │   └── etf.py                 # ETF数据模型
│   │   ├── 
│   │   ├── schemas/                   # Pydantic模式
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # 用户模式
│   │   │   ├── strategy.py            # 策略模式
│   │   │   ├── conversation.py        # 对话模式
│   │   │   └── common.py              # 通用模式
│   │   ├── 
│   │   ├── api/                       # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证API
│   │   │   ├── conversation.py        # 对话API
│   │   │   ├── strategy.py            # 策略API
│   │   │   └── websocket.py           # WebSocket API
│   │   ├── 
│   │   ├── services/                  # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # 认证服务
│   │   │   ├── conversation_service.py # 对话服务
│   │   │   ├── strategy_service.py    # 策略服务
│   │   │   └── data_service.py        # 数据服务
│   │   ├── 
│   │   ├── agent/                     # 智能体模块
│   │   │   ├── __init__.py
│   │   │   ├── core.py                # 智能体核心
│   │   │   ├── workflow.py            # 工作流定义
│   │   │   ├── prompts.py             # 提示词模板
│   │   │   └── memory.py              # 记忆管理
│   │   ├── 
│   │   ├── tools/                     # LangChain工具
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py           # 工具基类
│   │   │   ├── user_identification.py # 用户识别工具
│   │   │   ├── element_extraction.py  # 要素提取工具
│   │   │   ├── strategy_generation.py # 策略生成工具
│   │   │   ├── etf_data_fetch.py      # ETF数据获取工具
│   │   │   ├── strategy_backtest.py   # 策略回测工具
│   │   │   ├── market_news_fetch.py   # 市场新闻获取工具
│   │   │   └── strategy_optimization.py # 策略优化工具
│   │   ├── 
│   │   ├── safety/                    # 内容安全审查
│   │   │   ├── __init__.py
│   │   │   ├── content_checker.py     # 内容检查器
│   │   │   ├── keyword_filter.py      # 关键词过滤
│   │   │   ├── compliance_manager.py  # 合规管理
│   │   │   └── audit_logger.py        # 审查日志
│   │   ├── 
│   │   ├── data/                      # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── wind_client.py         # Wind数据客户端
│   │   │   ├── news_client.py         # 新闻API客户端
│   │   │   └── etf_repository.py      # ETF数据仓库
│   │   ├── 
│   │   ├── cache/                     # 缓存服务
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py        # Redis客户端
│   │   │   └── cache_manager.py       # 缓存管理
│   │   ├── 
│   │   ├── tasks/                     # 异步任务
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py          # Celery应用
│   │   │   ├── strategy_tasks.py      # 策略相关任务
│   │   │   └── data_tasks.py          # 数据相关任务
│   │   ├── 
│   │   └── utils/                     # 工具模块
│   │       ├── __init__.py
│   │       ├── logger.py              # 日志工具
│   │       ├── validators.py          # 验证工具
│   │       └── formatters.py          # 格式化工具
│   ├── 
│   ├── alembic/                       # 数据库迁移
│   │   ├── versions/                  # 迁移版本
│   │   ├── env.py                     # 迁移环境
│   │   └── script.py.mako             # 迁移模板
│   ├── 
│   ├── tests/                         # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py                # 测试配置
│   │   ├── test_auth.py               # 认证测试
│   │   ├── test_strategy.py           # 策略测试
│   │   └── test_agent.py              # 智能体测试
│   ├── 
│   ├── data/                          # 数据文件
│   │   ├── business_config/           # 业务配置
│   │   │   ├── business_flows.yaml    # 业务流程配置
│   │   │   ├── prompt_templates.yaml  # 提示词模板
│   │   │   └── strategy_templates.yaml # 策略模板
│   │   ├── 
│   │   ├── safety_config/             # 安全配置
│   │   │   ├── content_safety.yaml    # 内容安全配置
│   │   │   ├── keywords/              # 敏感词库
│   │   │   │   ├── political.txt
│   │   │   │   ├── nsfw.txt
│   │   │   │   └── financial_violations.txt
│   │   │   └── compliance_templates/  # 合规模板
│   │   │       ├── risk_warnings.yaml
│   │   │       └── disclaimers.yaml
│   │   ├── 
│   │   ├── user_data/                 # 用户数据文件
│   │   │   ├── profiles/              # 用户档案
│   │   │   └── sessions/              # 会话数据
│   │   └── 
│   │   └── knowledge_base/            # 知识库文件
│   │       ├── etf_categories.json    # ETF分类
│   │       ├── investment_concepts.json # 投资概念
│   │       └── risk_profiles.json     # 风险档案
│   ├── 
│   ├── Dockerfile                     # 后端Docker配置
│   └── alembic.ini                    # Alembic配置
├── 
├── scripts/                           # 部署脚本
│   ├── start.sh                       # Linux启动脚本
│   ├── start.bat                      # Windows启动脚本
│   ├── init_db.py                     # 数据库初始化
│   └── deploy.sh                      # 部署脚本
└── 
└── docs/                              # 文档目录
    ├── api/                           # API文档
    ├── deployment/                    # 部署文档
    └── development/                   # 开发文档
```

## 🔧 核心功能实现规范

### 1. 用户认证系统

#### 数据库模型
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### API接口规范
```python
# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, auth_service: AuthService = Depends()):
    """用户注册接口"""
    pass

@router.post("/login")
async def login(credentials: UserLogin, auth_service: AuthService = Depends()):
    """用户登录接口"""
    pass

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出接口"""
    pass
```

#### 前端认证组件
```typescript
// src/components/auth/LoginForm.tsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { loginUser } from '../../store/authSlice';
import Button from '../ui/Button';
import Input from '../ui/Input';
import styles from './LoginForm.module.css';

interface LoginFormProps {
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await dispatch(loginUser({ phone, password })).unwrap();
      onSuccess?.();
    } catch (error) {
      // 错误处理
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={styles.loginForm} onSubmit={handleSubmit}>
      <Input
        type="tel"
        placeholder="请输入手机号"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        required
      />
      <Input
        type="password"
        placeholder="请输入密码"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <Button type="submit" loading={loading} variant="primary">
        登录
      </Button>
    </form>
  );
};

export default LoginForm;
```

### 2. 智能体核心系统

#### LangChain工具定义
```python
# app/tools/base_tool.py
from typing import Any, Dict, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel
from app.core.database import get_db

class BaseETFTool(BaseTool):
    """ETF系统工具基类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = get_db()
    
    def _run(self, *args, **kwargs) -> str:
        """同步执行"""
        raise NotImplementedError
    
    async def _arun(self, *args, **kwargs) -> str:
        """异步执行"""
        raise NotImplementedError
```

```python
# app/tools/user_identification.py
from app.tools.base_tool import BaseETFTool
from app.models.user import User
from app.models.strategy import Strategy

class UserIdentificationTool(BaseETFTool):
    name = "user_identification"
    description = "识别用户类型（新用户/老用户）并获取用户信息"
    
    def _run(self, user_id: int) -> str:
        """识别用户类型"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return "用户不存在"
        
        # 检查用户是否有保存的策略
        strategy_count = self.db.query(Strategy).filter(
            Strategy.user_id == user_id
        ).count()
        
        user_type = "老用户" if strategy_count > 0 else "新用户"
        
        return f"用户类型: {user_type}, 历史策略数量: {strategy_count}"
```

#### 智能体工作流
```python
# app/agent/workflow.py
from langgraph import StateGraph, END
from typing import Dict, Any
from app.agent.core import AgentState
from app.tools import get_all_tools

def create_agent_workflow():
    """创建智能体工作流"""
    
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("user_identification", user_identification_node)
    workflow.add_node("element_extraction", element_extraction_node)
    workflow.add_node("strategy_generation", strategy_generation_node)
    workflow.add_node("content_safety_check", content_safety_check_node)
    
    # 设置入口点
    workflow.set_entry_point("user_identification")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "user_identification",
        should_extract_elements,
        {
            "extract": "element_extraction",
            "end": END
        }
    )
    
    # 编译工作流
    return workflow.compile()

async def user_identification_node(state: AgentState) -> Dict[str, Any]:
    """用户识别节点"""
    # 实现用户识别逻辑
    pass

async def element_extraction_node(state: AgentState) -> Dict[str, Any]:
    """要素提取节点"""
    # 实现要素提取逻辑
    pass
```

### 3. WebSocket实时通信

#### 后端WebSocket管理器
```python
# app/services/websocket_manager.py
from typing import List, Dict
from fastapi import WebSocket
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def send_status_update(self, user_id: int, status: str, data: Dict = None):
        message = {
            "type": "status_update",
            "status": status,
            "data": data or {}
        }
        await self.send_personal_message(json.dumps(message), user_id)

manager = ConnectionManager()
```

#### 前端WebSocket Hook
```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

interface WebSocketMessage {
  type: string;
  status?: string;
  data?: any;
}

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const { token } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (!token) return;

    const wsUrl = `ws://localhost:8000/ws?token=${token}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLastMessage(message);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [token]);

  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, lastMessage, sendMessage };
};
```

### 4. 自研UI组件系统

#### 按钮组件
```typescript
// src/components/ui/Button/index.tsx
import React, { ButtonHTMLAttributes } from 'react';
import classNames from 'classnames';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'text';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  icon?: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  icon,
  children,
  className,
  disabled,
  ...props
}) => {
  const buttonClass = classNames(
    styles.button,
    styles[variant],
    styles[size],
    {
      [styles.loading]: loading,
      [styles.disabled]: disabled || loading,
    },
    className
  );

  return (
    <button
      className={buttonClass}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className={styles.spinner} />}
      {icon && <span className={styles.icon}>{icon}</span>}
      {children}
    </button>
  );
};

export default Button;
```

```css
/* src/components/ui/Button/Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--border-radius-medium);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
  position: relative;
  overflow: hidden;
}

.primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  box-shadow: var(--shadow-light);
}

.primary:hover:not(.disabled) {
  background: linear-gradient(135deg, var(--primary-hover), var(--primary-color));
  box-shadow: var(--shadow-medium);
  transform: translateY(-1px);
}

.secondary {
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.secondary:hover:not(.disabled) {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-light);
}

.small {
  padding: 6px 12px;
  font-size: var(--font-size-sm);
}

.medium {
  padding: 8px 16px;
  font-size: var(--font-size-base);
}

.large {
  padding: 12px 24px;
  font-size: var(--font-size-lg);
}

.loading {
  pointer-events: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.icon {
  margin-right: 4px;
}
```

#### 自研图表组件
```typescript
// src/components/charts/PieChart/index.tsx
import React, { useEffect, useRef } from 'react';
import styles from './PieChart.module.css';

interface PieChartData {
  label: string;
  value: number;
  color: string;
}

interface PieChartProps {
  data: PieChartData[];
  width?: number;
  height?: number;
  showLabels?: boolean;
  showLegend?: boolean;
}

const PieChart: React.FC<PieChartProps> = ({
  data,
  width = 300,
  height = 300,
  showLabels = true,
  showLegend = true,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 计算总值
    const total = data.reduce((sum, item) => sum + item.value, 0);
    if (total === 0) return;

    // 绘制饼图
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 20;

    let startAngle = -Math.PI / 2;

    data.forEach((item, index) => {
      const sliceAngle = (item.value / total) * 2 * Math.PI;

      // 绘制扇形
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();

      // 创建渐变
      const gradient = ctx.createRadialGradient(
        centerX, centerY, 0,
        centerX, centerY, radius
      );
      gradient.addColorStop(0, item.color);
      gradient.addColorStop(1, adjustBrightness(item.color, -20));

      ctx.fillStyle = gradient;
      ctx.fill();

      // 绘制边框
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // 绘制标签
      if (showLabels && item.value / total > 0.05) {
        const labelAngle = startAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
        const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);

        ctx.fillStyle = '#ffffff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${((item.value / total) * 100).toFixed(1)}%`, labelX, labelY);
      }

      startAngle += sliceAngle;
    });
  }, [data, width, height, showLabels]);

  // 调整颜色亮度的辅助函数
  const adjustBrightness = (color: string, amount: number): string => {
    // 简单的颜色亮度调整实现
    return color; // 实际实现需要解析颜色并调整亮度
  };

  return (
    <div className={styles.pieChartContainer}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className={styles.canvas}
      />
      {showLegend && (
        <div className={styles.legend}>
          {data.map((item, index) => (
            <div key={index} className={styles.legendItem}>
              <div
                className={styles.legendColor}
                style={{ backgroundColor: item.color }}
              />
              <span className={styles.legendLabel}>{item.label}</span>
              <span className={styles.legendValue}>{item.value.toFixed(2)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PieChart;
```

### 5. 内容安全审查系统

#### 安全审查核心
```python
# app/safety/content_checker.py
import re
from typing import Dict, List, Any
import yaml
from pathlib import Path

class ContentSafetyChecker:
    def __init__(self):
        self.config = self._load_config()
        self.blocked_keywords = self._load_keywords()
    
    def _load_config(self) -> Dict:
        config_path = Path("data/safety_config/content_safety.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        keywords = {}
        keywords_dir = Path("data/safety_config/keywords")
        
        for keyword_file in keywords_dir.glob("*.txt"):
            category = keyword_file.stem
            with open(keyword_file, 'r', encoding='utf-8') as f:
                keywords[category] = [line.strip() for line in f if line.strip()]
        
        return keywords
    
    def check_content_safety(self, content: str, content_type: str = "general") -> Dict[str, Any]:
        """检查内容安全性"""
        violations = []
        risk_level = "low"
        
        # 1. 关键词检查
        for category, keywords in self.blocked_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    violations.append({
                        "type": "keyword_violation",
                        "category": category,
                        "keyword": keyword,
                        "severity": self.config["keyword_filters"][category]["severity"]
                    })
        
        # 2. 投资建议合规性检查
        if content_type == "investment_advice":
            compliance_violations = self._check_investment_compliance(content)
            violations.extend(compliance_violations)
        
        # 3. 确定风险等级
        if violations:
            severity_levels = [v.get("severity", "low") for v in violations]
            if "high" in severity_levels:
                risk_level = "high"
            elif "medium" in severity_levels:
                risk_level = "medium"
        
        # 4. 生成处理后的内容
        processed_content = self._process_content(content, violations, content_type)
        
        return {
            "is_safe": len(violations) == 0,
            "risk_level": risk_level,
            "violations": violations,
            "processed_content": processed_content,
            "suggestions": self._generate_suggestions(violations)
        }
    
    def _check_investment_compliance(self, content: str) -> List[Dict]:
        """检查投资建议合规性"""
        violations = []
        
        # 检查保证性表述
        guarantee_patterns = ["保证", "一定", "必然", "稳赚", "无风险"]
        for pattern in guarantee_patterns:
            if pattern in content:
                violations.append({
                    "type": "compliance_violation",
                    "category": "guarantee_statement",
                    "pattern": pattern,
                    "severity": "high"
                })
        
        # 检查风险提示
        if "风险" not in content and "谨慎" not in content:
            violations.append({
                "type": "compliance_violation",
                "category": "missing_risk_warning",
                "severity": "medium"
            })
        
        return violations
    
    def _process_content(self, content: str, violations: List[Dict], content_type: str) -> str:
        """处理内容，添加合规声明"""
        processed = content
        
        # 添加风险提示
        if content_type == "investment_advice":
            risk_warning = "【风险提示】投资有风险，入市需谨慎。"
            processed = f"{risk_warning}\n\n{processed}"
        
        # 添加免责声明
        if content_type in ["investment_advice", "strategy_recommendation"]:
            disclaimer = (
                "\n\n【免责声明】本内容仅为投资策略建议，不构成具体的投资推荐。"
                "历史业绩不代表未来表现，请根据自身风险承受能力谨慎决策。"
            )
            processed += disclaimer
        
        return processed
    
    def _generate_suggestions(self, violations: List[Dict]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for violation in violations:
            if violation["type"] == "keyword_violation":
                suggestions.append(f"请避免使用敏感词汇：{violation['keyword']}")
            elif violation["category"] == "guarantee_statement":
                suggestions.append("请避免使用保证性表述，改用'可能'、'预期'等词汇")
            elif violation["category"] == "missing_risk_warning":
                suggestions.append("请添加适当的风险提示")
        
        return list(set(suggestions))
```

## 📊 数据库设计规范

### MySQL数据表设计
```sql
-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) COMMENT '昵称',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_phone_number (phone_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 策略表
CREATE TABLE user_strategies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    strategy_name VARCHAR(100) NOT NULL COMMENT '策略名称',
    strategy_description TEXT COMMENT '策略描述',
    investment_elements JSON COMMENT '投资要素(JSON格式)',
    etf_allocations JSON NOT NULL COMMENT 'ETF配置(JSON格式)',
    risk_level ENUM('conservative', 'moderate', 'aggressive') COMMENT '风险等级',
    expected_return DECIMAL(5,2) COMMENT '预期收益率',
    backtest_data JSON COMMENT '回测数据(JSON格式)',
    performance_metrics JSON COMMENT '绩效指标(JSON格式)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户策略表';

-- 对话记录表
CREATE TABLE user_conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(50) NOT NULL COMMENT '会话ID',
    conversation_summary TEXT COMMENT '对话摘要',
    extracted_elements JSON COMMENT '提取的投资要素',
    conversation_file_path VARCHAR(255) COMMENT '详细对话文件路径',
    strategy_id INT COMMENT '关联的策略ID',
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active' COMMENT '对话状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (strategy_id) REFERENCES user_strategies(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户对话表';

-- ETF基础信息表
CREATE TABLE etf_basic_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    etf_code VARCHAR(20) UNIQUE NOT NULL COMMENT 'ETF代码',
    etf_name VARCHAR(100) NOT NULL COMMENT 'ETF名称',
    etf_name_en VARCHAR(100) COMMENT 'ETF英文名称',
    fund_company VARCHAR(50) COMMENT '基金公司',
    benchmark_index VARCHAR(100) COMMENT '跟踪指数',
    investment_target TEXT COMMENT '投资目标描述',
    investment_scope TEXT COMMENT '投资范围描述',
    category VARCHAR(50) COMMENT 'ETF分类',
    sub_category VARCHAR(50) COMMENT 'ETF子分类',
    market VARCHAR(20) COMMENT '上市市场',
    currency VARCHAR(10) DEFAULT 'CNY' COMMENT '计价货币',
    management_fee DECIMAL(5,4) COMMENT '管理费率',
    custodian_fee DECIMAL(5,4) COMMENT '托管费率',
    listing_date DATE COMMENT '上市日期',
    fund_size DECIMAL(15,2) COMMENT '基金规模(万元)',
    tags JSON COMMENT '标签(JSON数组)',
    risk_level ENUM('low', 'medium', 'high') COMMENT '风险等级',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    data_source VARCHAR(50) DEFAULT 'Wind' COMMENT '数据来源',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    INDEX idx_etf_code (etf_code),
    INDEX idx_category (category),
    INDEX idx_listing_date (listing_date),
    FULLTEXT idx_name_search (etf_name, investment_target)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ETF基础信息表';

-- ETF价格数据表
CREATE TABLE etf_price_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    etf_code VARCHAR(20) NOT NULL COMMENT 'ETF代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(10,4) COMMENT '开盘价',
    high_price DECIMAL(10,4) COMMENT '最高价',
    low_price DECIMAL(10,4) COMMENT '最低价',
    close_price DECIMAL(10,4) NOT NULL COMMENT '收盘价',
    volume BIGINT COMMENT '成交量',
    turnover DECIMAL(15,2) COMMENT '成交额',
    price_change DECIMAL(10,4) COMMENT '价格变动',
    change_percent DECIMAL(8,4) COMMENT '涨跌幅(%)',
    nav DECIMAL(10,4) COMMENT '净值',
    nav_change_percent DECIMAL(8,4) COMMENT '净值涨跌幅(%)',
    premium_discount_rate DECIMAL(8,4) COMMENT '溢价折价率(%)',
    data_source VARCHAR(50) DEFAULT 'Wind' COMMENT '数据来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (etf_code) REFERENCES etf_basic_info(etf_code) ON DELETE CASCADE,
    UNIQUE KEY idx_code_date (etf_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_close_price (close_price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ETF价格数据表';

-- 金融新闻表
CREATE TABLE financial_news (
    id INT PRIMARY KEY AUTO_INCREMENT,
    news_id VARCHAR(50) UNIQUE NOT NULL COMMENT '新闻ID',
    title VARCHAR(200) NOT NULL COMMENT '新闻标题',
    content TEXT COMMENT '新闻内容',
    summary TEXT COMMENT '新闻摘要',
    source VARCHAR(50) COMMENT '新闻来源',
    author VARCHAR(50) COMMENT '作者',
    publish_time TIMESTAMP COMMENT '发布时间',
    category VARCHAR(50) COMMENT '新闻分类',
    tags JSON COMMENT '标签(JSON数组)',
    related_stocks JSON COMMENT '相关股票代码(JSON数组)',
    related_concepts JSON COMMENT '相关概念(JSON数组)',
    sentiment_score DECIMAL(3,2) COMMENT '情感得分(-1到1)',
    market_impact ENUM('positive', 'negative', 'neutral') COMMENT '市场影响',
    investment_implications TEXT COMMENT '投资启示',
    url VARCHAR(500) COMMENT '新闻链接',
    is_important BOOLEAN DEFAULT FALSE COMMENT '是否重要',
    data_source VARCHAR(50) COMMENT '数据来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_news_id (news_id),
    INDEX idx_publish_time (publish_time),
    INDEX idx_category (category),
    INDEX idx_sentiment_score (sentiment_score),
    FULLTEXT idx_content_search (title, content, summary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='金融新闻表';

-- 内容审查日志表
CREATE TABLE content_audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT COMMENT '用户ID',
    session_id VARCHAR(50) COMMENT '会话ID',
    content_type ENUM('input', 'output', 'generated') NOT NULL COMMENT '内容类型',
    original_content TEXT NOT NULL COMMENT '原始内容',
    processed_content TEXT COMMENT '处理后内容',
    safety_score DECIMAL(3,2) COMMENT '安全评分(0-1)',
    violation_types JSON COMMENT '违规类型(JSON数组)',
    action_taken VARCHAR(50) COMMENT '采取的措施',
    reviewer_id INT COMMENT '审查员ID(如果人工审查)',
    review_result ENUM('approved', 'rejected', 'modified') COMMENT '审查结果',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '审查时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_content_type (content_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='内容审查日志表';
```

## 🚀 部署配置规范

### Docker配置
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - etf-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://etf_user:etf_pass@mysql:3306/etf_db
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend/data:/app/data
    networks:
      - etf-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=etf_db
      - MYSQL_USER=etf_user
      - MYSQL_PASSWORD=etf_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    networks:
      - etf-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - etf-network

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=mysql+pymysql://etf_user:etf_pass@mysql:3306/etf_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend/data:/app/data
    networks:
      - etf-network

volumes:
  mysql_data:
  redis_data:

networks:
  etf-network:
    driver: bridge
```

## 📝 AI代码生成指导规范

### 代码生成优先级
1. **核心业务逻辑优先**: 用户认证 → 智能体对话 → 策略生成 → 数据展示
2. **前后端协调开发**: 确保API接口和前端调用一致
3. **数据库优先创建**: 先建立数据模型，再开发业务逻辑
4. **安全机制集成**: 在每个生成内容的环节集成安全审查
5. **测试代码同步**: 为每个模块生成对应的测试代码

### 代码质量要求
- **类型安全**: 前端使用TypeScript，后端使用Pydantic
- **错误处理**: 完善的异常处理和用户友好的错误信息
- **日志记录**: 关键操作和错误的详细日志
- **性能优化**: 数据库查询优化、缓存使用、异步处理
- **安全考虑**: 输入验证、SQL注入防护、XSS防护

### 文档和注释要求
- **函数文档**: 每个函数包含详细的docstring
- **类型注解**: 所有函数参数和返回值的类型注解
- **配置说明**: 详细的配置文件说明和环境变量文档
- **API文档**: 自动生成的API文档（FastAPI自带）
- **部署文档**: 完整的部署和运维文档

## 🎯 实施检查清单

### 开发阶段检查
- [ ] 项目结构按照规范创建
- [ ] 数据库表结构正确创建
- [ ] 前端组件系统完整实现
- [ ] 后端API接口功能完整
- [ ] 智能体工作流正常运行
- [ ] WebSocket实时通信正常
- [ ] 内容安全审查有效
- [ ] 用户认证系统安全
- [ ] 数据缓存机制有效
- [ ] 错误处理机制完善

### 测试阶段检查
- [ ] 单元测试覆盖率>80%
- [ ] 集成测试通过
- [ ] 前端组件测试通过
- [ ] API接口测试通过
- [ ] 数据库操作测试通过
- [ ] 安全测试通过
- [ ] 性能测试达标
- [ ] 兼容性测试通过

### 部署阶段检查
- [ ] Docker镜像构建成功
- [ ] 环境变量配置正确
- [ ] 数据库连接正常
- [ ] Redis缓存正常
- [ ] 外部API连接正常
- [ ] SSL证书配置（生产环境）
- [ ] 日志系统正常
- [ ] 监控系统正常

### 生产运行检查
- [ ] 系统性能监控正常
- [ ] 错误日志监控正常
- [ ] 数据备份机制正常
- [ ] 安全审查系统正常
- [ ] 用户体验良好
- [ ] 业务功能完整
- [ ] 数据准确性验证
- [ ] 系统稳定性验证

---

**注意**: 此技术方案专为AI代码生成器设计，包含了详细的实现规范和代码示例。AI代理应严格按照此方案生成完整、可运行的生产级代码。每个模块都应包含完整的实现、测试和文档。
