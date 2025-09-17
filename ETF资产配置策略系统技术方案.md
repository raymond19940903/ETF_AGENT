# ETF资产配置策略系统技术方案

## 1. 项目概述

### 1.1 项目背景
基于对话式AI的ETF资产配置策略系统，通过智能对话引导客户表达投资需求，自动提取关键要素，生成个性化ETF配置策略，并提供实时策略展示和优化建议。

### 1.2 核心功能
- 对话式策略引导与要素提取
- 智能ETF资产配置策略生成
- 实时策略展示与回测分析
- 策略优化建议与历史管理
- 客户身份识别与策略持久化

## 2. 系统架构设计

### 2.1 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   后端服务层     │    │   数据存储层     │
│                │    │                │    │                │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ 对话界面    │ │◄──►│ │ 对话服务    │ │◄──►│ │ 策略数据库  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ 策略展示    │ │◄──►│ │ 策略引擎    │ │◄──►│ │ ETF数据     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ 历史管理    │ │◄──►│ │ 要素提取    │ │◄──►│ │ 市场数据    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 技术栈选择

#### 2.2.1 前端技术栈
- **框架**: React 18 + TypeScript
  - MIT许可证，开源免费，支持商业使用
  - 成熟稳定，生态丰富，商业项目广泛使用
  - TypeScript提供类型安全，降低开发错误率
- **状态管理**: Redux Toolkit
  - MIT许可证，官方推荐的状态管理方案
  - 取消RTK Query，使用自研API缓存机制
- **UI组件库**: 自研组件库 + 原生CSS
  - 取消Ant Design依赖，自行编写UI组件
  - 使用原生CSS和CSS Modules，避免第三方样式库
  - 提高代码可控性，减少外部依赖
- **图表库**: 自研图表组件
  - 取消ECharts依赖，自行编写基础图表组件
  - 使用Canvas或SVG实现饼图、曲线图等基础图表
  - 满足项目需求的同时减少外部依赖
- **构建工具**: Vite
  - MIT许可证，现代化构建工具，开发体验优秀
- **样式方案**: CSS Modules + 原生CSS
  - 模块化CSS，避免样式冲突
  - 取消Less/Sass预处理器，使用原生CSS特性
- **路由管理**: React Router v6
  - MIT许可证，官方推荐的路由解决方案

#### 2.2.2 后端技术栈
- **运行环境**: Python 3.11+
  - 长期支持版本，稳定可靠，AI生态丰富
- **Web框架**: FastAPI
  - 高性能异步框架，自动生成API文档
  - 支持类型提示，开发体验优秀
- **AI服务集成**:
  - **主要方案**: LangChain + LangGraph
    - LangChain：AI应用开发框架，支持多种LLM
    - LangGraph：基于图的AI工作流编排
- **数据库**:
  - **主数据库**: MySQL 8.0+
    - 开源免费，性能优秀，支持JSON字段
  - **缓存数据库**: Redis 7+
    - 高性能内存数据库，支持多种数据结构
- **ORM框架**: SQLAlchemy + Alembic
  - 功能强大的Python ORM
  - 支持数据库迁移和版本控制
- **任务队列**: Celery + Redis
  - 分布式任务队列，支持异步处理


#### 2.2.3 数据服务
- **ETF数据源与市场数据**:
  - **主要方案**: wind数据库（sqlserver数据库）
- **新闻资讯**:
  - **主要方案**: 通过request发起http请求（GET）获取新闻与研报

#### 2.2.4 部署运维
- **容器编排**: Docker + Docker Compose
  - 开发环境使用Docker Compose
  - 生产环境可考虑Kubernetes
- **反向代理**: Nginx
  - 高性能Web服务器，支持负载均衡


## 3. 数据存储设计

### 3.1 数据存储策略

#### 3.1.1 存储方案划分

**文件存储数据**（便于大模型读取理解）:

**业务配置文件**:
- `config/business_flows.yaml` - 业务流程定义和状态转换规则
- `config/prompt_templates.yaml` - 各阶段提示词模板
- `config/strategy_templates.json` - 标准策略模板和参数
- `config/investment_rules.yaml` - 投资规则和约束条件

**用户会话文件**:
- `data/sessions/{user_id}/{session_id}.json` - 对话上下文和要素提取结果
- `data/user_profiles/{user_id}/profile.json` - 用户投资偏好和历史行为
- `data/user_profiles/{user_id}/strategies.json` - 用户策略配置文件

**知识库文件**:
- `knowledge/etf_categories.json` - ETF分类和标签体系
- `knowledge/investment_concepts.yaml` - 投资概念和术语解释
- `knowledge/risk_profiles.json` - 风险等级定义和特征

**数据库存储数据**（结构化查询和实时更新）:
- ETF基础数据：产品信息、实时价格、绩效指标
- 市场数据：指数数据、行情数据、技术分析指标
- 新闻资讯数据：财经新闻、研报信息、市场热点
- 用户认证数据：登录信息、会话管理、权限控制
- 系统运行数据：操作日志、错误记录、性能监控

### 3.2 数据库模型设计（面向大模型优化）

#### 3.2.1 ETF数据表设计

**ETF基础信息表 (etf_basic_info)**:
- id: 主键，自增整数
- etf_code: ETF代码，如"510300.SH"
- etf_name: ETF名称，如"沪深300ETF"
- full_name: ETF全称
- asset_class: 资产类别，如"股票型ETF"
- investment_type: 投资类型，如"被动指数型"
- fund_company: 基金公司
- listing_date: 上市日期
- fund_scale: 基金规模（万元）
- status: 状态（上市/停牌/退市）


**ETF价格数据表 (etf_price_data)**:
- id: 主键，自增整数
- etf_code: ETF代码，外键关联
- trade_date: 交易日期
- open_price: 开盘价
- close_price: 收盘价
- high_price: 最高价
- low_price: 最低价
- volume: 成交量
- turnover: 成交额(千元)


**ETF绩效指标表 (etf_performance_metrics)**:
- id: 主键，自增整数
- etf_code: ETF代码，外键关联
- period_start_date: 统计开始日期
- period_end_date: 统计结束日期
- total_return: 总收益率（%）
- annualized_return: 年化收益率（%）
- volatility: 波动率（%）
- max_drawdown: 最大回撤（%）
- sharpe_ratio: 夏普比率
- sortino_ratio: 索提诺比率
- calmar_ratio: 卡尔玛比率
- win_rate: 胜率（%）
- beta: 贝塔系数
- alpha: 阿尔法系数
- information_ratio: 信息比率
- performance_summary: 绩效总结（文本，便于大模型理解）
- risk_assessment: 风险评估（文本描述）
- data_source: 数据来源
- calculated_at: 计算时间

#### 3.2.2 市场数据表设计

**市场指数数据表 (market_index_data)**:
- id: 主键，自增整数
- index_code: 指数代码，如"000300.SH"
- index_name: 指数名称，如"沪深300指数"
- trade_date: 交易日期
- open_value: 开盘点位
- close_value: 收盘点位
- high_value: 最高点位
- low_value: 最低点位
- volume: 成交量
- turnover: 成交额(千元)


#### 3.2.3 新闻资讯数据表设计

**财经新闻表 (financial_news)**:
- id: 主键，自增整数
- news_id: 新闻唯一标识
- title: 新闻标题
- summary: 新闻摘要
- content: 新闻正文（长文本）
- author: 作者
- source: 新闻来源，如"新浪财经"

**研究报告表 (research_reports)**:
- id: 主键，自增整数
- report_id: 报告唯一标识
- title: 报告标题
- abstract: 报告摘要
- institution: 研究机构
- analyst: 分析师
- report_type: 报告类型，如"行业研究/个股分析/策略报告"
- key_points: 核心观点（JSON数组）
- data_source: 数据来源



#### 3.2.4 用户数据表设计

**用户基础信息表 (users)**:
- id: 主键，自增整数
- phone_number: 手机号，唯一索引
- password_hash: 加密密码
- nickname: 用户昵称
- registration_date: 注册日期
- last_login_time: 最后登录时间
- login_count: 登录次数
- is_active: 账户状态
- user_type: 用户类型（新用户/老用户）
- created_at: 创建时间
- updated_at: 更新时间

**用户策略记录表 (user_strategies)**:
- id: 主键，自增整数
- user_id: 外键，关联用户表
- strategy_name: 策略名称
- strategy_file_path: 策略文件路径（指向JSON文件）
- risk_level: 风险等级
- target_return: 目标收益率（%）
- investment_amount: 投资金额
- etf_count: ETF数量
- asset_allocation_summary: 资产配置摘要（文本）
- creation_context: 创建背景（文本，记录创建时的对话要点）
- performance_summary: 绩效摘要（文本）
- last_backtest_date: 最后回测日期
- status: 策略状态（活跃/暂停/已删除）
- created_at: 创建时间
- updated_at: 更新时间

**用户对话记录表 (user_conversations)**:
- id: 主键，自增整数
- user_id: 外键，关联用户表
- session_id: 会话ID
- conversation_file_path: 对话文件路径（指向JSON文件）
- session_summary: 会话摘要（文本，便于大模型快速理解）
- extracted_elements_summary: 要素提取摘要（文本）
- business_stage: 业务阶段
- message_count: 消息数量
- strategy_generated: 是否生成了策略
- session_outcome: 会话结果（文本描述）
- started_at: 会话开始时间
- ended_at: 会话结束时间
- last_activity: 最后活跃时间

#### 3.2.5 数据补全与加工策略

基于Wind数据库的实际可获取字段，系统需要通过智能数据加工来补全缺失的关键信息。

**数据补全模块设计**:

**ETF分类信息补全**:
```python
# app/data_processing/etf_classifier.py
def derive_etf_classification(etf_name: str, etf_code: str) -> Dict[str, str]:
    """基于ETF名称和代码推导分类信息"""
    
    industry_keywords = {
        "科技": ["科技", "芯片", "半导体", "人工智能", "AI", "5G"],
        "医药": ["医药", "生物", "医疗", "健康", "制药"],
        "金融": ["银行", "保险", "证券", "金融"],
        "消费": ["消费", "食品", "饮料", "零售", "白酒"],
        "能源": ["能源", "石油", "煤炭", "电力", "新能源"],
        "军工": ["军工", "国防", "航天", "航空"]
    }
    
    # 基于名称匹配推导分类
    for industry, keywords in industry_keywords.items():
        if any(keyword in etf_name for keyword in keywords):
            return {
                "derived_category": f"{industry}行业ETF",
                "derived_sub_category": industry,
                "derived_investment_objective": f"跟踪{industry}行业相关指数，投资{industry}行业优质公司"
            }
    
    return {
        "derived_category": "综合指数ETF", 
        "derived_sub_category": "综合",
        "derived_investment_objective": "通过跟踪相关指数，实现对市场的广泛投资"
    }
```

**新闻关联性分析**:
```python
# app/data_processing/news_analyzer.py
class NewsETFMatcher:
    def analyze_news_relevance(self, news_content: str, etf_list: List[Dict]) -> Dict:
        """分析新闻与ETF的关联性"""
        
        # 1. 基于关键词匹配
        news_keywords = self._extract_keywords(news_content)
        related_etfs = []
        
        for etf in etf_list:
            if self._calculate_relevance_score(news_keywords, etf) > 0.3:
                related_etfs.append(etf['etf_code'])
        
        # 2. 情感分析
        sentiment_score = self._analyze_sentiment(news_content)
        
        # 3. 投资含义提取
        investment_implications = self._extract_investment_implications(news_content)
        
        return {
            "derived_related_etfs": related_etfs,
            "derived_sentiment_score": sentiment_score,
            "derived_investment_implications": investment_implications
        }
```

