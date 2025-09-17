"""策略回测工具"""
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StrategyBacktestInput(BaseModel):
    """策略回测工具输入"""
    strategy_config: Dict[str, Any] = Field(description="策略配置")
    backtest_period: int = Field(365, description="回测期间（天）")
    benchmark_index: str = Field("000300.SH", description="基准指数")


class StrategyBacktestTool(BaseTool):
    """策略回测工具"""
    name = "strategy_backtest_tool"
    description = "使用历史数据执行策略回测和性能分析"
    args_schema = StrategyBacktestInput
    
    def _run(self, strategy_config: Dict[str, Any], 
             backtest_period: int = 365,
             benchmark_index: str = "000300.SH") -> Dict[str, Any]:
        """执行策略回测"""
        try:
            # 模拟回测结果（实际实现中需要获取真实历史数据）
            backtest_results = self._simulate_backtest(
                strategy_config, backtest_period
            )
            
            # 计算性能指标
            performance_metrics = self._calculate_performance_metrics(backtest_results)
            
            result = {
                "success": True,
                "backtest_results": backtest_results,
                "performance_metrics": performance_metrics,
                "backtest_period": backtest_period,
                "benchmark_index": benchmark_index
            }
            
            logger.info(f"策略回测完成，期间: {backtest_period}天")
            return result
            
        except Exception as e:
            logger.error(f"策略回测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "backtest_results": None,
                "performance_metrics": None
            }
    
    async def _arun(self, strategy_config: Dict[str, Any],
                   backtest_period: int = 365,
                   benchmark_index: str = "000300.SH") -> Dict[str, Any]:
        """异步执行策略回测"""
        return self._run(strategy_config, backtest_period, benchmark_index)
    
    def _simulate_backtest(self, strategy_config: Dict[str, Any], 
                          period_days: int) -> Dict[str, Any]:
        """模拟回测数据"""
        # 生成模拟的日期序列
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 模拟策略收益率
        np.random.seed(42)
        daily_returns = np.random.normal(0.0008, 0.015, len(dates))  # 日收益率
        
        # 计算累计收益
        cumulative_returns = (1 + pd.Series(daily_returns)).cumprod()
        portfolio_values = cumulative_returns * 100000  # 假设初始投资10万
        
        # 构建回测数据
        backtest_data = []
        for i, date in enumerate(dates):
            backtest_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "daily_return": round(daily_returns[i] * 100, 4),
                "cumulative_return": round((cumulative_returns.iloc[i] - 1) * 100, 2),
                "portfolio_value": round(portfolio_values.iloc[i], 2)
            })
        
        return {
            "daily_data": backtest_data,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "total_days": len(dates)
        }
    
    def _calculate_performance_metrics(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """计算绩效指标"""
        daily_data = backtest_results["daily_data"]
        if not daily_data:
            return {}
        
        # 提取收益率数据
        daily_returns = [d["daily_return"] / 100 for d in daily_data]
        cumulative_returns = [d["cumulative_return"] / 100 for d in daily_data]
        
        # 计算绩效指标
        total_return = cumulative_returns[-1] if cumulative_returns else 0
        annual_return = (1 + total_return) ** (365 / len(daily_returns)) - 1 if daily_returns else 0
        
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0
        
        # 计算最大回撤
        peak = 0
        max_drawdown = 0
        for cum_ret in cumulative_returns:
            if cum_ret > peak:
                peak = cum_ret
            drawdown = (peak - cum_ret) / (1 + peak)
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 计算夏普比率
        risk_free_rate = 0.03  # 假设无风险利率3%
        excess_return = annual_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        return {
            "total_return": round(total_return * 100, 2),
            "annual_return": round(annual_return * 100, 2),
            "volatility": round(volatility * 100, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "win_rate": round(sum(1 for r in daily_returns if r > 0) / len(daily_returns) * 100, 2) if daily_returns else 0
        }
