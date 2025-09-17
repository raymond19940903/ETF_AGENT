"""策略模型"""
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import Base


class Strategy(Base):
    """策略表"""
    __tablename__ = "strategies"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(100), nullable=False, comment="策略名称")
    description = Column(Text, nullable=True, comment="策略描述")
    investment_philosophy = Column(Text, nullable=True, comment="投资理念")
    
    # 策略参数
    target_return = Column(Float, nullable=True, comment="目标收益率")
    max_drawdown = Column(Float, nullable=True, comment="最大回撤")
    risk_level = Column(String(20), nullable=True, comment="风险等级")
    rebalance_frequency = Column(String(20), nullable=True, comment="再平衡频率")
    investment_amount = Column(Float, nullable=True, comment="投资金额")
    
    # 策略配置（JSON格式存储）
    asset_allocation = Column(JSON, nullable=True, comment="资产配置")
    constraints = Column(JSON, nullable=True, comment="约束条件")
    preferences = Column(JSON, nullable=True, comment="用户偏好")
    
    # 策略状态
    status = Column(String(20), default="active", nullable=False, comment="策略状态")
    
    # 关联关系
    user = relationship("User", back_populates="strategies")
    etf_allocations = relationship("StrategyETFAllocation", back_populates="strategy", cascade="all, delete-orphan")
    backtest_data = relationship("StrategyBacktestData", back_populates="strategy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name}, user_id={self.user_id})>"


class StrategyETFAllocation(Base):
    """策略ETF配置表"""
    __tablename__ = "strategy_etf_allocations"
    
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    etf_code = Column(String(20), nullable=False, comment="ETF代码")
    etf_name = Column(String(100), nullable=False, comment="ETF名称")
    allocation_percentage = Column(Float, nullable=False, comment="配置比例")
    asset_class = Column(String(50), nullable=True, comment="资产类别")
    sector = Column(String(50), nullable=True, comment="行业板块")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="etf_allocations")
    
    def __repr__(self):
        return f"<StrategyETFAllocation(strategy_id={self.strategy_id}, etf_code={self.etf_code}, allocation={self.allocation_percentage})>"


# 创建索引
Index('idx_strategies_user_id', Strategy.user_id)
Index('idx_strategies_status', Strategy.status)
Index('idx_strategy_etf_allocations_strategy_id', StrategyETFAllocation.strategy_id)
Index('idx_strategy_etf_allocations_etf_code', StrategyETFAllocation.etf_code)
