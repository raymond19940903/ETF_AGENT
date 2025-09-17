"""ETF产品模型 - 适配Wind数据库字段"""
from sqlalchemy import Column, String, Float, Text, Date, Index, Integer
from .base import Base


class ETFBasicInfo(Base):
    """ETF基础信息表 - 基于Wind数据库可获取字段"""
    __tablename__ = "etf_basic_info"
    
    etf_code = Column(String(20), unique=True, nullable=False, index=True, comment="ETF代码")
    etf_name = Column(String(100), nullable=False, comment="ETF名称") 
    full_name = Column(String(200), nullable=True, comment="ETF全称")
    asset_class = Column(String(50), nullable=True, comment="资产类别")
    investment_type = Column(String(50), nullable=True, comment="投资类型")
    fund_company = Column(String(100), nullable=True, comment="基金公司")
    listing_date = Column(Date, nullable=True, comment="上市日期")
    fund_scale = Column(Float, nullable=True, comment="基金规模（万元）")
    status = Column(String(20), default="active", nullable=False, comment="状态")
    
    def __repr__(self):
        return f"<ETFBasicInfo(id={self.id}, code={self.etf_code}, name={self.etf_name})>"


class ETFPriceData(Base):
    """ETF价格数据表 - 基于Wind数据库可获取字段"""
    __tablename__ = "etf_price_data"
    
    etf_code = Column(String(20), nullable=False, index=True, comment="ETF代码")
    trade_date = Column(Date, nullable=False, comment="交易日期")
    open_price = Column(Float, nullable=True, comment="开盘价")
    close_price = Column(Float, nullable=False, comment="收盘价")
    high_price = Column(Float, nullable=True, comment="最高价")
    low_price = Column(Float, nullable=True, comment="最低价")
    volume = Column(Integer, nullable=True, comment="成交量")
    turnover = Column(Float, nullable=True, comment="成交额(千元)")
    
    def __repr__(self):
        return f"<ETFPriceData(etf_code={self.etf_code}, date={self.trade_date})>"


class ETFPerformanceMetrics(Base):
    """ETF绩效指标表 - 基于Wind数据库可获取字段"""
    __tablename__ = "etf_performance_metrics"
    
    etf_code = Column(String(20), nullable=False, index=True, comment="ETF代码")
    period_start_date = Column(Date, nullable=False, comment="统计开始日期")
    period_end_date = Column(Date, nullable=False, comment="统计结束日期")
    total_return = Column(Float, nullable=True, comment="总收益率（%）")
    annualized_return = Column(Float, nullable=True, comment="年化收益率（%）")
    volatility = Column(Float, nullable=True, comment="波动率（%）")
    max_drawdown = Column(Float, nullable=True, comment="最大回撤（%）")
    sharpe_ratio = Column(Float, nullable=True, comment="夏普比率")
    sortino_ratio = Column(Float, nullable=True, comment="索提诺比率")
    calmar_ratio = Column(Float, nullable=True, comment="卡尔玛比率")
    win_rate = Column(Float, nullable=True, comment="胜率（%）")
    beta = Column(Float, nullable=True, comment="贝塔系数")
    alpha = Column(Float, nullable=True, comment="阿尔法系数")
    information_ratio = Column(Float, nullable=True, comment="信息比率")
    performance_summary = Column(Text, nullable=True, comment="绩效总结（便于大模型理解）")
    risk_assessment = Column(Text, nullable=True, comment="风险评估（文本描述）")
    data_source = Column(String(50), default="Wind", comment="数据来源")
    
    def __repr__(self):
        return f"<ETFPerformanceMetrics(etf_code={self.etf_code}, period={self.period_start_date}-{self.period_end_date})>"


class MarketIndexData(Base):
    """市场指数数据表 - 基于Wind数据库可获取字段"""
    __tablename__ = "market_index_data"
    
    index_code = Column(String(20), nullable=False, index=True, comment="指数代码")
    index_name = Column(String(100), nullable=False, comment="指数名称")
    trade_date = Column(Date, nullable=False, comment="交易日期")
    open_value = Column(Float, nullable=True, comment="开盘点位")
    close_value = Column(Float, nullable=False, comment="收盘点位")
    high_value = Column(Float, nullable=True, comment="最高点位")
    low_value = Column(Float, nullable=True, comment="最低点位")
    volume = Column(Integer, nullable=True, comment="成交量")
    turnover = Column(Float, nullable=True, comment="成交额(千元)")
    
    def __repr__(self):
        return f"<MarketIndexData(index_code={self.index_code}, date={self.trade_date})>"


class FinancialNews(Base):
    """财经新闻表 - 基于HTTP API可获取字段"""
    __tablename__ = "financial_news"
    
    news_id = Column(String(50), unique=True, nullable=False, comment="新闻唯一标识")
    title = Column(String(200), nullable=False, comment="新闻标题")
    summary = Column(Text, nullable=True, comment="新闻摘要")
    content = Column(Text, nullable=True, comment="新闻正文")
    author = Column(String(50), nullable=True, comment="作者")
    source = Column(String(50), nullable=True, comment="新闻来源")
    
    def __repr__(self):
        return f"<FinancialNews(id={self.id}, title={self.title[:20]}...)>"


class ResearchReports(Base):
    """研究报告表 - 基于HTTP API可获取字段"""
    __tablename__ = "research_reports"
    
    report_id = Column(String(50), unique=True, nullable=False, comment="报告唯一标识")
    title = Column(String(200), nullable=False, comment="报告标题")
    abstract = Column(Text, nullable=True, comment="报告摘要")
    institution = Column(String(100), nullable=True, comment="研究机构")
    analyst = Column(String(50), nullable=True, comment="分析师")
    report_type = Column(String(50), nullable=True, comment="报告类型")
    key_points = Column(Text, nullable=True, comment="核心观点（JSON数组）")
    data_source = Column(String(50), nullable=True, comment="数据来源")
    
    def __repr__(self):
        return f"<ResearchReports(id={self.id}, title={self.title[:20]}...)>"


# 创建索引
Index('idx_etf_basic_info_code', ETFBasicInfo.etf_code)
Index('idx_etf_basic_info_asset_class', ETFBasicInfo.asset_class)
Index('idx_etf_basic_info_fund_company', ETFBasicInfo.fund_company)
Index('idx_etf_price_data_code_date', ETFPriceData.etf_code, ETFPriceData.trade_date)
Index('idx_etf_performance_code_period', ETFPerformanceMetrics.etf_code, ETFPerformanceMetrics.period_start_date)
Index('idx_market_index_code_date', MarketIndexData.index_code, MarketIndexData.trade_date)
Index('idx_financial_news_source', FinancialNews.source)
Index('idx_research_reports_institution', ResearchReports.institution)
