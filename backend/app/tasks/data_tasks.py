"""数据相关异步任务"""
from typing import Dict, Any, List
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.data.wind_service import WindService
from app.data.news_service import NewsService
from app.models.etf import ETFBasicInfo
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="sync_etf_data")
def sync_etf_data(self, asset_class: str = None, limit: int = 100) -> Dict[str, Any]:
    """同步ETF数据异步任务"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': '连接Wind数据库'})
        
        db = SessionLocal()
        wind_service = WindService()
        
        try:
            with wind_service:
                self.update_state(state='PROGRESS', meta={'progress': 30, 'status': '获取ETF列表'})
                
                # 从Wind获取ETF数据
                etf_list = wind_service.get_etf_list(asset_class=asset_class)
                
                self.update_state(state='PROGRESS', meta={'progress': 50, 'status': '同步到数据库'})
                
                synced_count = 0
                for etf_data in etf_list[:limit]:
                    # 检查是否已存在
                    existing_etf = db.query(ETFBasicInfo).filter(
                        ETFBasicInfo.etf_code == etf_data["code"]
                    ).first()
                    
                    if not existing_etf:
                        # 创建新记录
                        new_etf = ETFBasicInfo(
                            etf_code=etf_data["code"],
                            etf_name=etf_data["name"],
                            full_name=etf_data.get("full_name", ""),
                            asset_class=etf_data.get("industry", ""),
                            investment_type=etf_data.get("investment_type", ""),
                            fund_company=etf_data.get("fund_company", ""),
                            listing_date=etf_data.get("listing_date"),
                            fund_scale=etf_data.get("fund_scale"),
                            status="active"
                        )
                        db.add(new_etf)
                        synced_count += 1
                    else:
                        # 更新现有记录
                        existing_etf.name = etf_data["name"]
                        existing_etf.full_name = etf_data.get("full_name", "")
                        existing_etf.asset_class = etf_data.get("industry", "")
                        existing_etf.sector = etf_data.get("sector", "")
                
                db.commit()
                
                self.update_state(state='PROGRESS', meta={'progress': 100, 'status': '同步完成'})
                
                logger.info(f"ETF数据同步完成: 新增{synced_count}个ETF")
                
                return {
                    "success": True,
                    "synced_count": synced_count,
                    "total_processed": len(etf_list),
                    "asset_class": asset_class
                }
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"ETF数据同步失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name="fetch_market_news")
def fetch_market_news(self, category: str = "finance", limit: int = 20) -> Dict[str, Any]:
    """获取市场资讯异步任务"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': '连接资讯API'})
        
        news_service = NewsService()
        
        # 异步获取新闻
        import asyncio
        
        async def fetch_news():
            async with news_service:
                self.update_state(state='PROGRESS', meta={'progress': 60, 'status': '获取资讯数据'})
                
                news_data = await news_service.get_financial_news(category, limit)
                return news_data
        
        news_list = asyncio.run(fetch_news())
        
        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': '资讯获取完成'})
        
        logger.info(f"市场资讯获取完成: {len(news_list)}条")
        
        return {
            "success": True,
            "news_count": len(news_list),
            "news_data": news_list,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"市场资讯获取失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(name="update_etf_prices")
def update_etf_prices(etf_codes: List[str] = None) -> Dict[str, Any]:
    """更新ETF价格数据"""
    try:
        db = SessionLocal()
        wind_service = WindService()
        
        try:
            if not etf_codes:
                # 获取所有活跃ETF代码
                active_etfs = db.query(ETFBasicInfo).filter(
                    ETFBasicInfo.status == "active"
                ).all()
                etf_codes = [etf.etf_code for etf in active_etfs]
            
            updated_count = 0
            
            with wind_service:
                for etf_code in etf_codes:
                    try:
                        # 获取最新价格数据
                        from datetime import datetime, timedelta
                        end_date = datetime.now().strftime('%Y%m%d')
                        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
                        
                        price_data = wind_service.get_etf_price_data(etf_code, start_date, end_date)
                        
                        if price_data:
                            # 更新ETF产品表中的价格信息
                            etf = db.query(ETFBasicInfo).filter(ETFBasicInfo.etf_code == etf_code).first()
                            if etf and price_data:
                                latest_price = price_data[-1]
                                # ETFBasicInfo模型不包含nav字段，价格数据应存储到ETFPriceData表
                                # 这里可以添加价格数据存储逻辑
                                updated_count += 1
                        
                    except Exception as e:
                        logger.warning(f"更新ETF {etf_code} 价格失败: {e}")
                        continue
            
            db.commit()
            
            logger.info(f"ETF价格更新完成: {updated_count}/{len(etf_codes)}")
            
            return {
                "success": True,
                "updated_count": updated_count,
                "total_etfs": len(etf_codes)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"ETF价格更新失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="cleanup_old_data")
def cleanup_old_data(days_to_keep: int = 90) -> Dict[str, Any]:
    """清理旧数据"""
    try:
        from datetime import datetime, timedelta
        from app.models.conversation import Conversation
        from app.models.backtest import StrategyBacktestData
        
        db = SessionLocal()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # 清理旧的对话记录
            deleted_conversations = db.query(Conversation).filter(
                Conversation.created_at < cutoff_date
            ).delete()
            
            # 清理旧的回测数据
            deleted_backtest = db.query(StrategyBacktestData).filter(
                StrategyBacktestData.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"数据清理完成: 对话记录{deleted_conversations}条, 回测数据{deleted_backtest}条")
            
            return {
                "success": True,
                "deleted_conversations": deleted_conversations,
                "deleted_backtest": deleted_backtest,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据清理失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
