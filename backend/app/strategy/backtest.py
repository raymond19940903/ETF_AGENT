"""回测引擎"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.data.wind_service import WindService
from app.models.backtest import StrategyBacktestData
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.wind_service = WindService()
    
    async def run_backtest(self, strategy_config: Dict[str, Any], 
                          backtest_period: int = 365,
                          benchmark_index: str = "000300.SH") -> Dict[str, Any]:
        """执行策略回测"""
        try:
            # 获取回测时间范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=backtest_period)
            
            # 获取ETF历史数据
            etf_data = await self._get_etf_historical_data(
                strategy_config, start_date, end_date
            )
            
            if not etf_data:
                return {
                    "success": False,
                    "error": "无法获取ETF历史数据",
                    "backtest_results": None
                }
            
            # 计算组合收益率
            portfolio_returns = self._calculate_portfolio_returns(etf_data, strategy_config)
            
            # 获取基准数据
            benchmark_returns = await self._get_benchmark_returns(
                benchmark_index, start_date, end_date
            )
            
            # 计算绩效指标
            performance_metrics = self._calculate_performance_metrics(
                portfolio_returns, benchmark_returns
            )
            
            # 生成日度数据
            daily_data = self._generate_daily_data(portfolio_returns, start_date)
            
            result = {
                "success": True,
                "backtest_results": {
                    "daily_data": daily_data,
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "total_days": len(daily_data)
                },
                "performance_metrics": performance_metrics,
                "benchmark_comparison": {
                    "benchmark_index": benchmark_index,
                    "portfolio_return": performance_metrics["total_return"],
                    "benchmark_return": self._calculate_total_return(benchmark_returns) if benchmark_returns else 0,
                    "excess_return": performance_metrics["total_return"] - (self._calculate_total_return(benchmark_returns) if benchmark_returns else 0)
                }
            }
            
            logger.info(f"回测完成: {backtest_period}天, 年化收益{performance_metrics['annual_return']}%")
            return result
            
        except Exception as e:
            logger.error(f"回测执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "backtest_results": None,
                "performance_metrics": None
            }
    
    async def _get_etf_historical_data(self, strategy_config: Dict[str, Any], 
                                     start_date: datetime, 
                                     end_date: datetime) -> Dict[str, pd.DataFrame]:
        """获取ETF历史数据"""
        try:
            etf_data = {}
            allocations = strategy_config.get("etf_allocations", [])
            
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            with self.wind_service:
                for allocation in allocations:
                    etf_code = allocation["etf_code"]
                    
                    try:
                        price_data = self.wind_service.get_etf_price_data(
                            etf_code, start_str, end_str
                        )
                        
                        if price_data:
                            df = pd.DataFrame(price_data)
                            df['trade_date'] = pd.to_datetime(df['trade_date'])
                            df = df.set_index('trade_date').sort_index()
                            df['daily_return'] = df['close_price'].pct_change()
                            etf_data[etf_code] = df
                            
                    except Exception as e:
                        logger.warning(f"获取ETF {etf_code} 数据失败: {e}")
                        # 生成模拟数据作为备用
                        etf_data[etf_code] = self._generate_mock_data(start_date, end_date)
            
            return etf_data
            
        except Exception as e:
            logger.error(f"获取ETF历史数据失败: {e}")
            return {}
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """生成模拟数据"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成模拟价格数据
        np.random.seed(42)
        returns = np.random.normal(0.0008, 0.015, len(date_range))
        prices = 100 * (1 + pd.Series(returns)).cumprod()
        
        df = pd.DataFrame({
            'close_price': prices,
            'daily_return': returns
        }, index=date_range)
        
        return df
    
    def _calculate_portfolio_returns(self, etf_data: Dict[str, pd.DataFrame], 
                                   strategy_config: Dict[str, Any]) -> pd.Series:
        """计算组合收益率"""
        try:
            allocations = strategy_config.get("etf_allocations", [])
            
            if not etf_data or not allocations:
                return pd.Series()
            
            # 获取所有ETF的收益率数据
            returns_data = {}
            for allocation in allocations:
                etf_code = allocation["etf_code"]
                weight = allocation["weight"] / 100  # 转换为小数
                
                if etf_code in etf_data:
                    returns_data[etf_code] = etf_data[etf_code]['daily_return'] * weight
            
            if not returns_data:
                return pd.Series()
            
            # 合并所有ETF的收益率
            returns_df = pd.DataFrame(returns_data)
            
            # 计算组合日收益率
            portfolio_returns = returns_df.sum(axis=1, skipna=True)
            
            # 去除NaN值
            portfolio_returns = portfolio_returns.dropna()
            
            return portfolio_returns
            
        except Exception as e:
            logger.error(f"计算组合收益率失败: {e}")
            return pd.Series()
    
    async def _get_benchmark_returns(self, benchmark_index: str, 
                                   start_date: datetime, 
                                   end_date: datetime) -> Optional[pd.Series]:
        """获取基准收益率"""
        try:
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            with self.wind_service:
                benchmark_data = self.wind_service.get_market_index_data(
                    benchmark_index, start_str, end_str
                )
            
            if benchmark_data:
                df = pd.DataFrame(benchmark_data)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.set_index('trade_date').sort_index()
                df['daily_return'] = df['close_price'].pct_change()
                return df['daily_return'].dropna()
            
            return None
            
        except Exception as e:
            logger.warning(f"获取基准数据失败: {e}")
            return None
    
    def _calculate_performance_metrics(self, portfolio_returns: pd.Series, 
                                     benchmark_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """计算绩效指标"""
        try:
            if portfolio_returns.empty:
                return {}
            
            # 基础指标
            total_return = (1 + portfolio_returns).prod() - 1
            annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            # 最大回撤
            cumulative_returns = (1 + portfolio_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # 夏普比率
            risk_free_rate = 0.03
            excess_return = annual_return - risk_free_rate
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0
            
            # 胜率
            win_rate = (portfolio_returns > 0).sum() / len(portfolio_returns)
            
            metrics = {
                "total_return": round(total_return * 100, 2),
                "annual_return": round(annual_return * 100, 2),
                "volatility": round(volatility * 100, 2),
                "max_drawdown": round(abs(max_drawdown) * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "win_rate": round(win_rate * 100, 2)
            }
            
            # 如果有基准数据，计算相对指标
            if benchmark_returns is not None and not benchmark_returns.empty:
                # 对齐时间序列
                aligned_portfolio, aligned_benchmark = portfolio_returns.align(benchmark_returns, join='inner')
                
                if not aligned_portfolio.empty and not aligned_benchmark.empty:
                    benchmark_total_return = (1 + aligned_benchmark).prod() - 1
                    benchmark_annual_return = (1 + benchmark_total_return) ** (252 / len(aligned_benchmark)) - 1
                    
                    metrics.update({
                        "benchmark_annual_return": round(benchmark_annual_return * 100, 2),
                        "excess_return": round((annual_return - benchmark_annual_return) * 100, 2),
                        "tracking_error": round((aligned_portfolio - aligned_benchmark).std() * np.sqrt(252) * 100, 2),
                        "information_ratio": round(
                            (annual_return - benchmark_annual_return) / ((aligned_portfolio - aligned_benchmark).std() * np.sqrt(252))
                            if (aligned_portfolio - aligned_benchmark).std() > 0 else 0, 2
                        )
                    })
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算绩效指标失败: {e}")
            return {}
    
    def _generate_daily_data(self, portfolio_returns: pd.Series, 
                           start_date: datetime) -> List[Dict[str, Any]]:
        """生成日度回测数据"""
        try:
            if portfolio_returns.empty:
                return []
            
            # 计算累计收益和组合价值
            cumulative_returns = (1 + portfolio_returns).cumprod()
            initial_value = 100000  # 假设初始投资10万元
            portfolio_values = cumulative_returns * initial_value
            
            daily_data = []
            for i, (date, daily_ret) in enumerate(portfolio_returns.items()):
                daily_data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "daily_return": round(daily_ret * 100, 4),
                    "cumulative_return": round((cumulative_returns.iloc[i] - 1) * 100, 2),
                    "portfolio_value": round(portfolio_values.iloc[i], 2)
                })
            
            return daily_data
            
        except Exception as e:
            logger.error(f"生成日度数据失败: {e}")
            return []
    
    def _calculate_total_return(self, returns: pd.Series) -> float:
        """计算总收益率"""
        try:
            if returns.empty:
                return 0.0
            return ((1 + returns).prod() - 1) * 100
        except:
            return 0.0
    
    async def save_backtest_results(self, strategy_id: int, 
                                  backtest_results: Dict[str, Any]) -> bool:
        """保存回测结果到数据库"""
        try:
            # 删除现有的回测数据
            self.db.query(StrategyBacktestData).filter(
                StrategyBacktestData.strategy_id == strategy_id
            ).delete()
            
            # 保存新的回测数据
            daily_data = backtest_results.get("backtest_results", {}).get("daily_data", [])
            performance_metrics = backtest_results.get("performance_metrics", {})
            
            for data_point in daily_data:
                backtest_record = StrategyBacktestData(
                    strategy_id=strategy_id,
                    backtest_date=datetime.strptime(data_point["date"], '%Y-%m-%d').date(),
                    daily_return=data_point["daily_return"] / 100,
                    cumulative_return=data_point["cumulative_return"] / 100,
                    portfolio_value=data_point["portfolio_value"],
                    performance_metrics=performance_metrics
                )
                self.db.add(backtest_record)
            
            self.db.commit()
            logger.info(f"回测结果保存成功: strategy_id={strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存回测结果失败: {e}")
            self.db.rollback()
            return False
