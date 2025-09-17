/**
 * 自研API缓存管理器
 * 替代RTK Query，提供轻量级的API缓存功能
 */

interface CacheItem<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
}

interface CacheOptions {
  ttl?: number; // 生存时间（毫秒）
  maxSize?: number; // 最大缓存条目数
}

class ApiCacheManager {
  private cache = new Map<string, CacheItem>();
  private accessOrder = new Map<string, number>(); // LRU跟踪
  private maxSize: number;
  private defaultTTL: number;
  private accessCounter = 0;

  constructor(options: CacheOptions = {}) {
    this.maxSize = options.maxSize || 100;
    this.defaultTTL = options.ttl || 5 * 60 * 1000; // 默认5分钟
  }

  /**
   * 获取缓存数据
   */
  get<T = any>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // 检查是否过期
    if (this.isExpired(item)) {
      this.delete(key);
      return null;
    }

    // 更新访问顺序（LRU）
    this.accessOrder.set(key, ++this.accessCounter);
    
    return item.data;
  }

  /**
   * 设置缓存数据
   */
  set<T = any>(key: string, data: T, ttl?: number): void {
    // 检查缓存大小，执行LRU淘汰
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evictLRU();
    }

    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    };

    this.cache.set(key, item);
    this.accessOrder.set(key, ++this.accessCounter);
  }

  /**
   * 删除缓存项
   */
  delete(key: string): boolean {
    this.accessOrder.delete(key);
    return this.cache.delete(key);
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear();
    this.accessOrder.clear();
    this.accessCounter = 0;
  }

  /**
   * 检查是否存在且未过期
   */
  has(key: string): boolean {
    const item = this.cache.get(key);
    
    if (!item) {
      return false;
    }

    if (this.isExpired(item)) {
      this.delete(key);
      return false;
    }

    return true;
  }

  /**
   * 批量失效缓存（支持模式匹配）
   */
  invalidate(pattern: string | RegExp): number {
    let count = 0;
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.delete(key);
        count++;
      }
    }

    return count;
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    const now = Date.now();
    let expiredCount = 0;

    for (const item of this.cache.values()) {
      if (this.isExpired(item)) {
        expiredCount++;
      }
    }

    return {
      totalItems: this.cache.size,
      expiredItems: expiredCount,
      validItems: this.cache.size - expiredCount,
      maxSize: this.maxSize,
      usage: (this.cache.size / this.maxSize) * 100
    };
  }

  /**
   * 清理过期缓存
   */
  cleanup(): number {
    let cleanedCount = 0;
    
    for (const [key, item] of this.cache.entries()) {
      if (this.isExpired(item)) {
        this.delete(key);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  private isExpired(item: CacheItem): boolean {
    return Date.now() - item.timestamp > item.ttl;
  }

  private evictLRU(): void {
    if (this.accessOrder.size === 0) return;

    // 找到最久未访问的key
    let oldestKey = '';
    let oldestAccess = Infinity;

    for (const [key, accessTime] of this.accessOrder.entries()) {
      if (accessTime < oldestAccess) {
        oldestAccess = accessTime;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.delete(oldestKey);
    }
  }
}

// 创建全局缓存实例
export const apiCache = new ApiCacheManager({
  maxSize: 200,
  ttl: 5 * 60 * 1000 // 5分钟
});

/**
 * API缓存装饰器
 */
export function withCache<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: { keyGenerator?: (...args: any[]) => string; ttl?: number } = {}
): T {
  return (async (...args: any[]) => {
    const key = options.keyGenerator ? options.keyGenerator(...args) : JSON.stringify(args);
    
    // 尝试从缓存获取
    const cached = apiCache.get(key);
    if (cached) {
      return cached;
    }

    // 执行原函数
    const result = await fn(...args);
    
    // 缓存结果
    apiCache.set(key, result, options.ttl);
    
    return result;
  }) as T;
}

/**
 * React Hook for API caching
 */
export function useApiCache() {
  return {
    get: apiCache.get.bind(apiCache),
    set: apiCache.set.bind(apiCache),
    delete: apiCache.delete.bind(apiCache),
    clear: apiCache.clear.bind(apiCache),
    invalidate: apiCache.invalidate.bind(apiCache),
    has: apiCache.has.bind(apiCache),
    getStats: apiCache.getStats.bind(apiCache),
    cleanup: apiCache.cleanup.bind(apiCache)
  };
}

export default apiCache;
