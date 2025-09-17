"""新闻关联性分析模块

分析新闻与ETF的关联性，补全Wind数据库中缺失的关联信息。
"""

import jieba
import re
from typing import Dict, List, Any, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class NewsETFMatcher:
    """新闻与ETF关联性分析器"""
    
    def __init__(self):
        self.industry_keywords = {
            "科技": ["科技", "芯片", "半导体", "人工智能", "AI", "5G", "互联网", "软件", "云计算"],
            "医药": ["医药", "生物", "医疗", "健康", "制药", "疫苗", "创新药", "医疗器械"],
            "金融": ["银行", "保险", "证券", "金融", "券商", "信贷", "理财", "支付"],
            "消费": ["消费", "食品", "饮料", "零售", "白酒", "餐饮", "旅游", "酒店"],
            "能源": ["能源", "石油", "煤炭", "电力", "新能源", "光伏", "风电", "核电"],
            "军工": ["军工", "国防", "航天", "航空", "武器", "导弹", "雷达"],
            "地产": ["地产", "房地产", "建筑", "基建", "水泥", "钢铁", "建材"],
            "汽车": ["汽车", "新能源车", "电动车", "智能驾驶", "车联网"]
        }
        
        self.positive_words = [
            "上涨", "利好", "增长", "看好", "买入", "推荐", "积极", "乐观", 
            "突破", "创新高", "强势", "领涨", "机遇", "受益", "提升"
        ]
        
        self.negative_words = [
            "下跌", "利空", "下降", "看空", "卖出", "风险", "担忧", "悲观",
            "跌破", "创新低", "疲软", "领跌", "压力", "冲击", "下滑"
        ]
        
        # 初始化jieba分词
        jieba.initialize()
    
    def analyze_news_relevance(self, news_content: str, etf_list: List[Dict]) -> Dict[str, Any]:
        """分析新闻与ETF的关联性"""
        
        try:
            # 1. 提取新闻关键词
            news_keywords = self._extract_keywords(news_content)
            
            # 2. 计算与每个ETF的相关性
            related_etfs = []
            relevance_scores = {}
            
            for etf in etf_list:
                score = self._calculate_relevance_score(news_keywords, etf)
                if score > 0.3:  # 相关性阈值
                    related_etfs.append(etf.get('etf_code', ''))
                    relevance_scores[etf.get('etf_code', '')] = score
            
            # 3. 分析情感倾向
            sentiment_score = self._analyze_sentiment(news_content)
            
            # 4. 提取投资含义
            investment_implications = self._extract_investment_implications(
                news_content, related_etfs
            )
            
            # 5. 判断市场影响
            market_impact = self._determine_market_impact(sentiment_score, related_etfs)
            
            return {
                "derived_related_etfs": related_etfs,
                "relevance_scores": relevance_scores,
                "derived_sentiment_score": sentiment_score,
                "derived_investment_implications": investment_implications,
                "derived_market_impact": market_impact,
                "analysis_confidence": self._calculate_confidence(news_keywords, related_etfs)
            }
            
        except Exception as e:
            logger.error(f"新闻关联性分析失败: {e}")
            return {
                "derived_related_etfs": [],
                "relevance_scores": {},
                "derived_sentiment_score": 0.0,
                "derived_investment_implications": "分析失败，请稍后重试",
                "derived_market_impact": "neutral",
                "analysis_confidence": 0.0
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词"""
        
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        stop_words = {"的", "了", "在", "是", "和", "与", "及", "等", "将", "会", "可", "能"}
        meaningful_words = [
            word.strip() for word in words 
            if len(word.strip()) > 1 and word.strip() not in stop_words
        ]
        
        # 统计词频，返回高频词
        word_freq = Counter(meaningful_words)
        return [word for word, freq in word_freq.most_common(50)]
    
    def _calculate_relevance_score(self, news_keywords: List[str], etf: Dict) -> float:
        """计算新闻与ETF的相关性得分"""
        
        etf_name = etf.get('etf_name', '')
        etf_code = etf.get('etf_code', '')
        
        # 构建ETF相关关键词
        etf_keywords = []
        
        # 添加ETF名称中的关键词
        etf_name_words = jieba.cut(etf_name)
        etf_keywords.extend([word for word in etf_name_words if len(word) > 1])
        
        # 添加行业关键词
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in etf_name for keyword in keywords):
                etf_keywords.extend(keywords)
                break
        
        # 计算关键词重叠度
        if not etf_keywords:
            return 0.0
        
        overlap = set(news_keywords) & set(etf_keywords)
        base_score = len(overlap) / len(set(etf_keywords))
        
        # 名称直接匹配加分
        if etf_name in ' '.join(news_keywords) or any(word in etf_name for word in news_keywords):
            base_score += 0.3
        
        # ETF代码匹配加分
        if etf_code in ' '.join(news_keywords):
            base_score += 0.5
        
        return min(base_score, 1.0)  # 限制在0-1范围内
    
    def _analyze_sentiment(self, text: str) -> float:
        """分析文本情感倾向"""
        
        pos_count = sum(1 for word in self.positive_words if word in text)
        neg_count = sum(1 for word in self.negative_words if word in text)
        
        total_count = pos_count + neg_count
        if total_count == 0:
            return 0.0
        
        # 计算情感得分 (-1 到 1)
        sentiment = (pos_count - neg_count) / total_count
        return round(sentiment, 2)
    
    def _extract_investment_implications(self, news_content: str, related_etfs: List[str]) -> str:
        """提取投资含义"""
        
        if not related_etfs:
            return "该新闻与ETF产品关联度较低，建议关注相关行业动态。"
        
        sentiment_score = self._analyze_sentiment(news_content)
        
        if sentiment_score > 0.3:
            implication = f"该新闻对相关ETF（{', '.join(related_etfs[:3])}等）可能产生积极影响，"
            implication += "建议关注相关产品的投资机会，但需注意市场风险。"
        elif sentiment_score < -0.3:
            implication = f"该新闻对相关ETF（{', '.join(related_etfs[:3])}等）可能产生负面影响，"
            implication += "建议谨慎评估投资风险，考虑适当调整仓位。"
        else:
            implication = f"该新闻对相关ETF（{', '.join(related_etfs[:3])}等）影响中性，"
            implication += "建议持续关注后续发展，保持理性投资态度。"
        
        return implication
    
    def _determine_market_impact(self, sentiment_score: float, related_etfs: List[str]) -> str:
        """判断市场影响"""
        
        if not related_etfs:
            return "neutral"
        
        if sentiment_score > 0.3:
            return "positive"
        elif sentiment_score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_confidence(self, news_keywords: List[str], related_etfs: List[str]) -> float:
        """计算分析置信度"""
        
        # 基于关键词数量和相关ETF数量计算置信度
        keyword_score = min(len(news_keywords) / 20, 1.0)  # 关键词越多置信度越高
        etf_score = min(len(related_etfs) / 5, 1.0)  # 相关ETF越多置信度越高
        
        confidence = (keyword_score + etf_score) / 2
        return round(confidence, 2)


def analyze_news_relevance(news_content: str, etf_list: List[Dict]) -> Dict[str, Any]:
    """便捷函数：分析新闻关联性"""
    matcher = NewsETFMatcher()
    return matcher.analyze_news_relevance(news_content, etf_list)


def batch_analyze_news(news_list: List[Dict], etf_list: List[Dict]) -> List[Dict]:
    """批量分析新闻关联性"""
    matcher = NewsETFMatcher()
    
    for news in news_list:
        if news.get("content"):
            analysis_result = matcher.analyze_news_relevance(
                news["content"], 
                etf_list
            )
            news.update(analysis_result)
    
    return news_list


if __name__ == "__main__":
    # 测试代码
    test_news = "科技股今日大涨，人工智能概念股表现强势，芯片板块领涨市场。"
    test_etfs = [
        {"etf_name": "科技ETF", "etf_code": "515000.SH"},
        {"etf_name": "沪深300ETF", "etf_code": "510300.SH"}
    ]
    
    result = analyze_news_relevance(test_news, test_etfs)
    print(f"关联ETF: {result['derived_related_etfs']}")
    print(f"情感得分: {result['derived_sentiment_score']}")
    print(f"投资含义: {result['derived_investment_implications']}")
