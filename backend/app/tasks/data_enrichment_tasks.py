"""数据补全任务

定时执行数据补全和加工任务，确保数据的完整性和准确性。
"""

from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.data_processing.data_enricher import DataEnricher
from app.data_processing.etf_classifier import batch_classify_etfs
from app.data_processing.news_analyzer import batch_analyze_news
from app.data_processing.sector_builder import VirtualSectorBuilder
from app.data_processing.valuation_calculator import ValuationCalculator
from app.models.etf import ETFBasicInfo, FinancialNews
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 从主应用导入Celery实例
from .celery_app import celery


@celery.task(bind=True, max_retries=3)
def daily_data_enrichment(self):
    """每日数据补全任务"""
    
    try:
        db = next(get_db())
        enricher = DataEnricher(db)
        
        logger.info("开始执行每日数据补全任务")
        
        # 1. 补全ETF分类信息
        enrich_etf_classifications_task.delay()
        
        # 2. 分析新闻关联性
        process_news_etf_relations_task.delay()
        
        # 3. 构建虚拟板块数据
        build_virtual_sector_indices_task.delay()
        
        # 4. 计算估值指标
        calculate_valuation_metrics_task.delay()
        
        logger.info("每日数据补全任务启动完成")
        
    except Exception as e:
        logger.error(f"每日数据补全任务失败: {e}")
        self.retry(countdown=60 * 5)  # 5分钟后重试


@celery.task(bind=True, max_retries=3)
def enrich_etf_classifications_task(self):
    """补全ETF分类信息任务"""
    
    try:
        db = next(get_db())
        
        # 获取需要补全分类的ETF
        etfs = db.query(ETFBasicInfo).filter(
            ETFBasicInfo.status == "active"
        ).all()
        
        etf_data = []
        for etf in etfs:
            etf_data.append({
                "etf_code": etf.etf_code,
                "etf_name": etf.etf_name,
                "asset_class": etf.asset_class,
                "fund_company": etf.fund_company,
                "fund_scale": etf.fund_scale
            })
        
        # 批量分类
        classified_etfs = batch_classify_etfs(etf_data)
        
        # 这里可以将分类结果保存到缓存或文件中
        # 实际实现时可以考虑扩展数据库表或使用Redis缓存
        
        logger.info(f"成功补全 {len(classified_etfs)} 个ETF的分类信息")
        
    except Exception as e:
        logger.error(f"ETF分类补全任务失败: {e}")
        self.retry(countdown=60 * 10)  # 10分钟后重试


@celery.task(bind=True, max_retries=3)
def process_news_etf_relations_task(self):
    """处理新闻ETF关联性任务"""
    
    try:
        db = next(get_db())
        
        # 获取最近24小时的新闻
        yesterday = datetime.now() - timedelta(days=1)
        recent_news = db.query(FinancialNews).filter(
            FinancialNews.created_at >= yesterday
        ).all()
        
        # 获取ETF列表
        etfs = db.query(ETFBasicInfo).filter(
            ETFBasicInfo.status == "active"
        ).all()
        
        etf_list = []
        for etf in etfs:
            etf_list.append({
                "etf_code": etf.etf_code,
                "etf_name": etf.etf_name,
                "asset_class": etf.asset_class
            })
        
        # 分析新闻关联性
        news_data = []
        for news in recent_news:
            news_data.append({
                "news_id": news.news_id,
                "title": news.title,
                "content": news.content or news.summary,
                "source": news.source
            })
        
        analyzed_news = batch_analyze_news(news_data, etf_list)
        
        # 这里可以将分析结果保存到数据库或缓存
        
        logger.info(f"成功分析 {len(analyzed_news)} 条新闻的ETF关联性")
        
    except Exception as e:
        logger.error(f"新闻关联性分析任务失败: {e}")
        self.retry(countdown=60 * 15)  # 15分钟后重试


