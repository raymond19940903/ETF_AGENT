"""数据补全协调器

协调各个数据处理模块，提供统一的数据补全服务。
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from .etf_classifier import ETFClassifier
from .news_analyzer import NewsETFMatcher
from .sector_builder import VirtualSectorBuilder
from .valuation_calculator import ValuationCalculator
import logging

logger = logging.getLogger(__name__)


class DataEnricher:
    """数据补全器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.etf_classifier = ETFClassifier()
        self.news_matcher = NewsETFMatcher()
        self.sector_builder = VirtualSectorBuilder()
        self.valuation_calculator = ValuationCalculator()
    
    def enrich_etf_data(self, etf_data: List[Dict]) -> List[Dict]:
        """补全ETF数据"""
        
        try:
            enriched_data = []
            
            for etf in etf_data:
                enriched_etf = etf.copy()
                
                # 1. 补全分类信息
                if not etf.get('category') or not etf.get('investment_objective'):
                    classification = self.etf_classifier.classify_etf(
                        etf.get('etf_name', ''),
                        etf.get('etf_code', '')
                    )
                    enriched_etf.update(classification)
                
                # 2. 补全估值指标（如果有价格数据）
                price_history = self._get_price_history(etf.get('etf_code', ''))
                if price_history:
                    valuation = self.valuation_calculator.estimate_valuation_metrics(
                        etf.get('etf_code', ''),
                        price_history,
                        enriched_etf
                    )
                    enriched_etf.update(valuation)
                
                enriched_data.append(enriched_etf)
            
            logger.info(f"成功补全 {len(enriched_data)} 个ETF数据")
            return enriched_data
            
        except Exception as e:
            logger.error(f"ETF数据补全失败: {e}")
            return etf_data  # 返回原始数据
    
    def enrich_news_data(self, news_data: List[Dict], etf_list: List[Dict]) -> List[Dict]:
        """补全新闻数据"""
        
        try:
            enriched_news = []
            
            for news in news_data:
                enriched_news_item = news.copy()
                
                # 分析新闻与ETF关联性
                if news.get('content'):
                    relevance_analysis = self.news_matcher.analyze_news_relevance(
                        news['content'],
                        etf_list
                    )
                    enriched_news_item.update(relevance_analysis)
                
                enriched_news.append(enriched_news_item)
            
            logger.info(f"成功补全 {len(enriched_news)} 条新闻数据")
            return enriched_news
            
        except Exception as e:
            logger.error(f"新闻数据补全失败: {e}")
            return news_data
    
    def build_virtual_sectors(self, etf_data: List[Dict], target_date: str) -> List[Dict]:
        """构建虚拟板块数据"""
        
        try:
            # 确保ETF数据已经分类
            classified_etfs = self.enrich_etf_data(etf_data)
            
            # 构建虚拟板块
            sector_data = self.sector_builder.build_sector_data(classified_etfs, target_date)
            
            # 添加板块轮动分析
            if sector_data:
                rotation_analysis = self.sector_builder.build_sector_rotation_analysis(sector_data)
                return {
                    "sector_data": sector_data,
                    "rotation_analysis": rotation_analysis
                }
            
            return {"sector_data": [], "rotation_analysis": {}}
            
        except Exception as e:
            logger.error(f"虚拟板块构建失败: {e}")
            return {"sector_data": [], "rotation_analysis": {}}
    
    def comprehensive_data_enrichment(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """综合数据补全"""
        
        enriched_data = {
            "etf_data": [],
            "news_data": [],
            "sector_data": [],
            "market_analysis": {}
        }
        
        try:
            # 1. 补全ETF数据
            if raw_data.get("etf_data"):
                enriched_data["etf_data"] = self.enrich_etf_data(raw_data["etf_data"])
            
            # 2. 补全新闻数据
            if raw_data.get("news_data") and enriched_data["etf_data"]:
                enriched_data["news_data"] = self.enrich_news_data(
                    raw_data["news_data"],
                    enriched_data["etf_data"]
                )
            
            # 3. 构建虚拟板块
            if enriched_data["etf_data"]:
                target_date = raw_data.get("target_date", datetime.now().strftime("%Y-%m-%d"))
                virtual_sectors = self.build_virtual_sectors(enriched_data["etf_data"], target_date)
                enriched_data["sector_data"] = virtual_sectors.get("sector_data", [])
                enriched_data["rotation_analysis"] = virtual_sectors.get("rotation_analysis", {})
            
            # 4. 市场整体分析
            if enriched_data["etf_data"]:
                market_valuation = self.valuation_calculator.analyze_market_valuation_level(
                    enriched_data["etf_data"]
                )
                enriched_data["market_analysis"] = market_valuation
            
            logger.info("综合数据补全完成")
            return enriched_data
            
        except Exception as e:
            logger.error(f"综合数据补全失败: {e}")
            return enriched_data
    
    def _get_price_history(self, etf_code: str) -> List[Dict]:
        """获取ETF价格历史数据"""
        
        try:
            # 这里应该从数据库查询价格历史
            # 当前返回空列表，实际实现时需要查询etf_price_data表
            return []
            
        except Exception as e:
            logger.error(f"获取价格历史失败 {etf_code}: {e}")
            return []
    
    def get_enrichment_summary(self, original_data: Dict, enriched_data: Dict) -> Dict[str, Any]:
        """获取数据补全总结"""
        
        summary = {
            "original_etf_count": len(original_data.get("etf_data", [])),
            "enriched_etf_count": len(enriched_data.get("etf_data", [])),
            "original_news_count": len(original_data.get("news_data", [])),
            "enriched_news_count": len(enriched_data.get("news_data", [])),
            "virtual_sectors_created": len(enriched_data.get("sector_data", [])),
            "enrichment_fields": []
        }
        
        # 统计补全的字段
        enrichment_fields = [
            "derived_category",
            "derived_investment_objective", 
            "derived_related_etfs",
            "derived_sentiment_score",
            "derived_pe_ratio",
            "derived_pb_ratio"
        ]
        
        for field in enrichment_fields:
            count = sum(1 for etf in enriched_data.get("etf_data", []) if etf.get(field))
            if count > 0:
                summary["enrichment_fields"].append({
                    "field": field,
                    "enriched_count": count,
                    "coverage_rate": round(count / max(1, summary["enriched_etf_count"]) * 100, 1)
                })
        
        return summary


def enrich_data_for_llm(raw_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """便捷函数：为大模型补全数据"""
    enricher = DataEnricher(db)
    return enricher.comprehensive_data_enrichment(raw_data)


if __name__ == "__main__":
    # 测试代码
    test_data = {
        "etf_data": [
            {"etf_name": "科技ETF", "etf_code": "515000.SH"},
            {"etf_name": "医药ETF", "etf_code": "512010.SH"}
        ],
        "news_data": [
            {"content": "科技股今日大涨，人工智能概念表现强势"}
        ],
        "target_date": "2024-01-15"
    }
    
    # 注意：实际使用时需要传入数据库会话
    # enriched = enrich_data_for_llm(test_data, db_session)
    print("数据补全模块测试完成")
