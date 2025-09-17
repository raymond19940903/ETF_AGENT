"""ETF数据服务"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.etf import ETFBasicInfo, ETFPriceData, ETFPerformanceMetrics
from app.data.wind_service import WindService
from app.cache.service import CacheService
import logging

logger = logging.getLogger(__name__)


class ETFService:
    """ETF数据服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.wind_service = WindService()
        self.cache_service = CacheService()
    
    async def get_etf_list(self, asset_class: Optional[str] = None, 
                          sector: Optional[str] = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """获取ETF列表"""
        try:
            # 生成缓存键
            cache_key = f"{asset_class or 'all'}_{sector or 'all'}_{limit}"
            
            # 先从缓存获取
            cached_data = await self.cache_service.get_etf_list(cache_key)
            if cached_data:
                logger.info(f"从缓存获取ETF列表: {cache_key}")
                return cached_data
            
            # 从数据库查询
            query = self.db.query(ETFBasicInfo)
            
            if asset_class:
                query = query.filter(ETFBasicInfo.asset_class.like(f"%{asset_class}%"))
            
            if sector:
                # 注意：删减后的模型没有sector字段，这里需要基于名称模糊匹配
                query = query.filter(ETFBasicInfo.etf_name.like(f"%{sector}%"))
            
            query = query.filter(ETFBasicInfo.status == "active")
            query = query.order_by(ETFBasicInfo.fund_scale.desc())
            
            etfs = query.limit(limit).all()
            
            # 转换为字典格式
            etf_list = []
            for etf in etfs:
                etf_dict = {
                    'id': etf.id,
                    'etf_code': etf.etf_code,
                    'etf_name': etf.etf_name,
                    'full_name': etf.full_name,
                    'asset_class': etf.asset_class,
                    'investment_type': etf.investment_type,
                    'fund_company': etf.fund_company,
                    'listing_date': str(etf.listing_date) if etf.listing_date else None,
                    'fund_scale': etf.fund_scale,
                    'status': etf.status
                }
                etf_list.append(etf_dict)
            
            # 如果数据库为空，从Wind获取数据
            if not etf_list:
                logger.info("数据库ETF数据为空，从Wind获取")
                etf_list = await self._sync_etf_data_from_wind(asset_class, sector, limit)
            
            # 缓存结果
            await self.cache_service.set_etf_list(cache_key, etf_list)
            
            return etf_list
            
        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            return []
    
    async def get_etf_detail(self, etf_code: str) -> Optional[Dict[str, Any]]:
        """获取ETF详细信息"""
        try:
            # 先从缓存获取
            cached_data = await self.cache_service.get_etf_data(etf_code)
            if cached_data:
                logger.info(f"从缓存获取ETF详情: {etf_code}")
                return cached_data
            
            # 从数据库查询
            etf = self.db.query(ETFBasicInfo).filter(ETFBasicInfo.etf_code == etf_code).first()
            
            if not etf:
                # 从Wind同步数据
                etf_info = await self._sync_single_etf_from_wind(etf_code)
                if not etf_info:
                    return None
                etf = self.db.query(ETFBasicInfo).filter(ETFBasicInfo.etf_code == etf_code).first()
            
            if not etf:
                return None
            
            # 获取Wind的实时绩效数据
            performance_metrics = {}
            try:
                with self.wind_service:
                    performance_metrics = self.wind_service.get_etf_performance_metrics(etf_code)
            except Exception as e:
                logger.warning(f"获取ETF绩效指标失败 {etf_code}: {e}")
            
            etf_detail = {
                'id': etf.id,
                'code': etf.code,
                'name': etf.name,
                'full_name': etf.full_name,
                'asset_class': etf.asset_class,
                'sector': etf.sector,
                'region': etf.region,
                'currency': etf.currency,
                'nav': etf.nav,
                'market_cap': etf.market_cap,
                'expense_ratio': etf.expense_ratio,
                'dividend_yield': etf.dividend_yield,
                'volatility': etf.volatility,
                'beta': etf.beta,
                'sharpe_ratio': etf.sharpe_ratio,
                'description': etf.description,
                'investment_objective': etf.investment_objective,
                'listing_date': etf.listing_date,
                'status': etf.status,
                'performance_metrics': performance_metrics
            }
            
            # 缓存结果
            await self.cache_service.set_etf_data(etf_code, etf_detail)
            
            return etf_detail
            
        except Exception as e:
            logger.error(f"获取ETF详情失败 {etf_code}: {e}")
            return None
    
    async def search_etf(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索ETF"""
        try:
            # 从数据库搜索
            query = self.db.query(ETFBasicInfo).filter(
                (ETFBasicInfo.etf_name.like(f"%{keyword}%")) |
                (ETFBasicInfo.full_name.like(f"%{keyword}%")) |
                (ETFBasicInfo.asset_class.like(f"%{keyword}%"))
            )
            
            query = query.filter(ETFBasicInfo.status == "active")
            query = query.order_by(ETFBasicInfo.fund_scale.desc())
            
            etfs = query.limit(limit).all()
            
            etf_list = []
            for etf in etfs:
                etf_dict = {
                    'id': etf.id,
                    'code': etf.code,
                    'name': etf.name,
                    'full_name': etf.full_name,
                    'asset_class': etf.asset_class,
                    'sector': etf.sector,
                    'nav': etf.nav,
                    'market_cap': etf.market_cap
                }
                etf_list.append(etf_dict)
            
            # 如果数据库搜索结果不足，从Wind补充搜索
            if len(etf_list) < limit:
                try:
                    with self.wind_service:
                        wind_results = self.wind_service.search_etf_by_keyword(keyword, limit)
                        # 合并结果并去重
                        existing_codes = {etf['code'] for etf in etf_list}
                        for wind_etf in wind_results:
                            if wind_etf['code'] not in existing_codes:
                                etf_list.append({
                                    'code': wind_etf['code'],
                                    'name': wind_etf['name'],
                                    'full_name': wind_etf.get('full_name', ''),
                                    'asset_class': wind_etf.get('industry', ''),
                                    'sector': wind_etf.get('sector', ''),
                                    'listing_date': wind_etf.get('listing_date', '')
                                })
                except Exception as e:
                    logger.warning(f"Wind搜索ETF失败: {e}")
            
            return etf_list[:limit]
            
        except Exception as e:
            logger.error(f"搜索ETF失败 {keyword}: {e}")
            return []
    
    async def get_etf_price_history(self, etf_code: str, 
                                   days: int = 365) -> List[Dict[str, Any]]:
        """获取ETF价格历史"""
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            with self.wind_service:
                price_data = self.wind_service.get_etf_price_data(etf_code, start_date, end_date)
            
            return price_data
            
        except Exception as e:
            logger.error(f"获取ETF价格历史失败 {etf_code}: {e}")
            return []
    
    async def _sync_etf_data_from_wind(self, asset_class: Optional[str] = None,
                                     sector: Optional[str] = None,
                                     limit: int = 50) -> List[Dict[str, Any]]:
        """从Wind同步ETF数据"""
        try:
            with self.wind_service:
                wind_etfs = self.wind_service.get_etf_list(asset_class, sector)
            
            etf_list = []
            for wind_etf in wind_etfs[:limit]:
                # 检查数据库中是否已存在
                existing_etf = self.db.query(ETFBasicInfo).filter(
                    ETFBasicInfo.etf_code == wind_etf['code']
                ).first()
                
                if not existing_etf:
                    # 创建新的ETF记录
                    new_etf = ETFBasicInfo(
                        etf_code=wind_etf['code'],
                        etf_name=wind_etf['name'],
                        full_name=wind_etf.get('full_name', ''),
                        asset_class=wind_etf.get('industry', ''),
                        investment_type=wind_etf.get('investment_type', ''),
                        listing_date=wind_etf.get('listing_date', ''),
                        status='active'
                    )
                    
                    self.db.add(new_etf)
                    existing_etf = new_etf
                
                etf_dict = {
                    'code': existing_etf.code,
                    'name': existing_etf.name,
                    'full_name': existing_etf.full_name,
                    'asset_class': existing_etf.asset_class,
                    'sector': existing_etf.sector,
                    'listing_date': existing_etf.listing_date
                }
                etf_list.append(etf_dict)
            
            self.db.commit()
            logger.info(f"从Wind同步了 {len(etf_list)} 个ETF")
            
            return etf_list
            
        except Exception as e:
            logger.error(f"从Wind同步ETF数据失败: {e}")
            self.db.rollback()
            return []
    
    async def _sync_single_etf_from_wind(self, etf_code: str) -> Optional[Dict[str, Any]]:
        """从Wind同步单个ETF数据"""
        try:
            with self.wind_service:
                wind_etf = self.wind_service.get_etf_basic_info(etf_code)
            
            if not wind_etf:
                return None
            
            # 创建新的ETF记录
            new_etf = ETFBasicInfo(
                etf_code=wind_etf['code'],
                etf_name=wind_etf['name'],
                full_name=wind_etf.get('full_name', ''),
                asset_class=wind_etf.get('industry', ''),
                investment_type=wind_etf.get('investment_type', ''),
                listing_date=wind_etf.get('listing_date', ''),
                status='active'
            )
            
            self.db.add(new_etf)
            self.db.commit()
            
            logger.info(f"从Wind同步ETF: {etf_code}")
            
            return {
                'code': new_etf.code,
                'name': new_etf.name,
                'full_name': new_etf.full_name,
                'asset_class': new_etf.asset_class,
                'sector': new_etf.sector,
                'listing_date': new_etf.listing_date
            }
            
        except Exception as e:
            logger.error(f"从Wind同步ETF失败 {etf_code}: {e}")
            self.db.rollback()
            return None
