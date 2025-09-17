"""策略相关数据模型"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ETFAllocationRequest(BaseModel):
    """ETF配置请求模型"""
    etf_code: str = Field(..., description="ETF代码")
    etf_name: str = Field(..., description="ETF名称")
    weight: float = Field(..., ge=0, le=100, description="配置权重")
    asset_class: Optional[str] = Field(None, description="资产类别")
    sector: Optional[str] = Field(None, description="行业板块")


class StrategyCreateRequest(BaseModel):
    """策略创建请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    investment_philosophy: Optional[str] = Field(None, description="投资理念")
    target_return: Optional[float] = Field(None, ge=0, le=100, description="目标收益率")
    max_drawdown: Optional[float] = Field(None, ge=0, le=100, description="最大回撤")
    risk_level: Optional[str] = Field("稳健", description="风险等级")
    investment_amount: Optional[float] = Field(None, ge=0, description="投资金额")
    rebalance_frequency: Optional[str] = Field("季度", description="再平衡频率")
    etf_allocations: List[ETFAllocationRequest] = Field(..., description="ETF配置列表")
    asset_allocation: Optional[Dict[str, float]] = Field(None, description="资产配置汇总")
    constraints: Optional[Dict[str, Any]] = Field(None, description="约束条件")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")


class StrategyUpdateRequest(BaseModel):
    """策略更新请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    investment_philosophy: Optional[str] = Field(None, description="投资理念")
    target_return: Optional[float] = Field(None, ge=0, le=100, description="目标收益率")
    max_drawdown: Optional[float] = Field(None, ge=0, le=100, description="最大回撤")
    risk_level: Optional[str] = Field(None, description="风险等级")
    investment_amount: Optional[float] = Field(None, ge=0, description="投资金额")
    etf_allocations: Optional[List[ETFAllocationRequest]] = Field(None, description="ETF配置列表")
    asset_allocation: Optional[Dict[str, float]] = Field(None, description="资产配置汇总")


class ETFAllocationResponse(BaseModel):
    """ETF配置响应模型"""
    etf_code: str
    etf_name: str
    weight: float
    asset_class: Optional[str]
    sector: Optional[str]
    allocation_percentage: float


class PerformanceMetrics(BaseModel):
    """绩效指标模型"""
    total_return: Optional[float] = None
    annual_return: Optional[float] = None
    volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    expected_annual_return: Optional[float] = None
    expected_volatility: Optional[float] = None
    expected_max_drawdown: Optional[float] = None
    expected_sharpe_ratio: Optional[float] = None
    confidence_level: Optional[float] = None


class StrategyResponse(BaseModel):
    """策略响应模型"""
    id: int
    name: str
    description: Optional[str]
    investment_philosophy: Optional[str]
    target_return: Optional[float]
    max_drawdown: Optional[float]
    risk_level: Optional[str]
    investment_amount: Optional[float]
    rebalance_frequency: Optional[str]
    status: str
    created_at: str
    updated_at: str
    etf_allocations: List[ETFAllocationResponse]
    asset_allocation: Optional[Dict[str, float]]
    performance_estimates: Optional[PerformanceMetrics]
    
    class Config:
        from_attributes = True


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_id: int = Field(..., description="策略ID")
    backtest_period: int = Field(365, ge=30, le=1825, description="回测期间（天）")
    benchmark_index: str = Field("000300.SH", description="基准指数")


class BacktestDataPoint(BaseModel):
    """回测数据点模型"""
    date: str
    daily_return: float
    cumulative_return: float
    portfolio_value: float


class BacktestResponse(BaseModel):
    """回测响应模型"""
    strategy_id: int
    backtest_period: str
    performance_metrics: PerformanceMetrics
    daily_data: List[BacktestDataPoint]
    benchmark_comparison: Optional[Dict[str, Any]] = None


class StrategyOptimizationRequest(BaseModel):
    """策略优化请求模型"""
    strategy_id: int = Field(..., description="策略ID")
    user_feedback: Dict[str, Any] = Field(..., description="用户反馈")
    optimization_target: str = Field("user_satisfaction", description="优化目标")


class StrategyOptimizationResponse(BaseModel):
    """策略优化响应模型"""
    success: bool
    optimized_strategy: Optional[StrategyResponse]
    changes_summary: List[str]
    optimization_reason: Dict[str, Any]
