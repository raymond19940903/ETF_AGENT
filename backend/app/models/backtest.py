"""回测数据模型"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, JSON, Index
from sqlalchemy.orm import relationship
from .base import Base


class StrategyBacktestData(Base):
    """策略回测数据表"""
    __tablename__ = "strategy_backtest_data"
    
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    backtest_date = Column(Date, nullable=False, comment="回测日期")
    
    # 收益数据
    daily_return = Column(Float, nullable=True, comment="日收益率")
    cumulative_return = Column(Float, nullable=True, comment="累计收益率")
    portfolio_value = Column(Float, nullable=True, comment="组合价值")
    
    # 风险指标
    volatility = Column(Float, nullable=True, comment="波动率")
    max_drawdown = Column(Float, nullable=True, comment="最大回撤")
    sharpe_ratio = Column(Float, nullable=True, comment="夏普比率")
    
    # 基准对比
    benchmark_return = Column(Float, nullable=True, comment="基准收益率")
    excess_return = Column(Float, nullable=True, comment="超额收益")
    
    # 详细数据（JSON格式）
    holdings_data = Column(JSON, nullable=True, comment="持仓数据")
    performance_metrics = Column(JSON, nullable=True, comment="绩效指标")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="backtest_data")
    
    def __repr__(self):
        return f"<StrategyBacktestData(strategy_id={self.strategy_id}, date={self.backtest_date}, return={self.daily_return})>"


# 创建索引
Index('idx_strategy_backtest_data_strategy_id', StrategyBacktestData.strategy_id)
Index('idx_strategy_backtest_data_date', StrategyBacktestData.backtest_date)
Index('idx_strategy_backtest_data_strategy_date', StrategyBacktestData.strategy_id, StrategyBacktestData.backtest_date)
