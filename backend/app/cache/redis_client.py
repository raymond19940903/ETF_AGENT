"""Redis客户端配置"""
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis异步客户端"""
    
    def __init__(self):
        self.pool = None
        self.redis = None
    
    async def connect(self):
        """连接Redis"""
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            self.redis = redis.Redis(connection_pool=self.pool)
            
            # 测试连接
            await self.redis.ping()
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis连接已断开")
    
    async def get(self, key: str):
        """获取缓存值"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET错误 {key}: {e}")
            return None
    
    async def set(self, key: str, value, ttl: int = None):
        """设置缓存值"""
        try:
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            if ttl:
                await self.redis.setex(key, ttl, json_value)
            else:
                await self.redis.set(key, json_value)
            return True
        except Exception as e:
            logger.error(f"Redis SET错误 {key}: {e}")
            return False
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE错误 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS错误 {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int):
        """设置过期时间"""
        try:
            await self.redis.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE错误 {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1):
        """递增"""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR错误 {key}: {e}")
            return None
    
    async def hget(self, name: str, key: str):
        """获取哈希字段值"""
        try:
            value = await self.redis.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis HGET错误 {name}.{key}: {e}")
            return None
    
    async def hset(self, name: str, key: str, value):
        """设置哈希字段值"""
        try:
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            await self.redis.hset(name, key, json_value)
            return True
        except Exception as e:
            logger.error(f"Redis HSET错误 {name}.{key}: {e}")
            return False
    
    async def hgetall(self, name: str):
        """获取所有哈希字段"""
        try:
            data = await self.redis.hgetall(name)
            result = {}
            for key, value in data.items():
                try:
                    result[key] = json.loads(value)
                except:
                    result[key] = value
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL错误 {name}: {e}")
            return {}
    
    async def hdel(self, name: str, key: str):
        """删除哈希字段"""
        try:
            await self.redis.hdel(name, key)
            return True
        except Exception as e:
            logger.error(f"Redis HDEL错误 {name}.{key}: {e}")
            return False


# 创建全局Redis客户端实例
redis_client = RedisClient()
