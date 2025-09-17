"""缓存服务"""
from typing import Any, Optional
from app.cache.redis_client import redis_client
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.client = redis_client
    
    # 用户会话缓存
    async def set_user_session(self, user_id: int, session_data: dict) -> bool:
        """设置用户会话缓存"""
        key = f"user:session:{user_id}"
        return await self.client.set(key, session_data, settings.CACHE_TTL_USER_SESSION)
    
    async def get_user_session(self, user_id: int) -> Optional[dict]:
        """获取用户会话缓存"""
        key = f"user:session:{user_id}"
        return await self.client.get(key)
    
    async def delete_user_session(self, user_id: int) -> bool:
        """删除用户会话缓存"""
        key = f"user:session:{user_id}"
        return await self.client.delete(key)
    
    # ETF数据缓存
    async def set_etf_data(self, etf_code: str, data: dict) -> bool:
        """设置ETF数据缓存"""
        key = f"etf:data:{etf_code}"
        return await self.client.set(key, data, settings.CACHE_TTL_ETF_DATA)
    
    async def get_etf_data(self, etf_code: str) -> Optional[dict]:
        """获取ETF数据缓存"""
        key = f"etf:data:{etf_code}"
        return await self.client.get(key)
    
    async def set_etf_list(self, filter_key: str, etf_list: list) -> bool:
        """设置ETF列表缓存"""
        key = f"etf:list:{filter_key}"
        return await self.client.set(key, etf_list, settings.CACHE_TTL_ETF_DATA)
    
    async def get_etf_list(self, filter_key: str) -> Optional[list]:
        """获取ETF列表缓存"""
        key = f"etf:list:{filter_key}"
        return await self.client.get(key)
    
    # 策略缓存
    async def set_strategy_data(self, strategy_id: int, data: dict) -> bool:
        """设置策略数据缓存"""
        key = f"strategy:data:{strategy_id}"
        return await self.client.set(key, data, settings.CACHE_TTL_STRATEGY)
    
    async def get_strategy_data(self, strategy_id: int) -> Optional[dict]:
        """获取策略数据缓存"""
        key = f"strategy:data:{strategy_id}"
        return await self.client.get(key)
    
    async def set_user_strategies(self, user_id: int, strategies: list) -> bool:
        """设置用户策略列表缓存"""
        key = f"user:strategies:{user_id}"
        return await self.client.set(key, strategies, settings.CACHE_TTL_STRATEGY)
    
    async def get_user_strategies(self, user_id: int) -> Optional[list]:
        """获取用户策略列表缓存"""
        key = f"user:strategies:{user_id}"
        return await self.client.get(key)
    
    async def delete_user_strategies(self, user_id: int) -> bool:
        """删除用户策略列表缓存"""
        key = f"user:strategies:{user_id}"
        return await self.client.delete(key)
    
    # 市场资讯缓存
    async def set_news_data(self, news_key: str, news_data: list) -> bool:
        """设置市场资讯缓存"""
        key = f"news:data:{news_key}"
        return await self.client.set(key, news_data, settings.CACHE_TTL_NEWS)
    
    async def get_news_data(self, news_key: str) -> Optional[list]:
        """获取市场资讯缓存"""
        key = f"news:data:{news_key}"
        return await self.client.get(key)
    
    # 对话上下文缓存
    async def set_conversation_context(self, session_id: str, context: dict) -> bool:
        """设置对话上下文缓存"""
        key = f"conversation:context:{session_id}"
        return await self.client.set(key, context, settings.CACHE_TTL_CONVERSATION)
    
    async def get_conversation_context(self, session_id: str) -> Optional[dict]:
        """获取对话上下文缓存"""
        key = f"conversation:context:{session_id}"
        return await self.client.get(key)
    
    async def update_conversation_context(self, session_id: str, context_update: dict) -> bool:
        """更新对话上下文缓存"""
        key = f"conversation:context:{session_id}"
        current_context = await self.client.get(key) or {}
        current_context.update(context_update)
        return await self.client.set(key, current_context, settings.CACHE_TTL_CONVERSATION)
    
    async def delete_conversation_context(self, session_id: str) -> bool:
        """删除对话上下文缓存"""
        key = f"conversation:context:{session_id}"
        return await self.client.delete(key)
    
    # 任务状态缓存
    async def set_task_status(self, task_id: str, status: dict) -> bool:
        """设置任务状态缓存"""
        key = f"task:status:{task_id}"
        return await self.client.set(key, status, 3600)  # 1小时
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态缓存"""
        key = f"task:status:{task_id}"
        return await self.client.get(key)
    
    async def update_task_status(self, task_id: str, status_update: dict) -> bool:
        """更新任务状态缓存"""
        key = f"task:status:{task_id}"
        current_status = await self.client.get(key) or {}
        current_status.update(status_update)
        return await self.client.set(key, current_status, 3600)
    
    # 通用缓存方法
    async def set_cache(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置通用缓存"""
        if ttl is None:
            ttl = settings.CACHE_TTL_DEFAULT
        return await self.client.set(key, value, ttl)
    
    async def get_cache(self, key: str) -> Any:
        """获取通用缓存"""
        return await self.client.get(key)
    
    async def delete_cache(self, key: str) -> bool:
        """删除通用缓存"""
        return await self.client.delete(key)
    
    async def exists_cache(self, key: str) -> bool:
        """检查缓存是否存在"""
        return await self.client.exists(key)
    
    async def clear_user_cache(self, user_id: int) -> bool:
        """清除用户相关缓存"""
        try:
            await self.delete_user_session(user_id)
            await self.delete_user_strategies(user_id)
            logger.info(f"已清除用户 {user_id} 的缓存")
            return True
        except Exception as e:
            logger.error(f"清除用户 {user_id} 缓存失败: {e}")
            return False


# 创建全局缓存服务实例
cache_service = CacheService()