**虚拟板块数据构建**:
```python
# app/data_processing/sector_builder.py
class VirtualSectorBuilder:
    def build_sector_data(self, etf_data: List[Dict], date: str) -> List[Dict]:
        """基于ETF数据构建虚拟板块指数"""
        
        # 按行业分组ETF
        sector_groups = self._group_etfs_by_sector(etf_data)
        
        sector_data = []
        for sector_name, etfs in sector_groups.items():
            # 按市值加权计算板块指数
            sector_index = self._calculate_weighted_sector_index(etfs, date)
            sector_data.append({
                "virtual_sector_code": f"VS_{sector_name}",
                "sector_name": f"{sector_name}板块",
                "trade_date": date,
                "index_value": sector_index["value"],
                "change_rate": sector_index["change_rate"],
                "constituent_etfs": [etf["etf_code"] for etf in etfs]
            })
        
        return sector_data
```

**估值指标估算**:
```python
# app/data_processing/valuation_calculator.py
class ValuationCalculator:
    def estimate_valuation_metrics(self, etf_code: str, price_history: List[Dict]) -> Dict:
        """基于价格历史估算估值指标"""
        
        recent_prices = [p["close_price"] for p in price_history[-60:]]
        volatility = self._calculate_volatility(recent_prices)
        price_position = self._calculate_price_position(recent_prices)
        
        # 基于统计模型估算PE/PB
        estimated_pe = self._estimate_pe_ratio(price_position, volatility)
        estimated_pb = self._estimate_pb_ratio(estimated_pe)
        
        return {
            "derived_pe_ratio": estimated_pe,
            "derived_pb_ratio": estimated_pb,
            "price_position_percentile": price_position,
            "volatility": volatility
        }
```

**数据补全任务调度**:
```python
# app/tasks/data_enrichment_tasks.py
@celery.task
def daily_data_enrichment():
    """每日数据补全任务"""
    
    # 1. 补全ETF分类信息
    enrich_etf_classifications()
    
    # 2. 分析新闻关联性
    process_news_etf_relations()
    
    # 3. 构建虚拟板块数据
    build_virtual_sector_indices()
    
    # 4. 计算估值指标
    calculate_valuation_metrics()
```

#### 3.2.6 数据表优化设计（面向大模型）

**表设计原则**:
1. **语义化字段名**: 使用清晰的英文字段名，便于大模型理解
2. **文本描述丰富**: 增加description、summary等文本字段
3. **结构化标签**: 使用JSON格式存储标签和分类信息
4. **关联关系明确**: 通过外键和JSON字段建立数据关联
5. **时间序列优化**: 合理的时间字段设计，便于时序分析

**大模型友好特性**:
- 长文本字段存储详细描述，便于语义理解
- JSON格式存储结构化数据，便于解析
- 标准化的分类和标签体系
- 清晰的数据关联关系
- 丰富的元数据信息

### 3.3 文件存储结构设计

#### 3.3.1 业务配置文件结构

**业务流程配置文件** (`config/business_flows.yaml`):
```yaml
business_flows:
  new_user_flow:
    name: "新用户引导流程"
    description: "针对首次使用系统的用户的引导流程"
    stages:
      - stage_id: "introduction"
        name: "策略介绍"
        description: "介绍ETF资产配置策略核心逻辑"
        triggers: ["新用户", "首次使用"]
        next_stages: ["element_collection"]
        system_prompt: "您是专业的ETF投资顾问..."
      - stage_id: "element_collection"
        name: "要素收集"
        description: "收集用户投资偏好和约束条件"
        triggers: ["投资偏好", "风险承受"]
        next_stages: ["strategy_generation"]
        
  old_user_flow:
    name: "老用户服务流程"
    description: "针对已有策略用户的服务流程"
    stages:
      - stage_id: "welcome_back"
        name: "欢迎回归"
        description: "展示历史策略和最新收益"
        triggers: ["老用户", "历史策略"]
        next_stages: ["strategy_review", "optimization"]
```

**提示词模板文件** (`config/prompt_templates.yaml`):
```yaml
prompt_templates:
  element_extraction:
    system_prompt: |
      您是专业的投资顾问助手，需要从用户对话中提取关键投资要素。
      请分析对话内容，提取以下要素：
      1. 风险承受能力：保守/稳健/积极/激进
      2. 目标收益率：用户期望的年化收益率
      3. 投资金额：计划投资的资金量
      4. 投资期限：短期/中期/长期
      5. 偏好资产类别：股票/债券/商品/REITS等
      6. 禁忌资产：不愿投资的资产类别
    
  strategy_generation:
    system_prompt: |
      您是ETF资产配置专家，需要基于用户投资要素生成合适的ETF配置策略。
      请考虑以下因素：
      1. 风险收益匹配
      2. 资产分散化
      3. 费用成本控制
      4. 流动性要求
      
  strategy_optimization:
    system_prompt: |
      您需要根据用户反馈优化现有策略配置。
      分析用户不满意的方面，提供具体的调整建议。
```

#### 3.3.2 用户数据文件结构

