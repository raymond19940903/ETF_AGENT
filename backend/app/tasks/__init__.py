"""异步任务模块"""
from .celery_app import celery_app
from .strategy_tasks import run_strategy_backtest, generate_strategy_async
from .data_tasks import sync_etf_data, fetch_market_news

__all__ = [
    "celery_app",
    "run_strategy_backtest", 
    "generate_strategy_async",
    "sync_etf_data",
    "fetch_market_news"
]
