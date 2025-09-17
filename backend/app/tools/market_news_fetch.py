"""市场资讯获取工具"""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from app.data.news_service import NewsService
import logging

logger = logging.getLogger(__name__)


class MarketNewsFetchInput(BaseModel):
    """市场资讯获取工具输入"""
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    category: str = Field("finance", description="资讯类别")
    limit: int = Field(10, description="返回数量")


class MarketNewsFetchTool(BaseTool):
    """市场资讯获取工具"""
    name = "market_news_fetch_tool"
    description = "通过HTTP请求获取市场资讯和研报信息，用于策略推荐"
    args_schema = MarketNewsFetchInput
    
    def __init__(self):
        super().__init__()
        self.news_service = NewsService()
    
    def _run(self, keywords: Optional[List[str]] = None,
             category: str = "finance",
             limit: int = 10) -> Dict[str, Any]:
        """执行市场资讯获取"""
        try:
            # 同步包装异步调用
            import asyncio
            
            async def fetch_news():
                async with self.news_service:
                    if keywords:
                        return await self.news_service.get_etf_related_news(keywords, limit)
                    else:
                        return await self.news_service.get_financial_news(category, limit)
            
            news_data = asyncio.run(fetch_news())
            
            result = {
                "success": True,
                "news_data": news_data,
                "total_count": len(news_data),
                "keywords": keywords,
                "category": category
            }
            
            logger.info(f"市场资讯获取成功，返回 {len(news_data)} 条资讯")
            return result
            
        except Exception as e:
            logger.error(f"市场资讯获取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "news_data": [],
                "total_count": 0
            }
    
    async def _arun(self, keywords: Optional[List[str]] = None,
                   category: str = "finance",
                   limit: int = 10) -> Dict[str, Any]:
        """异步执行市场资讯获取"""
        try:
            async with self.news_service:
                if keywords:
                    news_data = await self.news_service.get_etf_related_news(keywords, limit)
                else:
                    news_data = await self.news_service.get_financial_news(category, limit)
            
            result = {
                "success": True,
                "news_data": news_data,
                "total_count": len(news_data),
                "keywords": keywords,
                "category": category
            }
            
            logger.info(f"市场资讯获取成功，返回 {len(news_data)} 条资讯")
            return result
            
        except Exception as e:
            logger.error(f"市场资讯获取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "news_data": [],
                "total_count": 0
            }