**用户投资档案文件** (`data/user_profiles/{user_id}/profile.json`):
```json
{
  "user_id": 12345,
  "investment_profile": {
    "risk_tolerance": "稳健",
    "investment_experience": "3年",
    "preferred_asset_classes": ["股票", "债券"],
    "forbidden_assets": ["房地产"],
    "typical_investment_amount": 100000,
    "investment_horizon": "中期",
    "rebalance_preference": "季度"
  },
  "behavioral_patterns": {
    "conversation_style": "详细咨询型",
    "decision_speed": "谨慎型",
    "feedback_frequency": "高频反馈",
    "optimization_preference": "渐进式调整"
  },
  "historical_preferences": [
    {
      "date": "2024-01-01",
      "preference_snapshot": {...},
      "context": "首次使用系统时的偏好"
    }
  ],
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**对话会话文件** (`data/sessions/{user_id}/{session_id}.json`):
```json
{
  "session_id": "uuid-string",
  "user_id": 12345,
  "session_metadata": {
    "started_at": "2024-01-15T09:00:00Z",
    "business_stage": "element_collection",
    "conversation_rounds": 5,
    "session_goal": "生成新的投资策略"
  },
  "conversation_history": [
    {
      "round": 1,
      "user_message": "我想投资ETF，但不知道怎么选择",
      "assistant_response": "我来帮您制定合适的ETF投资策略...",
      "extracted_elements": {
        "intent": "策略咨询",
        "risk_clues": ["不知道怎么选择"],
        "confidence": 0.7
      },
      "timestamp": "2024-01-15T09:01:00Z"
    }
  ],
  "extracted_investment_elements": {
    "risk_tolerance": "稳健",
    "target_return": 8.5,
    "investment_amount": 50000,
    "preferred_asset_classes": ["股票", "债券"],
    "extraction_confidence": 0.85,
    "last_updated": "2024-01-15T09:15:00Z"
  },
  "context_for_llm": {
    "user_background": "投资新手，希望通过ETF进行资产配置",
    "conversation_summary": "用户咨询ETF投资策略，已收集基本投资偏好",
    "next_actions": ["生成初步策略", "展示配置方案"],
    "key_concerns": ["风险控制", "收益稳定性"]
  }
}
```

#### 3.3.3 知识库文件结构

**ETF分类体系文件** (`knowledge/etf_categories.json`):
```json
{
  "asset_classes": {
    "equity_etfs": {
      "name": "股票型ETF",
      "description": "主要投资于股票市场的ETF产品",
      "subcategories": {
        "broad_market": {
          "name": "宽基指数ETF",
          "description": "跟踪市场宽基指数",
          "examples": ["510300.SH", "510500.SH"],
          "risk_level": "中等",
          "suitable_for": ["稳健型投资者", "长期投资"]
        },
        "sector_specific": {
          "name": "行业主题ETF", 
          "description": "专注特定行业或主题",
          "examples": ["512170.SH", "515030.SH"],
          "risk_level": "较高",
          "suitable_for": ["积极型投资者", "主题投资"]
        }
      }
    },
    "bond_etfs": {
      "name": "债券型ETF",
      "description": "主要投资于债券市场的ETF产品",
      "subcategories": {
        "government_bonds": {
          "name": "国债ETF",
          "description": "投资国家发行的债券",
          "risk_level": "低",
          "suitable_for": ["保守型投资者", "资产配置"]
        }
      }
    }
  },
  "risk_mapping": {
    "conservative": ["government_bonds", "high_grade_corporate_bonds"],
    "balanced": ["broad_market", "mixed_bonds"],
    "aggressive": ["sector_specific", "growth_stocks"],
    "speculative": ["thematic_etfs", "emerging_markets"]
  }
}
```

### 3.4 数据索引优化（面向大模型查询）

#### 3.4.1 数据库索引设计

**ETF数据表索引**:
- `idx_etf_basic_info_code` - ETF代码索引（唯一）
- `idx_etf_basic_info_asset_class` - 资产类别索引
- `idx_etf_basic_info_tracking_index` - 跟踪指数索引
- `idx_etf_basic_info_fund_company` - 基金公司索引
- `idx_etf_price_data_code_date` - 代码+日期复合索引
- `idx_etf_performance_metrics_code_period` - 代码+周期复合索引

**新闻资讯表索引**:
- `idx_financial_news_publish_time` - 发布时间索引
- `idx_financial_news_category` - 新闻分类索引
- `idx_financial_news_tags` - 标签索引（JSON数组）
- `idx_financial_news_sentiment_score` - 情感评分索引
- `idx_research_reports_publish_date` - 发布日期索引
- `idx_market_hotspots_heat_score` - 热度评分索引

**用户数据表索引**:
- `idx_users_phone_number` - 手机号唯一索引
- `idx_user_strategies_user_id` - 用户ID索引
- `idx_user_conversations_user_id` - 用户ID索引
- `idx_user_conversations_session_id` - 会话ID索引

#### 3.4.2 大模型查询优化

**文本搜索优化**:
- 为长文本字段创建全文索引
- 支持语义相似度查询
- 标签和分类的快速筛选

**数据关联优化**:
- JSON字段的高效查询
- 时间序列数据的范围查询
- 多表关联的性能优化

### 3.5 数据同步机制

#### 3.5.1 外部数据源集成

**Wind数据库同步**:
- 定时任务：每日凌晨同步ETF基础信息
- 实时同步：交易时间内每5分钟同步价格数据
- 数据清洗：标准化数据格式，补充描述性文本
- 增量更新：仅同步变更数据，提高效率

**新闻资讯数据同步**:
- 多源聚合：从新浪财经、东方财富等多个源获取
- 实时爬取：每30分钟获取最新财经新闻
- 内容处理：提取关键信息，生成摘要和标签
- 情感分析：使用大模型分析新闻情感倾向
- 关联分析：识别新闻与ETF、行业的关联关系

**数据质量控制**:
- 数据验证：检查数据完整性和准确性
- 重复检测：避免重复数据入库
- 异常处理：处理数据源异常和网络问题
- 数据标记：记录数据来源和处理状态

#### 3.5.2 文件数据管理

**配置文件版本控制**:
- Git管理：业务配置文件纳入版本控制
- 变更追踪：记录配置变更历史
- 回滚机制：支持配置回滚和恢复

**用户文件管理**:
- 自动创建：用户首次使用时自动创建档案文件
- 定期备份：用户数据文件定期备份
- 清理机制：定期清理过期的会话文件
- 权限控制：确保用户数据文件的访问安全

### 3.6 数据存储架构优势

#### 3.6.1 文件存储优势
- **大模型友好**: 文件格式便于大模型直接读取和理解
- **版本控制**: 配置文件可纳入Git管理，便于追踪变更
- **灵活配置**: 业务规则可通过修改文件快速调整
- **备份简单**: 文件备份和恢复机制简单可靠
- **调试便利**: 可直接查看和编辑文件内容

#### 3.6.2 数据库存储优势
- **查询性能**: 结构化数据查询效率高
- **数据一致性**: 事务保证数据一致性
- **并发处理**: 支持多用户并发访问
- **索引优化**: 针对大模型查询模式优化索引
- **扩展性**: 支持数据量增长和性能扩展

#### 3.6.3 混合存储优势
- **职责分离**: 配置与数据分离，便于管理
- **性能优化**: 热数据库存储，冷数据文件存储
- **成本控制**: 减少数据库存储成本
- **维护简化**: 不同类型数据采用最适合的存储方式

## 4. 系统运作流程

### 4.1 整体运作机制

系统采用前后端分离架构，通过WebSocket实现实时通信，基于对话驱动的策略生成模式。整个系统运作围绕"对话引导-要素提取-策略构建-反馈优化"的循环展开，实现从非结构化对话到结构化投资策略的转化。

### 4.2 模块交互流程

#### 4.2.1 用户认证与身份识别流程

**前端用户认证模块** → **后端用户认证模块** → **数据库服务模块**

1. **用户注册/登录**：
   - 前端用户认证模块收集用户手机号和密码
   - 通过HTTP请求发送到后端用户认证模块
   - 后端验证用户信息，加密存储到MySQL数据库
   - 返回JWT令牌给前端，建立用户会话

2. **用户身份判断**：
   - 后端用户认证模块查询用户历史策略记录
   - 根据是否有保存策略判断新用户/老用户类型
   - 将用户类型信息传递给智能体核心模块

#### 4.2.2 对话交互与策略生成流程

**前端对话界面模块** → **后端对话服务模块** → **智能体核心模块** → **LangChain工具模块** → **策略引擎模块**

1. **对话接收与处理**：
   - 前端对话界面模块接收用户输入
   - 通过WebSocket发送到后端对话服务模块
   - 对话服务模块将消息传递给智能体核心模块

2. **智能体任务规划**：
   - 智能体核心模块分析用户对话内容
   - 根据业务流程阶段生成任务规划
   - 调用相应的LangChain工具获取数据和信息

3. **要素提取与策略生成**：
   - 投资要素提取工具从对话中提取关键信息
   - ETF数据获取工具从Wind数据库获取历史数据
   - 策略生成工具基于要素和数据生成配置策略
   - 策略回测工具使用历史数据计算性能指标

4. **实时状态更新**：
   - 智能体核心模块通过WebSocket向前端推送处理状态
   - 前端对话界面模块显示"思考中"、"数据获取中"等状态
   - 前端策略展示模块实时更新策略内容

#### 4.2.3 策略展示与用户反馈流程

**前端策略展示模块** → **前端对话界面模块** → **后端对话服务模块**

1. **策略内容展示**：
   - 前端策略展示模块接收策略数据
   - 通过ECharts组件展示ETF配置饼图
   - 显示回测曲线和性能指标表格

2. **用户反馈收集**：
   - 用户通过对话界面提出修改意见
   - 前端将反馈信息发送到后端
   - 触发新一轮的策略优化流程

#### 4.2.4 历史策略管理流程

**前端历史管理模块** → **后端策略引擎模块** → **数据库服务模块**

1. **策略保存**：
   - 用户点击保存按钮
   - 前端历史管理模块发送保存请求
   - 后端策略引擎模块将策略数据存储到MySQL

2. **历史策略查看**：
   - 前端历史管理模块请求历史策略列表
   - 后端从数据库查询用户保存的策略
   - 返回策略列表给前端展示

### 4.3 业务场景运作流程

#### 4.3.1 新用户场景运作流程

**场景描述**：用户首次使用系统，没有保存过策略

**运作流程**：

1. **用户注册登录**：
   - 用户输入手机号和密码注册
   - 系统验证并创建用户账户
   - 判断为新用户类型

2. **系统引导介绍**：
   - 智能体核心模块生成ETF策略介绍内容
   - 前端对话界面模块展示介绍信息
   - 前端策略展示模块展示基准策略示例

3. **对话引导要素收集**：
   - 智能体通过多轮对话收集用户偏好
   - 投资要素提取工具实时提取关键信息
   - 系统主动推荐热点资讯和研报

4. **策略生成与展示**：
   - 基于收集的要素生成初步策略
   - 前端策略展示模块实时更新策略内容
   - 显示ETF配置、回测曲线、性能指标

5. **用户反馈与优化**：
   - 用户提出修改意见
   - 系统重新生成优化后的策略
   - 循环优化直到用户满意

6. **策略保存**：
   - 超过3轮对话后提示保存
   - 用户点击保存按钮
   - 策略和历史信息存储到数据库

#### 4.3.2 老用户场景运作流程

**场景描述**：用户已保存过策略，再次使用系统

**运作流程**：

1. **用户登录识别**：
   - 用户使用手机号登录
   - 系统识别为老用户类型
   - 查询用户历史保存的策略

2. **历史策略展示**：
   - 展示用户表现最好的历史策略
   - 显示策略最新收益追踪
   - 提供策略切换选项

3. **策略优化建议**：
   - 系统主动提出优化建议
   - 基于最新市场资讯和研报
   - 询问用户是否需要调整

4. **策略更新与保存**：
   - 用户确认优化建议
   - 系统生成更新后的策略
   - 用户选择保存新策略

#### 4.3.3 策略优化场景运作流程

**场景描述**：用户对当前策略提出修改要求

**运作流程**：

1. **用户反馈接收**：
   - 用户通过对话提出具体修改意见
   - 前端对话界面模块收集反馈信息
   - 发送到后端智能体核心模块

2. **要素重新提取**：
   - 投资要素提取工具分析用户反馈
   - 更新用户偏好和约束条件
   - 识别需要调整的策略参数

3. **策略重新生成**：
   - 策略生成工具基于新要素生成策略
   - 策略回测工具计算新策略性能
   - 对比新旧策略的差异

4. **优化结果展示**：
   - 前端策略展示模块更新策略内容
   - 显示修改说明和影响分析
   - 用户确认是否接受优化结果

#### 4.3.4 主动推荐场景运作流程

**场景描述**：系统主动向用户推荐新的资产类别或板块

**运作流程**：

1. **市场资讯获取**：
   - 市场资讯获取工具获取最新资讯
   - 按板块和资产类别分类整理
   - 生成推荐内容

2. **推荐内容展示**：
   - 智能体生成推荐对话内容
   - 前端对话界面模块展示推荐信息
   - 询问用户是否添加推荐资产

3. **用户决策处理**：
   - 用户选择添加或拒绝推荐
   - 系统根据用户选择更新策略
   - 如果拒绝超过3次，停止推荐

4. **策略更新**：
   - 基于用户选择重新生成策略
   - 更新ETF配置和投资比例
   - 展示优化后的策略结果

### 4.4 数据流转机制

#### 4.4.1 实时数据流转

**用户输入** → **WebSocket** → **后端处理** → **WebSocket** → **前端更新**

1. **用户消息流转**：
   - 前端对话界面模块收集用户输入
   - 通过WebSocket发送到后端对话服务模块
   - 后端处理后通过WebSocket返回响应

2. **状态更新流转**：
   - 智能体核心模块生成处理状态
   - 通过WebSocket实时推送到前端
   - 前端界面实时显示处理进度

3. **策略数据流转**：
   - 策略引擎模块生成策略数据
   - 通过WebSocket推送到前端策略展示模块
   - 前端实时更新策略展示内容

#### 4.4.2 数据存储流转

**混合存储架构** → **文件存储** + **数据库存储**

1. **文件存储流转**：
   - 用户对话上下文保存到JSON文件
   - 投资要素提取结果写入用户档案文件
   - 业务配置和提示词模板通过文件管理
   - 大模型直接读取文件进行分析和理解

2. **数据库存储流转**：
   - ETF基础数据从Wind数据库同步到MySQL
   - 新闻资讯数据从多个API源聚合到MySQL
   - 用户认证信息存储到MySQL用户表
   - 策略记录和回测结果存储到MySQL

3. **混合存储协作**：
   - 数据库存储结构化数据，支持高效查询
   - 文件存储上下文数据，便于大模型理解
   - 缓存层提升数据访问性能
   - 定期同步确保数据一致性

### 4.5 系统协作机制

#### 4.5.1 前后端协作

**前端模块协作**：
- 用户认证模块为其他模块提供用户身份信息
- 对话界面模块与策略展示模块协同工作
- 状态管理模块统一管理各模块状态

**后端模块协作**：
- 用户认证模块为所有模块提供身份验证
- 智能体核心模块协调各LangChain工具
- 策略引擎模块与数据服务模块协同工作
- 缓存服务模块为所有模块提供缓存支持

#### 4.5.2 实时通信机制

**WebSocket连接管理**：
- 建立持久的WebSocket连接
- 支持双向实时通信
- 处理连接断开和重连

**消息路由机制**：
- 根据消息类型路由到相应模块
- 支持广播和点对点通信
- 处理消息队列和优先级

**状态同步机制**：
- 实时同步前后端状态
- 处理并发状态更新
- 确保数据一致性

## 5. 功能模块设计

### 5.1 前端功能模块

#### 5.1.0 前端UI设计风格要求
**设计理念**: 打造现代化、专业化的金融科技产品界面，体现系统的专业性和科技感。

**整体风格要求**:
- **互联网风格**: 采用现代互联网产品的设计语言和交互模式
- **美观大气**: 界面布局合理，视觉层次清晰，整体美观大方
- **简洁明了**: 去除冗余元素，突出核心功能，信息展示简洁清晰
- **科技感**: 运用现代设计元素，体现金融科技的专业性和前瞻性

**视觉设计规范**:
- **配色方案**: 以深蓝色系为主色调，搭配白色、灰色和科技蓝
  - 主色调：#1890FF（科技蓝）
  - 辅助色：#F0F2F5（浅灰）、#FFFFFF（纯白）
  - 强调色：#52C41A（成功绿）、#FF4D4F（警告红）
- **字体规范**: 采用现代无衬线字体，确保可读性
  - 中文：苹方、微软雅黑、思源黑体
  - 英文：Roboto、Arial、Helvetica
- **图标风格**: 线性图标为主，简洁现代，统一风格

**组件设计要求**:
- **按钮设计**: 
  - 主要按钮：圆角矩形，渐变背景，悬停效果
  - 次要按钮：线框样式，悬停填充效果
  - 文字按钮：简洁文字，悬停变色
- **输入框设计**:
  - 圆角边框，聚焦时边框高亮
  - 占位符文字清晰，错误状态明显
- **卡片设计**:
  - 轻微阴影效果，圆角处理
  - 悬停时阴影加深，增强交互感
- **菜单样式**:
  - 侧边导航：简洁图标+文字，选中状态明显
  - 下拉菜单：圆角、阴影，动画过渡

**交互设计要求**:
- **动画效果**: 适度使用过渡动画，提升用户体验
- **响应式设计**: 适配不同屏幕尺寸，保证移动端体验
- **加载状态**: 优雅的加载动画和骨架屏
- **反馈机制**: 操作反馈及时，状态变化明确

**页面布局要求**:
- **导航结构**: 顶部导航+侧边菜单的经典布局
- **内容区域**: 合理的间距和留白，突出重要信息
- **信息层级**: 通过颜色、字号、间距建立清晰的信息层级

#### 5.1.1 用户认证模块
**功能描述**: 提供用户注册、登录、登出等认证功能，管理用户身份状态。

**细分功能**:
- 用户注册界面：提供手机号注册和密码设置功能
- 用户登录界面：提供手机号和密码登录功能
- 用户信息管理：显示和编辑用户基本信息
- 登录状态管理：管理用户登录状态和会话信息
- 密码修改功能：提供用户修改密码的界面

**依赖关系**:
- 依赖后端用户认证API
- 依赖状态管理模块管理登录状态
- 依赖本地存储保存用户信息

**输入输出规范**:
- 输入：用户注册信息、登录凭据、用户操作指令
- 输出：认证状态更新、用户信息展示、错误提示信息

#### 5.1.2 对话界面模块
**功能描述**: 提供用户与智能体交互的对话界面，支持实时消息展示和输入。

**细分功能**:
- 消息展示区域：显示用户和智能体的对话历史
- 消息输入区域：提供文本输入框和发送按钮
- 状态指示器：显示智能体处理状态（思考中、生成中、完成等）
- 消息类型区分：区分用户消息、智能体回复、系统提示等

**依赖关系**:
- 依赖对话服务模块获取消息数据
- 依赖状态管理模块管理界面状态
- 依赖WebSocket服务实现实时通信

**输入输出规范**:
- 输入：用户文本消息、系统状态更新
- 输出：发送用户消息到后端、更新界面显示状态

#### 5.1.3 策略展示模块
**功能描述**: 展示基于用户对话内容生成的ETF配置策略，包括策略详情、配置比例、回测结果等。

**细分功能**:
- 策略基本信息卡片：使用自研卡片组件显示策略名称、描述、投资理念
- ETF配置饼图：使用自研Canvas图表组件可视化展示各类ETF的配置比例
- 回测曲线图：使用自研SVG图表组件展示策略历史表现和收益曲线
- 性能指标表格：使用自研表格组件显示年化收益率、最大回撤、夏普比率等
- 对话驱动更新：根据用户对话内容更新策略展示
- 静态展示模式：策略生成后保持静态，不随行情变化

**依赖关系**:
- 依赖策略服务模块获取策略数据
- 依赖自研图表组件进行数据可视化
- 依赖WebSocket服务接收对话触发的策略更新通知

**输入输出规范**:
- 输入：策略数据、配置信息、回测结果、对话触发的更新指令
- 输出：用户交互事件（保存策略、修改配置等）

#### 5.1.4 历史管理模块
**功能描述**: 管理用户保存的策略历史，支持查看和删除操作。

**细分功能**:
- 策略列表展示：显示已保存的策略列表
- 策略详情查看：查看历史策略的完整信息
- 策略删除管理：支持删除不需要的策略

**依赖关系**:
- 依赖策略服务模块获取历史数据
- 依赖策略展示模块展示策略详情

**输入输出规范**:
- 输入：用户操作指令
- 输出：策略操作请求、界面状态更新

#### 5.1.5 状态管理模块
**功能描述**: 管理前端应用的核心状态，包括用户状态、对话状态、策略状态等。

**细分功能**:
- 用户状态管理：管理用户身份、会话信息
- 对话状态管理：管理对话历史、当前会话状态
- 策略状态管理：管理当前策略、策略生成状态
- 界面状态管理：管理加载状态、错误状态、提示信息

**依赖关系**:
- 为所有前端模块提供状态管理服务
- 依赖后端API进行数据同步

**输入输出规范**:
- 输入：用户操作、API响应、系统事件
- 输出：状态更新通知、数据同步请求

### 5.2 后端功能模块

#### 5.2.1 用户认证模块
**功能描述**: 提供用户注册、登录、身份验证等认证服务，管理用户账户和权限。

**技术实现**:
- **框架**: FastAPI + SQLAlchemy
- **认证**: JWT + PassLib
- **密码加密**: bcrypt
- **中间件**: FastAPI依赖注入

**细分功能**:
- 用户注册服务：处理用户手机号注册和密码设置
- 用户登录验证：验证用户手机号和密码，生成访问令牌
- 身份验证中间件：验证用户身份和访问权限
- 用户信息管理：管理用户基本信息和账户状态
- 密码加密存储：使用bcrypt加密存储用户密码
- 用户类型判断：根据用户是否有保存策略判断新老用户

**依赖关系**:
- 依赖数据库服务存储用户信息
- 依赖缓存服务管理用户会话
- 为所有需要认证的模块提供身份验证

**输入输出规范**:
- 输入：用户注册信息、登录凭据、身份验证请求
- 输出：认证结果、用户信息、访问令牌、用户类型判断

#### 5.2.2 智能体核心模块
**功能描述**: 基于业务流程设计智能体系统，通过LangChain和LangGraph实现任务规划和执行。

**技术实现**:
- **框架**: LangChain + LangGraph
- **LLM集成**: 本地模型
- **工具调用**: LangChain Tools
- **工作流编排**: LangGraph StateGraph

**细分功能**:
- 业务流程解析：将业务流程转换为LangChain的system提示词
- 任务规划生成：使用LangGraph生成任务规划图
- 工具调用管理：通过LangChain Tools调用各种功能工具
- 状态管理：使用LangGraph管理对话状态和流程状态
- 结果汇总生成：将工具调用结果汇总生成最终回复

**依赖关系**:
- 依赖所有MCP工具模块
- 依赖业务流程配置模块
- 依赖LangChain和LangGraph框架

**输入输出规范**:
- 输入：用户消息、对话上下文、业务流程配置
- 输出：任务规划图、工具调用指令、最终回复内容

#### 5.2.3 LangChain工具模块集合
**功能描述**: 提供核心LangChain Tools供智能体调用，实现数据获取、处理、分析等功能。

**技术实现**:
- **工具框架**: LangChain Tools
- **数据库连接**: SQLAlchemy + PyMySQL
- **HTTP请求**: requests + aiohttp
- **数据处理**: pandas + numpy

**细分功能**:
- 用户身份识别工具：识别新老用户，获取用户历史信息
- 要素提取工具：从对话中提取投资要素和偏好信息
- ETF数据获取工具：从Wind数据库获取ETF产品信息和市场数据
- 策略生成工具：基于要素生成ETF配置策略
- 策略回测工具：执行策略回测计算和性能分析
- 策略优化工具：根据用户反馈优化策略配置
- 市场资讯获取工具：通过HTTP请求获取最新市场资讯和研报

**依赖关系**:
- 依赖数据服务模块获取外部数据
- 依赖策略引擎模块进行策略计算
- 依赖缓存服务模块提高性能
- 依赖LangChain框架

**输入输出规范**:
- 输入：工具调用参数、上下文信息
- 输出：工具执行结果、状态信息、错误信息

#### 5.2.4 对话服务模块
**功能描述**: 管理对话流程，支持实时状态更新和中间结果展示。

**技术实现**:
- **框架**: FastAPI + WebSocket
- **异步处理**: asyncio + aiohttp
- **状态管理**: Redis + JSON
- **消息队列**: Celery

**细分功能**:
- 对话会话管理：创建、维护、销毁对话会话
- 实时状态推送：通过WebSocket向前端推送智能体处理状态
- 中间结果展示：推送任务执行过程中的中间结果
- 对话历史管理：存储和管理对话历史记录
- 异步消息处理：使用Celery处理长时间运行的任务

**依赖关系**:
- 依赖智能体核心模块获取处理状态
- 依赖WebSocket服务实现实时通信
- 依赖Redis缓存管理会话状态

**输入输出规范**:
- 输入：用户消息、智能体状态更新
- 输出：实时状态推送、对话历史数据

#### 5.2.5 策略引擎模块
**功能描述**: 负责基于用户对话内容生成ETF策略、回测、优化等核心计算功能。

**技术实现**:
- **计算框架**: pandas + numpy + scipy
- **回测引擎**: 自研回测算法
- **优化算法**: scipy.optimize
- **数据处理**: pandas + ta-lib
- **异步计算**: Celery任务队列

**细分功能**:
- 策略生成算法：基于用户对话提取的投资要素生成ETF配置策略
- 回测计算引擎：使用历史数据执行策略回测和性能计算
- 策略优化算法：根据用户对话反馈优化策略配置
- 风险评估模型：计算策略风险指标和回撤分析
- 对话驱动更新：策略仅在用户对话触发时更新，不随实时行情变化
- 异步回测任务：使用Celery处理长时间回测计算

**依赖关系**:
- 依赖数据服务模块获取历史市场数据
- 依赖LangChain工具模块接收对话提取的策略参数
- 依赖缓存服务模块提高计算性能
- 依赖Celery处理异步任务

**输入输出规范**:
- 输入：对话提取的投资要素、历史市场数据、用户反馈参数
- 输出：策略配置、回测结果、性能指标

#### 5.2.6 数据服务模块
**功能描述**: 提供统一的数据访问接口，管理多数据源集成和混合存储架构。

**技术实现**:
- **数据库连接**: SQLAlchemy + PyMySQL
- **Wind数据库**: pyodbc + SQL Server
- **HTTP请求**: requests + aiohttp
- **数据处理**: pandas + numpy
- **文件操作**: json + yaml + pathlib
- **缓存管理**: redis-py

**细分功能**:
- **多源数据集成**：从Wind、新浪财经、东方财富等多个数据源获取数据
- **数据标准化处理**：清洗和标准化不同来源的数据格式
- **统一存储管理**：将多源数据统一存储到MySQL数据库
- **文件数据管理**：管理用户档案、会话记录等文件数据
- **大模型数据准备**：为大模型工具调用准备结构化数据
- **数据质量控制**：验证数据完整性和准确性
- **增量同步机制**：支持增量数据更新和同步

**数据源管理**:
- **ETF数据源**: Wind数据库 → MySQL (etf_basic_info, etf_price_data, etf_performance_metrics)
- **市场数据源**: Wind数据库 → MySQL (market_index_data, sector_data)
- **新闻资讯源**: 多个HTTP API → MySQL (financial_news, research_reports, market_hotspots)
- **用户数据**: 混合存储（数据库+文件）
- **配置数据**: 文件存储（YAML/JSON格式）

**依赖关系**:
- 依赖Wind数据库连接
- 依赖多个HTTP请求服务
- 依赖缓存服务模块
- 依赖文件系统管理
- 依赖SQLAlchemy ORM

**输入输出规范**:
- 输入：数据查询请求、多源数据、文件读写请求
- 输出：标准化数据、文件数据、缓存状态信息

#### 5.2.7 缓存服务模块
**功能描述**: 提供基础的缓存管理服务，提高系统响应速度。

**技术实现**:
- **缓存框架**: redis-py + aioredis
- **序列化**: pickle + json
- **缓存策略**: TTL + LRU
- **连接池**: redis-py连接池

**细分功能**:
- 会话状态缓存：存储用户会话和对话状态
- 策略数据缓存：缓存生成的策略和回测结果
- 市场数据缓存：缓存从Wind数据库获取的市场数据
- 缓存失效管理：管理缓存过期和更新
- 异步缓存操作：支持异步缓存读写操作

**依赖关系**:
- 为所有后端模块提供缓存服务
- 依赖Redis数据库
- 支持异步操作

**输入输出规范**:
- 输入：缓存存储请求、查询请求
- 输出：缓存数据、缓存状态信息

#### 5.2.8 业务流程配置模块
**功能描述**: 管理业务流程配置，为智能体提供system提示词和流程控制。

**技术实现**:
- **配置管理**: Pydantic + YAML
- **状态机**: 自研状态机 + LangGraph
- **模板引擎**: Jinja2
- **配置存储**: SQLAlchemy + JSON字段

**细分功能**:
- 业务流程定义：定义新用户和老用户的业务流程
- 提示词模板管理：使用Jinja2管理不同阶段的提示词模板
- 流程状态跟踪：跟踪当前对话所处的业务流程阶段
- 流程规则配置：配置流程跳转和条件判断规则
- 动态配置更新：支持运行时更新流程配置

**依赖关系**:
- 为智能体核心模块提供流程配置
- 依赖对话服务模块获取流程状态
- 依赖LangGraph状态管理

**输入输出规范**:
- 输入：流程状态更新、用户行为数据
- 输出：流程配置、提示词模板、状态转换指令

#### 5.2.9 数据处理与补全模块
**功能描述**: 对Wind数据库获取的原始数据进行智能加工和补全，生成大模型可理解的丰富信息。

**技术实现**:
- **分类推导**: 基于机器学习和规则引擎的ETF分类
- **文本分析**: jieba分词 + TF-IDF + 情感分析
- **统计计算**: pandas + numpy数据处理
- **任务调度**: Celery定时任务

**细分功能**:
- ETF分类信息推导：基于名称和代码推导行业分类、投资主题
- 投资目标生成：根据分类信息生成标准化的投资目标描述
- 新闻关联性分析：分析新闻与ETF的关联度，提取投资含义
- 虚拟板块构建：基于ETF分类构建行业板块指数数据
- 估值指标估算：基于价格历史估算PE/PB等估值指标
- 数据质量监控：监控补全数据的准确性和一致性

**依赖关系**:
- 依赖数据服务模块获取原始数据
- 为智能体工具提供补全后的数据
- 依赖缓存服务存储计算结果
- 为策略引擎提供丰富的分析数据

**输入输出规范**:
- 输入：原始ETF数据、新闻文本、价格历史数据
- 输出：补全的分类信息、关联分析结果、估值指标、板块数据

#### 5.2.10 内容安全审查模块
**功能描述**: 对大模型生成的所有内容进行安全审查，确保内容合规性和安全性。

**技术实现**:
- **框架**: 自研内容安全审查系统
- **算法**: 关键词匹配 + 语义分析 + 规则引擎
- **存储**: 安全规则文件 + 审查日志数据库
- **性能**: 异步处理 + 缓存优化

**细分功能**:
- 输入内容预检查：检查用户输入是否包含敏感内容
- 大模型输出审查：对AI生成内容进行安全性检查
- 敏感词库管理：维护政治、NSFW、金融违规等敏感词库
- 合规性检查：确保投资建议符合金融监管要求
- 免责声明管理：自动添加标准化的风险提示和免责声明
- 安全日志记录：记录所有审查过程和结果
- 人工复审机制：高风险内容触发人工审核流程

**依赖关系**:
- 为智能体核心模块提供内容安全检查
- 依赖配置文件管理安全规则
- 依赖数据库存储审查日志
- 为所有涉及内容生成的模块提供安全保障

**输入输出规范**:
- 输入：待审查内容、审查类型、安全配置
- 输出：审查结果、处理后内容、安全评分、违规信息

## 6. API接口设计

### 6.1 用户认证相关接口

#### 6.1.1 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "phoneNumber": "string",
  "password": "string",
  "nickname": "string"
}

Response:
{
  "success": boolean,
  "message": "string",
  "userId": "string"
}
```

