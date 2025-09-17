"""估值指标计算模块

基于价格历史数据估算PE/PB等估值指标，补全Wind数据库中缺失的估值信息。
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ValuationCalculator:
    """估值指标计算器"""
    
    def __init__(self):
        # 行业基准PE/PB比率
        self.industry_base_ratios = {
            "科技": {"base_pe": 25, "base_pb": 3.5},
            "医药": {"base_pe": 30, "base_pb": 4.0},
            "金融": {"base_pe": 8, "base_pb": 0.8},
            "消费": {"base_pe": 20, "base_pb": 2.5},
            "能源": {"base_pe": 12, "base_pb": 1.2},
            "军工": {"base_pe": 35, "base_pb": 3.0},
            "地产": {"base_pe": 10, "base_pb": 1.0},
            "材料": {"base_pe": 15, "base_pb": 1.5},
            "综合": {"base_pe": 18, "base_pb": 2.0}
        }
    
    def estimate_valuation_metrics(self, etf_code: str, price_history: List[Dict], 
                                 etf_classification: Optional[Dict] = None) -> Dict[str, Any]:
        """估算估值指标"""
        
        try:
            if not price_history or len(price_history) < 20:
                return self._get_default_valuation()
            
            # 1. 处理价格数据
            prices_df = pd.DataFrame(price_history)
            prices_df['trade_date'] = pd.to_datetime(prices_df['trade_date'])
            prices_df = prices_df.sort_values('trade_date')
            
            # 2. 计算技术指标
            recent_prices = prices_df['close_price'].tail(60).tolist()
            current_price = recent_prices[-1]
            
            # 3. 计算价格位置
            price_position = self._calculate_price_position(recent_prices)
            
            # 4. 计算波动率
            volatility = self._calculate_volatility(recent_prices)
            
            # 5. 估算PE/PB比率
            industry = self._get_industry_from_classification(etf_classification)
            estimated_pe = self._estimate_pe_ratio(price_position, volatility, industry)
            estimated_pb = self._estimate_pb_ratio(estimated_pe, industry)
            
            # 6. 计算溢价折价率
            nav_estimate = self._estimate_nav(recent_prices, current_price)
            premium_discount = ((current_price - nav_estimate) / nav_estimate) * 100
            
            return {
                "derived_pe_ratio": round(estimated_pe, 2),
                "derived_pb_ratio": round(estimated_pb, 2),
                "derived_premium_discount_rate": round(premium_discount, 2),
                "price_position_percentile": round(price_position * 100, 1),
                "volatility": round(volatility, 4),
                "confidence_level": "estimated",
                "calculation_date": datetime.now().strftime("%Y-%m-%d"),
                "data_points": len(price_history)
            }
            
        except Exception as e:
            logger.error(f"估值指标计算失败 {etf_code}: {e}")
            return self._get_default_valuation()
    
    def _calculate_price_position(self, prices: List[float]) -> float:
        """计算价格在历史区间中的位置（0-1）"""
        
        if len(prices) < 2:
            return 0.5
        
        current_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        
        if max_price == min_price:
            return 0.5
        
        position = (current_price - min_price) / (max_price - min_price)
        return max(0, min(1, position))
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算年化波动率"""
        
        if len(prices) < 2:
            return 0.2  # 默认波动率
        
        # 计算日收益率
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        if not returns:
            return 0.2
        
        # 计算年化波动率
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * np.sqrt(252)  # 252个交易日
        
        return max(0.05, min(1.0, annual_volatility))  # 限制在合理范围内
    
    def _get_industry_from_classification(self, classification: Optional[Dict]) -> str:
        """从分类信息中获取行业"""
        
        if not classification:
            return "综合"
        
        industry = classification.get("derived_industry") or classification.get("derived_sub_category")
        return industry if industry in self.industry_base_ratios else "综合"
    
    def _estimate_pe_ratio(self, price_position: float, volatility: float, industry: str) -> float:
        """估算PE比率"""
        
        base_ratios = self.industry_base_ratios.get(industry, self.industry_base_ratios["综合"])
        base_pe = base_ratios["base_pe"]
        
        # 基于价格位置调整
        position_adjustment = (price_position - 0.5) * base_pe * 0.3
        
        # 基于波动率调整
        volatility_adjustment = (volatility - 0.3) * base_pe * 0.2
        
        estimated_pe = base_pe + position_adjustment + volatility_adjustment
        
        # 限制在合理范围内
        min_pe = base_pe * 0.5
        max_pe = base_pe * 2.0
        
        return max(min_pe, min(max_pe, estimated_pe))
    
    def _estimate_pb_ratio(self, estimated_pe: float, industry: str) -> float:
        """估算PB比率"""
        
        base_ratios = self.industry_base_ratios.get(industry, self.industry_base_ratios["综合"])
        base_pb = base_ratios["base_pb"]
        
        # PB通常与PE相关，但比例因行业而异
        if industry == "金融":
            pb_pe_ratio = 0.1  # 金融行业PB/PE比率较低
        elif industry in ["科技", "医药"]:
            pb_pe_ratio = 0.15  # 成长性行业比率较高
        else:
            pb_pe_ratio = 0.12  # 一般行业
        
        estimated_pb = estimated_pe * pb_pe_ratio
        
        # 确保不低于基准值的一半
        return max(base_pb * 0.5, estimated_pb)
    
    def _estimate_nav(self, prices: List[float], current_price: float) -> float:
        """估算净值"""
        
        # 简化估算：假设净值接近近期平均价格
        if len(prices) >= 10:
            recent_avg = np.mean(prices[-10:])
            return recent_avg * 0.98  # 略低于市价
        else:
            return current_price * 0.98
    
    def _get_default_valuation(self) -> Dict[str, Any]:
        """获取默认估值指标"""
        
        return {
            "derived_pe_ratio": 18.0,
            "derived_pb_ratio": 2.0,
            "derived_premium_discount_rate": 0.0,
            "price_position_percentile": 50.0,
            "volatility": 0.25,
            "confidence_level": "default",
            "calculation_date": datetime.now().strftime("%Y-%m-%d"),
            "data_points": 0
        }
    
    def batch_calculate_valuations(self, etf_list: List[Dict], 
                                 price_data_dict: Dict[str, List[Dict]]) -> List[Dict]:
        """批量计算估值指标"""
        
        for etf in etf_list:
            etf_code = etf.get("etf_code")
            if etf_code and etf_code in price_data_dict:
                price_history = price_data_dict[etf_code]
                valuation = self.estimate_valuation_metrics(
                    etf_code, 
                    price_history, 
                    etf.get("classification")
                )
                etf.update(valuation)
        
        return etf_list
    
    def analyze_market_valuation_level(self, etf_valuations: List[Dict]) -> Dict[str, Any]:
        """分析市场整体估值水平"""
        
        pe_ratios = [v.get("derived_pe_ratio", 0) for v in etf_valuations if v.get("derived_pe_ratio")]
        pb_ratios = [v.get("derived_pb_ratio", 0) for v in etf_valuations if v.get("derived_pb_ratio")]
        
        if not pe_ratios or not pb_ratios:
            return {"market_valuation_level": "unknown", "analysis": "数据不足，无法分析"}
        
        avg_pe = np.mean(pe_ratios)
        avg_pb = np.mean(pb_ratios)
        
        # 判断估值水平
        if avg_pe > 25 or avg_pb > 3:
            level = "high"
            analysis = "市场整体估值偏高，建议谨慎投资，关注价值型ETF。"
        elif avg_pe < 15 or avg_pb < 1.5:
            level = "low" 
            analysis = "市场整体估值偏低，具有投资价值，可考虑增加配置。"
        else:
            level = "moderate"
            analysis = "市场整体估值合理，建议均衡配置，关注结构性机会。"
        
        return {
            "market_valuation_level": level,
            "average_pe": round(avg_pe, 2),
            "average_pb": round(avg_pb, 2),
            "analysis": analysis,
            "sample_size": len(pe_ratios)
        }


def estimate_etf_valuation(etf_code: str, price_history: List[Dict], 
                          classification: Optional[Dict] = None) -> Dict[str, Any]:
    """便捷函数：估算单个ETF的估值指标"""
    calculator = ValuationCalculator()
    return calculator.estimate_valuation_metrics(etf_code, price_history, classification)


if __name__ == "__main__":
    # 测试代码
    test_prices = [
        {"trade_date": "2024-01-01", "close_price": 1.0},
        {"trade_date": "2024-01-02", "close_price": 1.02},
        {"trade_date": "2024-01-03", "close_price": 0.98},
        {"trade_date": "2024-01-04", "close_price": 1.05}
    ]
    
    test_classification = {"derived_industry": "科技"}
    
    result = estimate_etf_valuation("515000.SH", test_prices, test_classification)
    print(f"估算PE: {result['derived_pe_ratio']}")
    print(f"估算PB: {result['derived_pb_ratio']}")
