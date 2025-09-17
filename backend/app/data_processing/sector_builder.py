"""虚拟板块数据构建模块

基于ETF分类构建虚拟行业板块指数，补全缺失的板块数据。
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VirtualSectorBuilder:
    """虚拟板块数据构建器"""
    
    def __init__(self):
        self.sector_mapping = {
            "科技": ["科技", "芯片", "半导体", "人工智能", "AI", "5G", "互联网", "计算机"],
            "医药": ["医药", "生物", "医疗", "健康", "制药", "医疗器械"],
            "金融": ["银行", "保险", "证券", "金融", "券商"],
            "消费": ["消费", "食品", "饮料", "零售", "白酒", "家电"],
            "能源": ["能源", "石油", "煤炭", "电力", "新能源", "光伏"],
            "军工": ["军工", "国防", "航天", "航空"],
            "地产": ["地产", "房地产", "建筑", "基建"],
            "材料": ["材料", "化工", "钢铁", "有色", "采掘"]
        }
    
    def build_sector_data(self, etf_data: List[Dict], target_date: str) -> List[Dict]:
        """构建虚拟板块数据"""
        
        try:
            # 1. 按行业分组ETF
            sector_groups = self._group_etfs_by_sector(etf_data)
            
            sector_data = []
            for sector_name, etfs in sector_groups.items():
                if len(etfs) < 2:  # 至少需要2个ETF才能构建板块
                    continue
                
                # 2. 计算板块指数
                sector_index = self._calculate_sector_index(etfs, target_date)
                
                if sector_index:
                    sector_data.append({
                        "virtual_sector_code": f"VS_{sector_name}",
                        "sector_name": f"{sector_name}板块",
                        "trade_date": target_date,
                        "index_value": sector_index["value"],
                        "change_rate": sector_index["change_rate"],
                        "constituent_etfs": [etf["etf_code"] for etf in etfs],
                        "etf_count": len(etfs),
                        "total_market_cap": sector_index["total_market_cap"],
                        "weights": sector_index["weights"],
                        "performance_summary": self._generate_sector_summary(sector_name, sector_index)
                    })
            
            logger.info(f"成功构建 {len(sector_data)} 个虚拟板块数据")
            return sector_data
            
        except Exception as e:
            logger.error(f"虚拟板块数据构建失败: {e}")
            return []
    
    def _group_etfs_by_sector(self, etf_data: List[Dict]) -> Dict[str, List[Dict]]:
        """按行业分组ETF"""
        
        sectors = {}
        
        for etf in etf_data:
            etf_name = etf.get("etf_name", "")
            
            # 基于名称推导行业
            sector = self._derive_sector_from_name(etf_name)
            
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(etf)
        
        return sectors
    
    def _derive_sector_from_name(self, etf_name: str) -> str:
        """从ETF名称推导行业"""
        
        for sector, keywords in self.sector_mapping.items():
            if any(keyword in etf_name for keyword in keywords):
                return sector
        
        return "综合"  # 默认分类
    
    def _calculate_sector_index(self, etfs: List[Dict], target_date: str) -> Optional[Dict]:
        """计算板块指数"""
        
        try:
            # 获取各ETF的市值和收益率数据
            etf_data = []
            total_market_cap = 0
            
            for etf in etfs:
                market_cap = etf.get("fund_scale", 0)  # 基金规模作为权重
                if market_cap <= 0:
                    market_cap = 1  # 默认权重
                
                # 获取收益率（这里简化处理，实际应该从价格数据计算）
                return_rate = self._get_etf_return_rate(etf, target_date)
                
                etf_data.append({
                    "etf_code": etf["etf_code"],
                    "market_cap": market_cap,
                    "return_rate": return_rate
                })
                total_market_cap += market_cap
            
            if total_market_cap == 0:
                return None
            
            # 计算市值加权收益率
            weighted_return = 0
            weights = {}
            
            for data in etf_data:
                weight = data["market_cap"] / total_market_cap
                weighted_return += weight * data["return_rate"]
                weights[data["etf_code"]] = round(weight, 4)
            
            # 计算板块指数值（基准值1000）
            base_value = 1000
            current_value = base_value * (1 + weighted_return / 100)
            
            return {
                "value": round(current_value, 2),
                "change_rate": round(weighted_return, 2),
                "total_market_cap": total_market_cap,
                "weights": weights
            }
            
        except Exception as e:
            logger.error(f"板块指数计算失败: {e}")
            return None
    
    def _get_etf_return_rate(self, etf: Dict, target_date: str) -> float:
        """获取ETF收益率（简化实现）"""
        
        # 这里应该从数据库获取实际的价格数据计算收益率
        # 当前使用模拟数据
        
        etf_name = etf.get("etf_name", "")
        
        # 基于行业特征模拟收益率
        if any(keyword in etf_name for keyword in ["科技", "芯片", "AI"]):
            return np.random.normal(0.5, 2.0)  # 科技板块波动较大
        elif any(keyword in etf_name for keyword in ["消费", "食品", "白酒"]):
            return np.random.normal(0.2, 1.5)  # 消费板块相对稳定
        elif any(keyword in etf_name for keyword in ["银行", "金融", "保险"]):
            return np.random.normal(0.1, 1.0)  # 金融板块波动较小
        else:
            return np.random.normal(0.0, 1.5)  # 综合板块
    
    def _generate_sector_summary(self, sector_name: str, sector_index: Dict) -> str:
        """生成板块表现总结"""
        
        change_rate = sector_index["change_rate"]
        
        if change_rate > 2:
            trend = "强势上涨"
            suggestion = "表现优异，可考虑适当配置"
        elif change_rate > 0:
            trend = "温和上涨"
            suggestion = "表现平稳，可持续关注"
        elif change_rate > -2:
            trend = "小幅波动"
            suggestion = "表现中性，建议观望"
        else:
            trend = "明显下跌"
            suggestion = "表现疲弱，建议谨慎配置"
        
        return f"{sector_name}板块今日{trend}，涨跌幅{change_rate:.2f}%。{suggestion}。"
    
    def get_sector_ranking(self, sector_data: List[Dict]) -> List[Dict]:
        """获取板块表现排名"""
        
        # 按涨跌幅排序
        sorted_sectors = sorted(
            sector_data, 
            key=lambda x: x.get("change_rate", 0), 
            reverse=True
        )
        
        # 添加排名信息
        for i, sector in enumerate(sorted_sectors):
            sector["rank"] = i + 1
            sector["performance_level"] = self._get_performance_level(sector["change_rate"])
        
        return sorted_sectors
    
    def _get_performance_level(self, change_rate: float) -> str:
        """获取表现等级"""
        
        if change_rate > 3:
            return "excellent"
        elif change_rate > 1:
            return "good"
        elif change_rate > -1:
            return "neutral"
        elif change_rate > -3:
            return "poor"
        else:
            return "very_poor"
    
    def build_sector_rotation_analysis(self, sector_data: List[Dict]) -> Dict[str, Any]:
        """构建板块轮动分析"""
        
        ranked_sectors = self.get_sector_ranking(sector_data)
        
        # 强势板块（前30%）
        strong_sectors = ranked_sectors[:max(1, len(ranked_sectors) // 3)]
        
        # 弱势板块（后30%）
        weak_sectors = ranked_sectors[-max(1, len(ranked_sectors) // 3):]
        
        return {
            "rotation_analysis": {
                "strong_sectors": [s["sector_name"] for s in strong_sectors],
                "weak_sectors": [s["sector_name"] for s in weak_sectors],
                "rotation_suggestion": self._generate_rotation_suggestion(strong_sectors, weak_sectors)
            },
            "sector_ranking": ranked_sectors
        }
    
    def _generate_rotation_suggestion(self, strong_sectors: List[Dict], weak_sectors: List[Dict]) -> str:
        """生成板块轮动建议"""
        
        strong_names = [s["sector_name"] for s in strong_sectors[:3]]
        weak_names = [s["sector_name"] for s in weak_sectors[:3]]
        
        suggestion = f"当前市场中，{', '.join(strong_names)}等板块表现强势，"
        suggestion += f"而{', '.join(weak_names)}等板块相对疲弱。"
        suggestion += "建议在风险可控的前提下，适当增加强势板块配置，减少弱势板块权重。"
        
        return suggestion


if __name__ == "__main__":
    # 测试代码
    test_etfs = [
        {"etf_name": "科技ETF", "etf_code": "515000.SH", "fund_scale": 1000},
        {"etf_name": "芯片ETF", "etf_code": "512760.SH", "fund_scale": 800},
        {"etf_name": "医药ETF", "etf_code": "512010.SH", "fund_scale": 600}
    ]
    
    builder = VirtualSectorBuilder()
    sector_data = builder.build_sector_data(test_etfs, "2024-01-15")
    
    for sector in sector_data:
        print(f"{sector['sector_name']}: {sector['change_rate']:.2f}%")