#### 6.1.2 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "phoneNumber": "string",
  "password": "string"
}

Response:
{
  "success": boolean,
  "message": "string",
  "token": "string",
  "user": {
    "id": "string",
    "phoneNumber": "string",
    "nickname": "string",
    "isNewUser": boolean
  }
}
```

#### 6.1.3 用户登出
```http
POST /api/auth/logout
Authorization: Bearer {token}

Response:
{
  "success": boolean,
  "message": "string"
}
```

### 6.2 对话相关接口

#### 6.2.1 开始对话
```http
POST /api/conversation/start
Content-Type: application/json
Authorization: Bearer {token}

{
  "userId": "string"
}

Response:
{
  "sessionId": "string",
  "welcomeMessage": "string",
  "isNewUser": boolean
}
```

#### 6.2.2 发送消息
```http
POST /api/conversation/message
Content-Type: application/json
Authorization: Bearer {token}

{
  "sessionId": "string",
  "message": "string"
}

Response:
{
  "response": "string",
  "strategyUpdated": boolean,
  "strategyId": "string"
}
```

### 6.3 策略相关接口

#### 6.3.1 获取策略详情
```http
GET /api/strategy/{strategyId}
Authorization: Bearer {token}

Response:
{
  "id": "string",
  "name": "string",
  "description": "string",
  "investmentPhilosophy": "string",
  "allocations": [
    {
      "etfCode": "string",
      "etfName": "string",
      "percentage": number,
      "category": "string"
    }
  ],
  "performance": {
    "annualReturn": number,
    "maxDrawdown": number,
    "sharpeRatio": number
  },
  "backtestData": [
    {
      "date": "string",
      "value": number,
      "return": number
    }
  ]
}
```

#### 6.3.2 保存策略
```http
POST /api/strategy/save
Content-Type: application/json
Authorization: Bearer {token}

