"""市场资讯服务"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class NewsService:
    """市场资讯服务类"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=settings.NEWS_API_TIMEOUT)
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def get_financial_news(self, category: str = "finance", 
                               limit: int = 20) -> List[Dict[str, Any]]:
        """获取财经新闻"""
        try:
            # 使用新浪财经API示例
            sina_config = settings.FINANCIAL_NEWS_SOURCES["sina"]
            url = f"{sina_config['base_url']}/news/list"
            
            params = {
                'category': category,
                'limit': limit,
                'format': 'json'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            async with self.session.get(
                url, 
                params=params, 
                headers=sina_config['headers']
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_sina_news(data)
                else:
                    logger.warning(f"新浪财经API返回状态码: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"获取新浪财经新闻失败: {e}")
            return []
    
    async def get_etf_related_news(self, keywords: List[str], 
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """获取ETF相关新闻"""
        try:
            news_list = []
            
            for keyword in keywords:
                # 搜索包含关键词的新闻
                keyword_news = await self.search_news(keyword, limit//len(keywords) + 1)
                news_list.extend(keyword_news)
            
            # 去重并按时间排序
            unique_news = self._deduplicate_news(news_list)
            sorted_news = sorted(unique_news, 
                               key=lambda x: x.get('publish_time', ''), 
                               reverse=True)
            
            return sorted_news[:limit]
            
        except Exception as e:
            logger.error(f"获取ETF相关新闻失败: {e}")
            return []
    
    async def search_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索新闻"""
        try:
            # 使用东方财富API示例
            eastmoney_config = settings.FINANCIAL_NEWS_SOURCES["eastmoney"]
            url = f"{eastmoney_config['base_url']}/search/news"
            
            params = {
                'keyword': keyword,
                'limit': limit,
                'type': 'finance'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            async with self.session.get(
                url, 
                params=params, 
                headers=eastmoney_config['headers']
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_eastmoney_news(data)
                else:
                    logger.warning(f"东方财富API返回状态码: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"搜索新闻失败 {keyword}: {e}")
            return []
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪指标"""
        try:
            # 模拟市场情绪数据
            # 实际实现中可以调用专业的情绪分析API
            sentiment_data = {
                'overall_sentiment': 'neutral',  # positive, neutral, negative
                'sentiment_score': 0.1,  # -1 to 1
                'bull_bear_ratio': 1.2,  # 多空比例
                'fear_greed_index': 45,  # 恐惧贪婪指数 0-100
                'vix_level': 18.5,  # VIX指数
                'update_time': datetime.now().isoformat()
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"获取市场情绪失败: {e}")
            return {}
    
    async def get_sector_news(self, sector: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取行业新闻"""
        try:
            sector_keywords = {
                '科技': ['科技', '人工智能', '芯片', '5G', '互联网'],
                '医药': ['医药', '生物', '疫苗', '医疗', '健康'],
                '新能源': ['新能源', '电池', '光伏', '风电', '储能'],
                '消费': ['消费', '零售', '品牌', '食品', '饮料'],
                '金融': ['银行', '保险', '证券', '金融科技', '支付'],
                '地产': ['房地产', '建筑', '基建', '城市化', '土地']
            }
            
            keywords = sector_keywords.get(sector, [sector])
            news_list = await self.get_etf_related_news(keywords, limit)
            
            return news_list
            
        except Exception as e:
            logger.error(f"获取行业新闻失败 {sector}: {e}")
            return []
    
    async def get_research_reports(self, asset_class: str = None, 
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """获取研究报告"""
        try:
            # 模拟研究报告数据
            # 实际实现中需要接入专业的研报数据源
            reports = [
                {
                    'title': f'{asset_class or "市场"}投资策略报告',
                    'author': '某证券研究所',
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'summary': f'关于{asset_class or "市场"}的最新投资策略分析...',
                    'rating': 'BUY',
                    'target_price': None,
                    'report_url': 'https://example.com/report/1'
                }
                for i in range(min(limit, 5))
            ]
            
            return reports
            
        except Exception as e:
            logger.error(f"获取研究报告失败: {e}")
            return []
    
    def _format_sina_news(self, data: dict) -> List[Dict[str, Any]]:
        """格式化新浪财经新闻数据"""
        try:
            news_list = []
            items = data.get('data', {}).get('items', [])
            
            for item in items:
                news_item = {
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'publish_time': item.get('publish_time', ''),
                    'source': 'sina',
                    'category': item.get('category', 'finance'),
                    'keywords': item.get('keywords', [])
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            logger.error(f"格式化新浪新闻数据失败: {e}")
            return []
    
    def _format_eastmoney_news(self, data: dict) -> List[Dict[str, Any]]:
        """格式化东方财富新闻数据"""
        try:
            news_list = []
            items = data.get('result', [])
            
            for item in items:
                news_item = {
                    'title': item.get('title', ''),
                    'summary': item.get('content', '')[:200],
                    'url': item.get('url', ''),
                    'publish_time': item.get('time', ''),
                    'source': 'eastmoney',
                    'category': 'finance',
                    'keywords': []
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            logger.error(f"格式化东方财富新闻数据失败: {e}")
            return []
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """新闻去重"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    async def get_hot_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门话题"""
        try:
            # 模拟热门话题数据
            # 实际实现中可以通过分析新闻热度、搜索量等指标
            hot_topics = [
                {
                    'topic': 'AI概念股',
                    'heat_score': 95,
                    'trend': 'up',  # up, down, stable
                    'related_etfs': ['159819.SZ', '515070.SH'],
                    'description': '人工智能相关概念持续火热'
                },
                {
                    'topic': '新能源汽车',
                    'heat_score': 88,
                    'trend': 'stable',
                    'related_etfs': ['515030.SH', '516390.SH'],
                    'description': '新能源汽车行业稳步发展'
                }
            ]
            
            return hot_topics[:limit]
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return []


# 创建全局新闻服务实例
news_service = NewsService()
