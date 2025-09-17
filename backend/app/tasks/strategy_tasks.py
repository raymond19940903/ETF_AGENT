"""策略相关异步任务"""
from typing import Dict, Any
from celery import current_task
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.strategy.engine import StrategyEngine
from app.strategy.backtest import BacktestEngine
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="run_strategy_backtest")
def run_strategy_backtest(self, strategy_config: Dict[str, Any], 
                         strategy_id: int = None,
                         backtest_period: int = 365) -> Dict[str, Any]:
    """执行策略回测异步任务"""
    try:
        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': '初始化回测引擎'})
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化回测引擎
            backtest_engine = BacktestEngine(db)
            
            self.update_state(state='PROGRESS', meta={'progress': 30, 'status': '获取历史数据'})
            
            # 执行回测
            result = backtest_engine.run_backtest(
                strategy_config, backtest_period
            )
            
            self.update_state(state='PROGRESS', meta={'progress': 80, 'status': '计算绩效指标'})
            
            # 如果有策略ID，保存回测结果
            if strategy_id and result.get("success"):
                backtest_engine.save_backtest_results(strategy_id, result)
            
            self.update_state(state='PROGRESS', meta={'progress': 100, 'status': '回测完成'})
            
            logger.info(f"策略回测任务完成: strategy_id={strategy_id}")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略回测任务失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name="generate_strategy_async")
def generate_strategy_async(self, investment_elements: Dict[str, Any],
                           constraints: Dict[str, Any] = None) -> Dict[str, Any]:
    """异步生成策略任务"""
    try:
        if constraints is None:
            constraints = {}
        
        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': '分析投资要素'})
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化策略引擎
            strategy_engine = StrategyEngine(db)
            
            self.update_state(state='PROGRESS', meta={'progress': 30, 'status': '构建ETF候选池'})
            
            # 生成策略
            result = strategy_engine.generate_strategy(investment_elements, constraints)
            
            self.update_state(state='PROGRESS', meta={'progress': 80, 'status': '优化配置权重'})
            
            # 如果生成成功，执行简单回测
            if result.get("success") and result.get("strategy"):
                self.update_state(state='PROGRESS', meta={'progress': 90, 'status': '计算预期绩效'})
                
                # 这里可以添加简单的绩效估算
                strategy = result["strategy"]
                performance = strategy.get("performance_estimates", {})
                
                result["strategy"]["estimated_performance"] = performance
            
            self.update_state(state='PROGRESS', meta={'progress': 100, 'status': '策略生成完成'})
            
            logger.info("策略生成任务完成")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略生成任务失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name="optimize_strategy_async")
def optimize_strategy_async(self, current_strategy: Dict[str, Any],
                           user_feedback: Dict[str, Any]) -> Dict[str, Any]:
    """异步优化策略任务"""
    try:
        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': '分析用户反馈'})
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化策略引擎
            strategy_engine = StrategyEngine(db)
            
            self.update_state(state='PROGRESS', meta={'progress': 50, 'status': '优化策略配置'})
            
            # 执行策略优化
            result = strategy_engine.optimize_strategy(current_strategy, user_feedback)
            
            self.update_state(state='PROGRESS', meta={'progress': 100, 'status': '优化完成'})
            
            logger.info("策略优化任务完成")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略优化任务失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(name="calculate_strategy_metrics")
def calculate_strategy_metrics(strategy_id: int) -> Dict[str, Any]:
    """计算策略绩效指标"""
    try:
        db = SessionLocal()
        
        try:
            # 这里可以添加策略绩效计算逻辑
            # 例如：计算实时收益、风险指标等
            
            logger.info(f"策略绩效计算完成: strategy_id={strategy_id}")
            return {
                "success": True,
                "strategy_id": strategy_id,
                "metrics": {}
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略绩效计算失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "strategy_id": strategy_id
        }