{
  "strategyId": "string",
  "name": "string"
}

Response:
{
  "success": boolean,
  "strategyId": "string"
}
```

### 6.4 历史管理接口

#### 6.4.1 获取策略列表
```http
GET /api/strategy/history
Authorization: Bearer {token}

Response:
{
  "strategies": [
    {
      "id": "string",
      "name": "string",
      "createdAt": "string",
      "performance": {
        "annualReturn": number,
        "maxDrawdown": number
      }
    }
  ]
}
```

## 7. 前端界面设计

### 7.1 页面结构
```
┌─────────────────────────────────────────────────────────┐
│                    顶部导航栏                            │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│   对话界面      │           策略展示区域                 │
│                 │                                       │
│  ┌───────────┐  │  ┌─────────────────────────────────┐  │
│  │ 对话历史  │  │  │        策略详情卡片              │  │
│  └───────────┘  │  └─────────────────────────────────┘  │
│                 │  ┌─────────────────────────────────┐  │
│  ┌───────────┐  │  │        回测图表                 │  │
│  │ 输入框    │  │  └─────────────────────────────────┘  │
│  └───────────┘  │  ┌─────────────────────────────────┐  │
│                 │  │        操作按钮                  │  │
│                 │  └─────────────────────────────────┘  │
└─────────────────┴───────────────────────────────────────┘
```

### 7.2 核心组件（基于设计风格要求）

#### 7.2.0 设计系统实现
**设计令牌 (Design Tokens)**:
```css
/* 主要颜色变量 */
:root {
  --primary-color: #1890FF;
  --primary-hover: #40A9FF;
  --primary-active: #096DD9;
  
  --background-color: #FFFFFF;
  --background-secondary: #F0F2F5;
  --background-tertiary: #FAFAFA;
  
  --text-primary: #262626;
  --text-secondary: #595959;
  --text-disabled: #BFBFBF;
  
  --success-color: #52C41A;
  --warning-color: #FAAD14;
  --error-color: #FF4D4F;
  
  --border-color: #D9D9D9;
  --border-hover: #40A9FF;
  
  --shadow-light: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-heavy: 0 8px 24px rgba(0, 0, 0, 0.12);
  
  --border-radius-small: 4px;
  --border-radius-medium: 6px;
  --border-radius-large: 8px;
  
  --font-size-small: 12px;
  --font-size-base: 14px;
  --font-size-large: 16px;
  --font-size-xl: 20px;
  --font-size-xxl: 24px;
  
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}

/* 动画变量 */
:root {
  --transition-fast: 0.2s ease;
  --transition-base: 0.3s ease;
  --transition-slow: 0.5s ease;
}
```

**通用组件样式基类**:
```css
/* 按钮基础样式 */
.btn-base {
  border: none;
  border-radius: var(--border-radius-medium);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  padding: var(--spacing-sm) var(--spacing-md);
  box-shadow: var(--shadow-light);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--primary-hover), var(--primary-color));
  box-shadow: var(--shadow-medium);
  transform: translateY(-1px);
}

/* 卡片基础样式 */
.card-base {
  background: var(--background-color);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-light);
  padding: var(--spacing-lg);
  transition: all var(--transition-base);
}

.card-base:hover {
  box-shadow: var(--shadow-medium);
  transform: translateY(-2px);
}

/* 输入框基础样式 */
.input-base {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-medium);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
  outline: none;
  background: var(--background-color);
}