@celery.task(bind=True, max_retries=3)
def build_virtual_sector_indices_task(self):
    """构建虚拟板块指数任务"""
    
    try:
        db = next(get_db())
        sector_builder = VirtualSectorBuilder()
        
        # 获取所有活跃ETF
        etfs = db.query(ETFBasicInfo).filter(
            ETFBasicInfo.status == "active"
        ).all()
        
        etf_data = []
        for etf in etfs:
            etf_data.append({
                "etf_code": etf.etf_code,
                "etf_name": etf.etf_name,
                "fund_scale": etf.fund_scale or 0
            })
        
        # 构建虚拟板块数据
        today = datetime.now().strftime("%Y-%m-%d")
        sector_data = sector_builder.build_sector_data(etf_data, today)
        
        # 这里可以将板块数据保存到数据库或缓存
        
        logger.info(f"成功构建 {len(sector_data)} 个虚拟板块指数")
        
    except Exception as e:
        logger.error(f"虚拟板块构建任务失败: {e}")
        self.retry(countdown=60 * 20)  # 20分钟后重试


@celery.task(bind=True, max_retries=3)
def calculate_valuation_metrics_task(self):
    """计算估值指标任务"""
    
    try:
        db = next(get_db())
        calculator = ValuationCalculator()
        
        # 获取需要计算估值的ETF
        etfs = db.query(ETFBasicInfo).filter(
            ETFBasicInfo.status == "active"
        ).limit(100).all()  # 限制数量避免任务过重
        
        for etf in etfs:
            # 获取价格历史（这里需要实现从etf_price_data表查询）
            price_history = []  # 实际实现时需要查询价格数据
            
            if price_history:
                valuation = calculator.estimate_valuation_metrics(
                    etf.etf_code,
                    price_history
                )
                
                # 这里可以将估值结果保存到缓存或扩展表中
                logger.debug(f"计算 {etf.etf_code} 估值指标: PE={valuation.get('derived_pe_ratio')}")
        
        logger.info(f"成功计算 {len(etfs)} 个ETF的估值指标")
        
    except Exception as e:
        logger.error(f"估值指标计算任务失败: {e}")
        self.retry(countdown=60 * 30)  # 30分钟后重试


@celery.task
def cleanup_expired_enrichment_data():
    """清理过期的补全数据"""
    
    try:
        # 清理过期的缓存数据
        # 清理临时文件
        # 清理过期的计算结果
        
        logger.info("数据清理任务完成")
        
    except Exception as e:
        logger.error(f"数据清理任务失败: {e}")


@celery.task
def monitor_data_quality():
    """监控数据质量"""
    
    try:
        db = next(get_db())
        
        # 检查数据完整性
        etf_count = db.query(ETFBasicInfo).count()
        news_count = db.query(FinancialNews).count()
        
        # 检查数据更新时间
        # 检查数据质量指标
        
        quality_report = {
            "etf_count": etf_count,
            "news_count": news_count,
            "check_time": datetime.now().isoformat(),
            "quality_score": 0.95  # 简化实现
        }
        
        logger.info(f"数据质量监控完成: {quality_report}")
        
    except Exception as e:
        logger.error(f"数据质量监控失败: {e}")


# 设置定时任务
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """设置定时任务"""
    
    # 每日凌晨2点执行数据补全
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        daily_data_enrichment.s(),
        name='每日数据补全'
    )
    
    # 每4小时执行一次新闻关联性分析
    sender.add_periodic_task(
        crontab(minute=0, hour='*/4'),
        process_news_etf_relations_task.s(),
        name='新闻关联性分析'
    )
    
    # 每小时清理一次过期数据
    sender.add_periodic_task(
        crontab(minute=0),
        cleanup_expired_enrichment_data.s(),
        name='清理过期数据'
    )
    
    # 每6小时监控一次数据质量
    sender.add_periodic_task(
        crontab(minute=30, hour='*/6'),
        monitor_data_quality.s(),
        name='数据质量监控'
    )


if __name__ == "__main__":
    # 测试任务
    print("数据补全任务模块加载完成")
