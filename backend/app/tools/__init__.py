"""LangChain工具模块 - 集成数据补全和安全审查"""
from .base_tool import BaseETFTool
from .user_identification import UserIdentificationTool
from .element_extraction import ElementExtractionTool
from .etf_data_fetch import ETFDataFetchTool
from .strategy_generation import StrategyGenerationTool
from .strategy_backtest import StrategyBacktestTool
from .market_news_fetch import MarketNewsFetchTool
from .strategy_optimization import StrategyOptimizationTool
from .virtual_sector_data import VirtualSectorDataTool

__all__ = [
    "BaseETFTool",
    "UserIdentificationTool",
    "ElementExtractionTool", 
    "ETFDataFetchTool",
    "StrategyGenerationTool",
    "StrategyBacktestTool",
    "MarketNewsFetchTool",
    "StrategyOptimizationTool",
    "VirtualSectorDataTool"
]

def get_all_tools(db_session):
    """获取所有可用的LangChain工具"""
    return [
        UserIdentificationTool(db_session),
        ElementExtractionTool(db_session),
        ETFDataFetchTool(db_session),
        StrategyGenerationTool(db_session),
        StrategyBacktestTool(db_session),
        MarketNewsFetchTool(db_session),
        StrategyOptimizationTool(db_session),
        VirtualSectorDataTool(db_session)
    ]