.input-base:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
```

#### 7.2.1 对话组件 (ConversationPanel) - 科技风设计
**设计特色**:
- **消息气泡**: 圆角矩形，用户消息右对齐（科技蓝渐变），AI消息左对齐（浅灰背景）
- **输入框**: 大圆角设计，聚焦时发光效果，支持多行自适应
- **发送按钮**: 圆形按钮，科技蓝渐变，悬停时放大效果
- **状态指示**: 脉冲动画的连接状态灯，处理进度的波浪动画
- **加载状态**: 三个跳跃的圆点动画，体现科技感

**技术实现**:
- 自研消息列表组件：支持富文本、图片、链接等多种消息类型
- 自研智能输入框：支持快捷键、自动补全、表情符号
- 自研状态指示器：WebSocket连接状态、AI处理进度可视化
- 原生CSS动画：流畅的过渡效果和微交互

#### 7.2.2 策略展示组件 (StrategyDisplay) - 数据可视化设计
**设计特色**:
- **信息卡片**: 毛玻璃效果背景，悬停时轻微上浮
- **饼图组件**: Canvas绘制，渐变色彩，悬停时扇区突出显示
- **折线图组件**: SVG绘制，平滑曲线，渐变填充，动画绘制效果
- **数据表格**: 斑马纹背景，悬停行高亮，数字右对齐
- **指标卡片**: 大数字显示，颜色编码（绿色正收益，红色负收益）

**技术实现**:
- 自研Canvas饼图：支持动画、交互、自适应尺寸
- 自研SVG图表：支持缩放、工具提示、数据标记
- 自研数据表格：支持排序、筛选、分页、导出
- 自研指标组件：数字滚动动画、状态颜色变化

#### 7.2.3 历史管理组件 (StrategyHistory) - 列表展示设计
**设计特色**:
- **策略卡片**: 立体卡片设计，左侧彩色边框标识策略类型
- **时间轴**: 垂直时间线，连接各个历史策略
- **操作按钮**: 图标+文字的组合按钮，悬停时颜色变化
- **搜索框**: 带搜索图标的输入框，实时搜索反馈
- **分页器**: 简洁的数字分页，当前页高亮显示

**技术实现**:
- 自研卡片组件：支持展开/折叠、标签分类、状态标识
- 自研时间轴组件：响应式布局、动态加载、无限滚动
- 自研操作组件：权限控制、批量操作、确认对话框
- 自研搜索组件：防抖搜索、历史记录、智能提示

#### 7.2.4 自研组件优势
- **完全可控**：所有组件源码自主开发，无第三方依赖
- **轻量高效**：仅实现必要功能，避免冗余代码
- **定制灵活**：可根据业务需求快速调整和扩展
- **许可证安全**：无第三方许可证风险，支持商业使用

### 7.3 自研组件实现方案（科技风设计系统）

#### 7.3.1 UI组件库替代方案 - 现代科技风格
**替代目标**: 取消Ant Design依赖，自行开发具有科技感的UI组件

**核心组件实现**:
- **按钮组件**: 
  - 渐变背景：线性渐变营造立体感
  - 悬停效果：轻微上浮 + 阴影加深
  - 加载状态：内置loading动画
  - 多种尺寸：small、medium、large
  - 多种类型：primary（渐变蓝）、secondary（边框）、text（纯文字）

- **输入框组件**:
  - 聚焦发光：边框颜色变化 + 外发光效果
  - 状态指示：成功（绿色）、错误（红色）、警告（黄色）
  - 前置图标：支持搜索、用户等图标
  - 自适应高度：textarea自动调整高度

- **卡片组件**:
  - 毛玻璃效果：backdrop-filter实现半透明背景
  - 立体阴影：多层阴影营造浮起效果
  - 悬停动画：transform translateY + 阴影变化
  - 边框渐变：可选的渐变边框效果

- **表格组件**:
  - 斑马纹行：交替行背景色
  - 悬停高亮：行悬停时背景变化
  - 排序图标：可点击的排序指示器
  - 加载骨架：数据加载时的占位动画

- **模态框组件**:
  - 背景模糊：backdrop-filter模糊背景
  - 弹出动画：scale + opacity过渡效果
  - 拖拽支持：可拖拽移动位置
  - 自适应尺寸：根据内容自动调整

- **表单组件**:
  - 实时验证：输入时即时验证反馈
  - 错误提示：动画显示错误信息
  - 成功状态：绿色对勾确认
  - 步骤指示：多步表单的进度条

**样式系统设计**:
- **CSS变量系统**: 完整的设计令牌（颜色、尺寸、动画）
- **主题切换**: 支持亮色/暗色主题切换
- **响应式设计**: 移动端友好的断点系统
- **动画系统**: 统一的过渡动画和微交互
- **图标系统**: SVG图标库，支持多种尺寸和颜色

#### 7.3.2 图表组件替代方案 - 科技感数据可视化
**替代目标**: 取消ECharts依赖，自行开发具有科技感的图表组件

**饼图组件实现**:
- **Canvas绘制**: 高性能的图形渲染
- **渐变配色**: 科技蓝到深蓝的径向渐变
- **动画效果**: 扇区逐个绘制的动画
- **交互体验**: 悬停时扇区突出 + 数据提示框
- **发光效果**: 边缘发光营造科技感
- **数据标签**: 白色文字 + 半透明背景

**曲线图组件实现**:
- **SVG绘制**: 矢量图形，无损缩放
- **平滑曲线**: 使用贝塞尔曲线平滑连接
- **渐变填充**: 曲线下方渐变填充效果
- **网格背景**: 科技感的网格线背景
- **数据点**: 圆形数据点 + 悬停放大效果
- **工具提示**: 跟随鼠标的数据提示框
- **动画绘制**: 曲线从左到右的绘制动画

**数据表格组件**:
- **斑马纹设计**: 交替行的浅色背景
- **悬停效果**: 行悬停时背景高亮
- **排序图标**: 可点击的三角形排序指示器
- **加载状态**: 骨架屏占位动画
- **数字格式**: 自动千分位分隔符
- **状态标识**: 颜色编码的状态指示

**指标卡片组件**:
- **大数字显示**: 突出的数字展示
- **状态颜色**: 绿色（正值）、红色（负值）、蓝色（中性）
- **数字动画**: 数字滚动到目标值的动画
- **图标装饰**: 趋势箭头、百分比符号等
- **背景效果**: 轻微的渐变背景

**实现优势**:
- **科技感十足**: 现代化的视觉设计和交互体验
- **性能优化**: Canvas离屏渲染、SVG元素复用
- **完全自主**: 无第三方图表库的许可证风险
- **轻量高效**: 仅实现业务必需功能，减少bundle体积
- **高度定制**: 可根据业务需求灵活调整样式和功能

#### 7.3.3 状态管理简化方案
**调整内容**: 取消RTK Query，使用自研API缓存

**自研API缓存实现**:
- 基于Map数据结构的内存缓存
- 支持TTL过期机制
- LRU缓存淘汰策略
- 请求去重和防抖处理

**实现方案**:
```typescript
// 自研API缓存管理器
class ApiCacheManager {
  private cache = new Map();
  private ttlMap = new Map();
  
  get(key: string) { /* 缓存获取逻辑 */ }
  set(key: string, data: any, ttl?: number) { /* 缓存设置逻辑 */ }
  invalidate(pattern: string) { /* 缓存失效逻辑 */ }
}
```

**优势**:
- 减少Redux Toolkit的复杂依赖
- 实现轻量级的API状态管理
- 完全可控的缓存策略
- 无额外学习成本

## 8. 智能体系统设计

### 8.1 业务流程作为System提示词

#### 8.1.1 业务流程定义
智能体系统将完整的ETF资产配置业务流程作为system提示词，包括：

**新用户流程**:
- 用户类型判断：识别新用户身份（无保存策略）
- 策略介绍：介绍ETF资产配置策略核心逻辑
- 基准策略展示：展示策略示例和投资理念
- 要素收集：通过对话收集投资偏好和约束条件
- 策略生成：基于要素生成个性化策略
- 策略优化：根据用户反馈进行策略调整

**老用户流程**:
- 历史策略展示：展示用户保存的最佳策略
- 收益追踪：显示策略最新收益表现
- 策略切换：支持用户手动切换策略
- 策略优化：主动提出优化建议
- 要素更新：更新用户投资偏好

#### 7.1.2 流程状态管理
- 流程阶段识别：智能体根据对话内容判断当前流程阶段
- 状态转换规则：定义各阶段间的转换条件和跳转逻辑
- 异常处理：处理用户偏离正常流程的情况
- 流程回退：支持用户返回上一阶段或重新开始

### 8.2 LangChain工具设计

#### 8.2.1 用户身份识别工具
**工具名称**: user_identification_tool
**功能描述**: 识别用户身份类型和历史信息获取
**技术实现**: LangChain Tool + SQLAlchemy + 文件读取
**数据来源**: MySQL用户表 + 用户档案文件
**输入参数**: 用户ID、用户信息
**输出结果**: 用户类型（新用户/老用户）、历史策略列表、用户偏好信息
**调用时机**: 用户登录后、对话开始时

#### 8.2.2 要素提取工具
**工具名称**: element_extraction_tool
**功能描述**: 从对话中提取投资要素和偏好信息
**技术实现**: LangChain Tool + 本地LLM + 文件存储
**数据来源**: 提示词模板文件 + 对话上下文文件
**输入参数**: 对话内容、上下文信息、提示词模板
**输出结果**: 结构化投资要素、置信度评分、更新的用户档案
**调用时机**: 每轮对话结束后、要素更新时

#### 8.2.3 ETF数据获取工具（集成数据补全）
**工具名称**: etf_data_fetch_tool
**功能描述**: 从MySQL数据库获取ETF数据并进行智能补全，提供完整的投资分析信息
**技术实现**: LangChain Tool + SQLAlchemy + 数据补全模块
**数据来源**: MySQL (etf_basic_info, etf_price_data, etf_performance_metrics) + 数据补全算法
**输入参数**: 资产类别、筛选条件、数据范围、大模型查询意图
**输出结果**: 
- 原始ETF数据（Wind数据库字段）
- 补全的分类信息（推导的行业分类、投资主题）
- 生成的投资目标描述
- 估算的估值指标（PE/PB估算值）
- 风险评估和投资建议
**调用时机**: 用户对话触发策略生成时、策略优化时

**数据补全逻辑**:
```python
def fetch_enriched_etf_data(self, query_params: Dict) -> Dict:
    # 1. 获取原始数据
    raw_data = self._fetch_raw_etf_data(query_params)
    
    # 2. 补全分类信息
    for etf in raw_data:
        if not etf.get('category'):  # Wind数据缺失的字段
            classification = derive_etf_classification(etf['etf_name'], etf['etf_code'])
            etf.update(classification)
    
    # 3. 补全投资目标
        if not etf.get('investment_objective'):
            etf['investment_objective'] = generate_investment_objective(etf)
    
    # 4. 补全估值指标
        valuation = estimate_valuation_metrics(etf['etf_code'])
        etf.update(valuation)
    
    return self._format_for_llm(raw_data)
```

#### 8.2.4 策略生成工具
**工具名称**: strategy_generation_tool
**功能描述**: 基于用户对话提取的投资要素生成ETF配置策略
**技术实现**: LangChain Tool + 自研策略算法 + 策略模板文件
**数据来源**: 用户档案文件 + 策略模板文件 + MySQL ETF数据
**输入参数**: 投资要素文件路径、策略模板、约束条件
**输出结果**: 策略配置JSON、投资理念文本、策略文件路径
**调用时机**: 用户对话完成要素收集后、用户要求策略优化时

#### 8.2.5 策略回测工具
**工具名称**: strategy_backtest_tool
**功能描述**: 使用历史数据执行策略回测和性能分析
**技术实现**: LangChain Tool + Celery异步任务
**数据来源**: MySQL历史价格数据 + 策略配置文件
**输入参数**: 策略文件路径、回测期间、基准指数
**输出结果**: 回测结果、性能指标文本、风险评估描述
**调用时机**: 策略生成后、用户要求查看回测结果时

#### 8.2.6 市场资讯获取工具（集成关联性分析）
**工具名称**: market_news_fetch_tool
**功能描述**: 从MySQL数据库获取市场资讯并进行ETF关联性分析，提供投资决策参考
**技术实现**: LangChain Tool + SQLAlchemy + NLP文本分析 + 关联性算法
**数据来源**: MySQL (financial_news, research_reports) + 关联性分析算法
**输入参数**: 资讯类型、时间范围、关键词、目标ETF代码、大模型分析需求
**输出结果**: 
- 原始新闻数据（HTTP获取的基础字段）
- 补全的关联ETF信息（通过文本分析推导）
- 情感倾向评分（正面/负面/中性）
- 投资含义分析（自动生成的投资建议）
- 市场影响评估（对相关ETF的潜在影响）
**调用时机**: 用户对话中主动推荐时、策略优化建议时

**关联性分析逻辑**:
```python
def fetch_enriched_news_data(self, query_params: Dict) -> Dict:
    # 1. 获取原始新闻数据
    raw_news = self._fetch_raw_news_data(query_params)
    
    # 2. 分析新闻与ETF关联性
    etf_list = self._get_etf_universe()
    
    for news in raw_news:
        # 分析关联性
        relevance_analysis = analyze_news_relevance(news['content'], etf_list)
        
        # 补全缺失字段
        news.update({
            'derived_related_etfs': relevance_analysis['related_etfs'],
            'derived_sentiment_score': relevance_analysis['sentiment_score'],
            'derived_investment_implications': relevance_analysis['investment_implications'],
            'derived_market_impact': relevance_analysis['market_impact']
        })
    
    return self._format_news_for_llm(raw_news)
