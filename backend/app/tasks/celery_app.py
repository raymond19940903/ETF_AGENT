"""Celery应用配置"""
from celery import Celery
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# 创建Celery应用
celery_app = Celery(
    "etf_strategy_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.strategy_tasks",
        "app.tasks.data_tasks"
    ]
)

# 配置Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    
    # 任务路由
    task_routes={
        'app.tasks.strategy_tasks.*': {'queue': 'strategy'},
        'app.tasks.data_tasks.*': {'queue': 'data'},
    },
    
    # 任务配置
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # 工作进程配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 结果过期时间
    result_expires=3600,  # 1小时
    
    # 任务时间限制
    task_soft_time_limit=300,  # 5分钟软限制
    task_time_limit=600,       # 10分钟硬限制
    
    # 重试配置
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 任务发现
celery_app.autodiscover_tasks([
    'app.tasks.strategy_tasks',
    'app.tasks.data_tasks'
])


@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    logger.info(f'Request: {self.request!r}')
    return 'Debug task completed'


# Celery启动时的钩子
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """设置定期任务"""
    from celery.schedules import crontab
    
    # 每天凌晨同步ETF数据
    sender.add_periodic_task(
        crontab(hour=1, minute=0),
        'app.tasks.data_tasks.sync_etf_data',
        name='同步ETF数据'
    )
    
    # 每小时获取市场资讯
    sender.add_periodic_task(
        crontab(minute=0),
        'app.tasks.data_tasks.fetch_market_news',
        name='获取市场资讯'
    )


if __name__ == '__main__':
    celery_app.start()