```

#### 8.2.7 策略优化工具
**工具名称**: strategy_optimization_tool
**功能描述**: 根据用户对话反馈优化策略配置
**技术实现**: LangChain Tool + scipy.optimize + 文件操作
**数据来源**: 当前策略文件 + 用户反馈文件 + 优化模板
**输入参数**: 策略文件路径、用户反馈内容、优化目标
**输出结果**: 优化后策略文件、修改说明文本、影响分析报告
**调用时机**: 用户对话中提出修改要求时、主动优化建议时

#### 8.2.8 虚拟板块数据工具
**工具名称**: virtual_sector_data_tool
**功能描述**: 基于ETF分类构建虚拟行业板块数据，提供板块轮动分析依据
**技术实现**: LangChain Tool + 数据聚合算法 + 统计计算
**数据来源**: ETF价格数据 + 分类信息 + 市值权重
**输入参数**: 板块类型、时间范围、分析维度
**输出结果**: 
- 虚拟板块指数数据
- 板块成分ETF列表
- 板块表现排名
- 板块轮动建议
**调用时机**: 策略生成时需要板块配置建议、用户询问板块表现时

**虚拟板块构建逻辑**:
```python
def build_virtual_sector_data(self, sector_type: str, date_range: str) -> Dict:
    # 1. 获取相关ETF数据
    etf_data = self._get_etfs_by_sector(sector_type)
    
    # 2. 计算板块加权指数
    sector_index = self._calculate_sector_index(etf_data, date_range)
    
    # 3. 分析板块表现
    performance_analysis = self._analyze_sector_performance(sector_index)
    
    return {
        'sector_name': f"{sector_type}板块",
        'index_data': sector_index,
        'constituent_etfs': [etf['etf_code'] for etf in etf_data],
        'performance_metrics': performance_analysis,
        'investment_suggestion': self._generate_sector_suggestion(performance_analysis)
    }
```

#### 8.2.9 文件管理工具
**工具名称**: file_management_tool
**功能描述**: 管理用户档案和会话文件的读写操作
**技术实现**: LangChain Tool + pathlib + json/yaml
**数据来源**: 本地文件系统
**输入参数**: 文件路径、操作类型、数据内容
**输出结果**: 文件操作结果、文件内容、错误信息
**调用时机**: 需要读写用户档案、会话记录、配置文件时

#### 8.2.9 内容安全审查工具
**工具名称**: content_safety_check_tool
**功能描述**: 对大模型生成的内容进行安全审查和合规性检查
**技术实现**: LangChain Tool + 自研安全审查算法
**数据来源**: 安全规则配置文件 + 敏感词库文件
**输入参数**: 待审查内容、内容类型、审查级别
**输出结果**: 安全评分、违规信息、处理后内容、合规建议
**调用时机**: 每次大模型生成内容后、内容发布前

### 8.3 任务规划机制（集成安全审查）

#### 8.3.1 任务规划生成
智能体根据以下信息生成任务规划：
- 当前业务流程阶段
- 用户最新对话内容和需求
- 对话上下文和历史信息
- 对话触发的数据需求
- 内容安全审查要求

#### 8.3.2 任务规划结构（包含安全审查）
**任务规划包含**:
- 任务目标：当前需要完成的主要目标
- 工具调用序列：需要调用的LangChain Tools及其顺序
- 安全审查节点：在关键生成节点插入安全审查
- 数据依赖关系：各工具间的数据依赖关系
- 预期输出：任务完成后的预期结果
- 异常处理：可能的异常情况和处理方案
- 安全保障：内容安全检查和合规性验证

#### 8.3.3 任务执行流程（包含安全审查）
1. **任务解析**: 解析用户需求，确定任务目标
2. **输入安全检查**: 对用户输入进行安全预检查
3. **工具选择**: 根据任务目标选择合适的LangChain Tools
4. **参数准备**: 准备工具调用所需的参数
5. **工具执行**: 通过LangGraph按顺序执行选定的工具
6. **内容安全审查**: 对生成内容进行安全性检查
7. **合规性处理**: 添加免责声明和风险提示
8. **结果汇总**: 汇总各工具的执行结果
9. **最终审查**: 对最终回复进行安全复查
10. **安全发布**: 发布通过审查的安全内容

### 8.4 实时状态更新机制

#### 8.4.1 状态更新类型
**处理状态**:
- 思考中：智能体正在分析用户对话内容和规划任务
- 安全检查中：正在对用户输入进行安全预检查
- 数据获取中：正在调用工具获取对话相关的数据
- 策略生成中：正在基于对话内容生成或优化策略
- 回测计算中：正在执行策略回测
- 内容审查中：正在对生成内容进行安全审查
- 合规处理中：正在添加免责声明和风险提示
- 结果汇总中：正在汇总结果生成回复

**中间结果**:
- 安全检查结果：显示输入内容的安全检查状态
- 要素提取结果：显示从对话中提取的投资要素
- 数据获取进度：显示对话触发的数据获取进度和状态
- 策略生成进度：显示基于对话内容的策略生成中间步骤
- 回测计算进度：显示回测计算的进度和中间结果
- 安全审查进度：显示内容安全审查的进度和结果

#### 8.4.2 状态推送机制
- **WebSocket推送**: 实时向前端推送状态更新
- **状态缓存**: 将状态信息缓存到Redis
- **状态持久化**: 将重要状态保存到数据库
- **状态同步**: 确保多实例间的状态同步

#### 8.4.3 用户体验优化
- **进度指示器**: 显示当前处理进度和预计完成时间
- **中间结果展示**: 展示处理过程中的中间结果
- **状态说明**: 提供状态变化的文字说明
- **取消机制**: 允许用户取消当前处理任务

## 9. 技术栈总结

### 9.1 核心技术栈对比

| 技术分类 | 选择方案 | 许可证 | 商业使用 | 选择理由 |
|---------|---------|--------|---------|---------|
| **前端框架** | React 18 + TypeScript | MIT | ✅ 免费商用 | 生态成熟，企业级应用广泛 |
| **状态管理** | Redux Toolkit | MIT | ✅ 免费商用 | 官方推荐，功能完善 |
| **UI组件库** | 自研组件库 | 自主开发 | ✅ 完全可控 | 避免第三方依赖，代码可控 |
| **图表库** | 自研图表组件 | 自主开发 | ✅ 完全可控 | Canvas/SVG实现，满足需求 |
| **构建工具** | Vite | MIT | ✅ 免费商用 | 构建速度快，开发体验好 |
| **样式方案** | CSS Modules + 原生CSS | 标准技术 | ✅ 免费使用 | 模块化，无外部依赖 |
| **路由管理** | React Router v6 | MIT | ✅ 免费商用 | 官方推荐路由方案 |
| **后端框架** | FastAPI + Python | MIT | ✅ 免费商用 | 高性能异步，自动API文档 |
| **AI框架** | LangChain + LangGraph | MIT | ✅ 免费商用 | 成熟AI应用开发框架 |
| **数据库** | MySQL 8.0+ | GPL/商业双许可 | ✅ 免费商用 | 性能优秀，支持JSON字段 |
| **ORM** | SQLAlchemy + Alembic | MIT | ✅ 免费商用 | 功能强大，支持迁移 |
| **缓存** | Redis | BSD | ✅ 免费商用 | 功能丰富，支持多种数据结构 |
| **任务队列** | Celery + Redis | BSD | ✅ 免费商用 | 分布式任务队列，功能完善 |
| **容器化** | Docker + Docker Compose | Apache 2.0 | ✅ 免费商用 | 生态成熟，文档完善 |

### 9.2 技术栈优势

#### 9.2.1 许可证安全
- 所有核心技术栈都使用MIT、BSD、Apache等商业友好许可证
- 无GPL等限制性开源协议，支持商业开发和使用
- 自研组件完全自主可控，无许可证风险
- 源代码透明，安全性可控

#### 9.2.2 成本控制
- 核心技术栈完全开源免费，无商业许可费用
- 自研UI组件和图表组件，避免第三方许可费用
- 降低项目总体拥有成本（TCO）
- 无厂商锁定风险

#### 9.2.3 代码可控性
- 自研UI组件库，完全掌控界面逻辑和样式
- 自研图表组件，满足特定业务需求
- 减少外部依赖，降低供应链安全风险
- 便于定制化开发和功能扩展

#### 9.2.4 性能优化
- 前端使用Vite构建，开发体验优秀
- 自研组件轻量化，减少包体积
- 后端使用FastAPI，异步处理能力强
- 数据库使用MySQL，查询性能优秀
- 缓存使用Redis，响应速度快

#### 9.2.5 技术成熟度
- React、FastAPI等核心框架经过市场验证
- 社区活跃，文档完善，问题解决容易
- 版本稳定，长期支持，适合商业项目
- 技术栈学习成本低，人才储备充足

#### 9.2.6 扩展性强
- 模块化设计，易于扩展和维护
- 自研组件可根据业务需求灵活调整
- 支持微服务架构演进
- 支持容器化和云原生部署

### 9.3 技术栈调整说明

#### 9.3.1 自研组件替代策略
为确保项目的商业安全性和代码可控性，技术方案采用以下替代策略：

**前端UI组件替代**:
- **原方案**: Ant Design (虽然MIT许可证，但增加外部依赖)
- **调整方案**: 自研UI组件库
- **替代理由**: 减少外部依赖，提高代码可控性，避免潜在的许可证风险

**图表组件替代**:
- **原方案**: ECharts (Apache 2.0许可证，支持商业使用)
- **调整方案**: 自研Canvas/SVG图表组件
- **替代理由**: 项目仅需基础图表功能，自研实现更轻量化

**API缓存替代**:
- **原方案**: RTK Query (MIT许可证，但功能复杂)
- **调整方案**: 自研API缓存管理器
- **替代理由**: 项目缓存需求简单，自研实现更符合业务需求

#### 9.3.2 保留的开源技术栈
以下技术栈因为核心功能重要且许可证安全而保留：

**核心框架**: React 18 + TypeScript (MIT许可证)
**状态管理**: Redux Toolkit (MIT许可证)
**构建工具**: Vite (MIT许可证)
**路由管理**: React Router v6 (MIT许可证)
**后端框架**: FastAPI + Python (MIT许可证)
**数据库**: MySQL + Redis (GPL/BSD许可证，商业友好)
**AI框架**: LangChain + LangGraph (MIT许可证)

#### 9.3.3 技术栈最终优势
- **许可证安全**: 所有技术栈都确认支持商业使用
- **依赖最小化**: 减少不必要的第三方依赖
- **代码可控**: 核心UI和图表组件完全自主开发
- **成本优化**: 无任何商业许可费用
- **维护性强**: 自研组件便于维护和定制

## 10. 大模型内容安全审查

### 10.1 内容安全审查机制

#### 10.1.1 安全审查目标
确保大模型生成的所有内容符合法律法规要求，维护系统的合规性和安全性。

**审查范围**:
- 大模型生成的所有对话回复
- 投资策略建议和分析内容
- 市场资讯解读和投资建议
- 风险提示和免责声明
- 用户交互过程中的所有AI生成内容

**审查标准**:
- 禁止NSFW（Not Safe For Work）内容
- 禁止政治倾向性言论和敏感政治话题
- 禁止违法违规的投资建议
- 禁止误导性或虚假的市场信息
- 禁止歧视性或不当的表达内容

#### 10.1.2 多层次安全审查架构

**第一层：输入内容预检查**
- 用户输入内容关键词过滤
- 敏感话题识别和拦截
- 非投资相关内容引导
- 恶意输入检测和防护

**第二层：大模型输出审查**
- 生成内容实时安全扫描
- 关键词黑名单匹配
- 语义安全性分析
- 合规性自动检测

**第三层：内容发布前复审**
- 重要内容人工复审机制
- 投资建议合规性检查
- 免责声明自动添加
- 内容版本控制和追溯

### 10.2 安全审查技术实现

#### 10.2.1 内容过滤系统

**敏感词库管理**:
- 政治敏感词库：涉及政治立场、政府政策评价等
- NSFW内容词库：不适宜工作场所的内容
- 金融违规词库：违法金融活动、虚假宣传等
- 歧视性词库：种族、性别、地域歧视等

**过滤规则配置** (`config/content_safety.yaml`):
```yaml
content_safety_rules:
  blocked_keywords:
    political:
      - "政治立场相关词汇"
      - "敏感政治话题"
    nsfw:
      - "不适宜内容关键词"
    financial_violations:
      - "保证收益"
      - "无风险高收益"
      - "内幕消息"
    
  warning_keywords:
    investment_risk:
      - "投资有风险"
      - "市场波动"
      - "历史业绩不代表未来"
      
  replacement_rules:
    inappropriate_content:
      original: "违规表达"
      replacement: "合规替代表达"
```

#### 10.2.2 安全审查服务

**技术实现**:
- **框架**: 自研内容安全审查模块
- **算法**: 关键词匹配 + 语义分析 + 规则引擎
- **存储**: 审查规则文件 + 审查日志数据库
- **性能**: 异步处理 + 缓存优化

**审查流程**:
1. **预处理**: 文本标准化和分词处理
2. **关键词检测**: 敏感词库匹配检查
3. **语义分析**: 使用轻量级模型进行语义安全分析
4. **规则匹配**: 应用预定义的安全规则
5. **结果判定**: 通过/警告/拒绝/需人工审核
6. **内容处理**: 自动修正或要求重新生成

#### 10.2.3 安全审查工具

**内容安全审查工具**:
```python
class ContentSafetyChecker:
    """内容安全审查器"""
    
    def __init__(self):
        self.blocked_keywords = self._load_blocked_keywords()
        self.safety_rules = self._load_safety_rules()
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """检查内容安全性"""
        return {
            "is_safe": True/False,
            "risk_level": "low/medium/high",
            "violations": [],
            "suggestions": [],
            "processed_content": "处理后的安全内容"
        }
    
    def add_compliance_disclaimer(self, content: str) -> str:
        """添加合规免责声明"""
        
    def sanitize_investment_advice(self, advice: str) -> str:
        """净化投资建议内容"""
```

### 10.3 合规性保障措施

#### 10.3.1 投资建议合规性

**投资建议规范**:
- 所有投资建议必须包含风险提示
- 禁止保证收益的表述
- 明确历史业绩不代表未来表现
- 强调投资者适当性原则
- 建议用户根据自身情况决策

**标准免责声明**:
```text
【风险提示】本内容仅为投资策略建议，不构成具体的投资推荐。
投资有风险，入市需谨慎。历史业绩不代表未来表现，请根据
自身风险承受能力谨慎决策。
```

**合规性检查点**:
- 避免绝对化表述（"一定"、"必然"等）
- 避免夸大收益预期
- 避免淡化风险提示
- 避免诱导性投资建议
- 避免时间紧迫性压力表述

#### 10.3.2 内容审查流程

**实时审查流程**:
1. **输入检查**: 用户输入内容安全预检
2. **生成监控**: 大模型生成过程实时监控
3. **输出审查**: 生成内容安全性检查
4. **合规处理**: 添加免责声明和风险提示
5. **发布控制**: 安全内容发布，违规内容拦截

**人工复审机制**:
- 高风险内容触发人工审核
- 定期抽查大模型生成内容
- 用户投诉内容专项审查
- 审查规则定期更新优化

#### 10.3.3 安全日志和监控

**安全日志记录**:
- 记录所有内容审查结果
- 追踪违规内容和处理措施
- 监控审查规则的触发频率
- 分析内容安全趋势和模式

**监控指标**:
- 内容安全通过率
- 违规内容类型分布
- 审查响应时间
- 人工复审工作量

### 10.4 技术实现架构

#### 10.4.1 安全审查模块集成

**模块位置**: `app/safety/`
- `content_checker.py` - 内容安全检查器
- `keyword_filter.py` - 关键词过滤器
- `compliance_manager.py` - 合规性管理器
- `safety_config.py` - 安全配置管理
- `audit_logger.py` - 审查日志记录器

**集成到智能体流程**:
```python
# 在智能体核心模块中集成安全审查
class AgentCore:
    def __init__(self):
        self.content_checker = ContentSafetyChecker()
    
    async def process_conversation(self, message: str) -> str:
        # 1. 输入内容安全检查
        input_check = self.content_checker.check_input_safety(message)
        if not input_check["is_safe"]:
            return "抱歉，您的输入包含不当内容，请重新表述。"
        
        # 2. 大模型生成内容
        response = await self.generate_response(message)
        
        # 3. 输出内容安全审查
        output_check = self.content_checker.check_content_safety(response)
        if not output_check["is_safe"]:
            # 重新生成或使用安全的替代回复
            response = self.get_safe_fallback_response()
        
        # 4. 添加合规声明
        final_response = self.content_checker.add_compliance_disclaimer(response)
        
        return final_response
```

#### 10.4.2 配置文件设计

**安全配置文件** (`config/content_safety.yaml`):
```yaml
content_safety:
  # 敏感词库配置
  keyword_filters:
    political_sensitive:
      enabled: true
      severity: "high"
      action: "block"
      keywords_file: "keywords/political.txt"
    
    nsfw_content:
      enabled: true
      severity: "high" 
      action: "block"
      keywords_file: "keywords/nsfw.txt"
    
    financial_violations:
      enabled: true
      severity: "medium"
      action: "warn_and_modify"
      keywords_file: "keywords/financial_violations.txt"
  
  # 合规性规则
  compliance_rules:
    investment_advice:
      require_risk_warning: true
      require_disclaimer: true
      max_return_promise: null
      forbidden_guarantees: ["保证收益", "无风险", "稳赚不赔"]
    
    market_analysis:
      require_objectivity: true
      avoid_absolute_statements: true
      require_data_source: true
  
  # 审查配置
  review_settings:
    auto_review_threshold: 0.8
    human_review_threshold: 0.6
    content_cache_ttl: 3600
    audit_log_retention: 90  # 天
```

### 10.5 内容安全保障体系

#### 10.5.1 预防性措施

**系统级预防**:
- 大模型训练数据清洗和过滤
- 提示词工程中加入安全约束
- 输出模板规范化设计
- 定期安全评估和测试

**业务级预防**:
- 投资建议标准化模板
- 风险提示自动添加机制
- 免责声明标准化管理
- 用户教育和风险揭示

#### 10.5.2 响应性措施

**实时响应**:
- 违规内容立即拦截
- 安全内容自动放行
- 可疑内容标记审查
- 用户反馈快速处理

**事后处理**:
- 违规内容追溯分析
- 审查规则持续优化
- 安全事件应急响应
- 合规培训和改进

#### 10.5.3 监管合规

**法律法规遵循**:
- 遵守《网络安全法》相关规定
- 符合金融监管部门要求
- 遵循投资顾问业务规范
- 满足数据保护法律要求

**行业标准对标**:
- 参考金融行业内容审查标准
- 对标头部金融科技公司实践
- 遵循AI伦理和安全指导原则
- 建立内容安全最佳实践

### 10.6 安全审查技术架构

#### 10.6.1 安全审查服务架构

```
用户输入 → 输入安全检查 → 大模型处理 → 输出安全审查 → 合规处理 → 用户展示
    ↓           ↓             ↓           ↓          ↓
 敏感词过滤   内容预检查    生成监控    违规拦截   免责声明
    ↓           ↓             ↓           ↓          ↓
 拦截/警告   引导重述      重新生成    安全替代   合规发布
```

#### 10.6.2 安全数据库设计

**内容审查日志表 (content_audit_logs)**:
- id: 主键，自增整数
- user_id: 用户ID
- session_id: 会话ID
- content_type: 内容类型（input/output/generated）
- original_content: 原始内容
- processed_content: 处理后内容
- safety_score: 安全评分（0-1）
- violation_types: 违规类型（JSON数组）
- action_taken: 采取的措施
- reviewer_id: 审查员ID（如果人工审查）
- review_result: 审查结果
- created_at: 审查时间

**安全规则配置表 (safety_rules)**:
- id: 主键，自增整数
- rule_name: 规则名称
- rule_type: 规则类型（keyword/semantic/compliance）
- rule_content: 规则内容（JSON格式）
- severity_level: 严重程度（low/medium/high/critical）
- action_type: 处理动作（block/warn/modify/review）
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间

#### 10.6.3 安全监控和告警

**实时监控指标**:
- 内容安全通过率
- 违规内容拦截率
- 人工审查工作量
- 安全事件响应时间

**告警机制**:
- 违规内容超阈值告警
- 安全规则失效告警
- 异常行为模式告警
- 系统安全状态监控

### 10.7 安全审查实施方案

#### 10.7.1 开发阶段安全措施

**代码层面**:
- 在所有大模型调用点集成安全审查
- 实现安全审查中间件
- 建立内容安全测试用例
- 代码安全审查和评估

**配置层面**:
- 建立完善的安全配置文件
- 实现安全规则热更新机制
- 建立安全配置版本控制
- 定期安全配置审查

#### 10.7.2 部署阶段安全保障

**部署安全**:
- 安全配置文件加密存储
- 敏感词库访问权限控制
- 审查日志安全存储
- 安全备份和恢复机制

**运维安全**:
- 定期安全评估和测试
- 安全事件应急响应预案
- 安全培训和意识提升
- 第三方安全审计

#### 10.7.3 持续改进机制

**规则优化**:
- 基于审查结果优化规则
- 新增安全场景的规则扩展
- 误报和漏报的规则调整
- 行业最佳实践的规则更新

**技术升级**:
- 安全检测算法持续优化
- 新技术在安全审查中的应用
- 性能优化和响应速度提升
- 安全审查准确性持续改进

---

*本技术方案基于需求文档分析制定，采用成熟、开源、商业友好的技术栈，通过自研组件替代策略和完善的内容安全审查机制，确保项目的稳定性、可维护性、扩展性、商业安全性和内容合规性。可根据实际开发过程中的反馈进行调整和优化。*
