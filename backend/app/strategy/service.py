"""策略服务"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.strategy import Strategy, StrategyETFAllocation
from app.models.user import User
from app.strategy.engine import StrategyEngine
from app.strategy.backtest import BacktestEngine
from app.cache.service import CacheService
import logging

logger = logging.getLogger(__name__)


class StrategyService:
    """策略服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.strategy_engine = StrategyEngine(db)
        self.backtest_engine = BacktestEngine(db)
        self.cache_service = CacheService()
    
    async def create_strategy(self, user_id: int, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建策略"""
        try:
            # 创建策略记录
            strategy = Strategy(
                user_id=user_id,
                name=strategy_data["name"],
                description=strategy_data.get("description"),
                investment_philosophy=strategy_data.get("investment_philosophy"),
                target_return=strategy_data.get("target_return"),
                max_drawdown=strategy_data.get("max_drawdown"),
                risk_level=strategy_data.get("risk_level"),
                investment_amount=strategy_data.get("investment_amount"),
                asset_allocation=strategy_data.get("asset_allocation"),
                constraints=strategy_data.get("constraints"),
                preferences=strategy_data.get("preferences"),
                status="active"
            )
            
            self.db.add(strategy)
            self.db.commit()
            self.db.refresh(strategy)
            
            # 添加ETF配置
            etf_allocations = strategy_data.get("etf_allocations", [])
            for allocation_data in etf_allocations:
                allocation = StrategyETFAllocation(
                    strategy_id=strategy.id,
                    etf_code=allocation_data["etf_code"],
                    etf_name=allocation_data["etf_name"],
                    allocation_percentage=allocation_data["weight"],
                    asset_class=allocation_data.get("asset_class"),
                    sector=allocation_data.get("sector")
                )
                self.db.add(allocation)
            
            self.db.commit()
            
            # 清除用户策略缓存
            await self.cache_service.delete_user_strategies(user_id)
            
            # 更新用户类型
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.is_new_user:
                user.is_new_user = False
                self.db.commit()
            
            logger.info(f"策略创建成功: {strategy.id}")
            
            return {
                "success": True,
                "strategy_id": strategy.id,
                "strategy": self._format_strategy_response(strategy)
            }
            
        except Exception as e:
            logger.error(f"创建策略失败: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_strategy(self, strategy_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取策略详情"""
        try:
            # 先从缓存获取
            cached_strategy = await self.cache_service.get_strategy_data(strategy_id)
            if cached_strategy:
                return cached_strategy
            
            # 从数据库查询
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id,
                Strategy.status == "active"
            ).first()
            
            if not strategy:
                return None
            
            strategy_data = self._format_strategy_response(strategy)
            
            # 缓存结果
            await self.cache_service.set_strategy_data(strategy_id, strategy_data)
            
            return strategy_data
            
        except Exception as e:
            logger.error(f"获取策略失败: {e}")
            return None
    
    async def get_user_strategies(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户策略列表"""
        try:
            # 先从缓存获取
            cached_strategies = await self.cache_service.get_user_strategies(user_id)
            if cached_strategies:
                return cached_strategies
            
            # 从数据库查询
            strategies = self.db.query(Strategy).filter(
                Strategy.user_id == user_id,
                Strategy.status == "active"
            ).order_by(Strategy.updated_at.desc()).all()
            
            strategy_list = []
            for strategy in strategies:
                strategy_data = self._format_strategy_response(strategy, include_allocations=False)
                strategy_list.append(strategy_data)
            
            # 缓存结果
            await self.cache_service.set_user_strategies(user_id, strategy_list)
            
            return strategy_list
            
        except Exception as e:
            logger.error(f"获取用户策略失败: {e}")
            return []
    
    async def update_strategy(self, strategy_id: int, user_id: int, 
                           update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新策略"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id
            ).first()
            
            if not strategy:
                return {
                    "success": False,
                    "error": "策略不存在"
                }
            
            # 更新策略字段
            for field, value in update_data.items():
                if hasattr(strategy, field) and value is not None:
                    setattr(strategy, field, value)
            
            # 更新ETF配置
            if "etf_allocations" in update_data:
                # 删除现有配置
                self.db.query(StrategyETFAllocation).filter(
                    StrategyETFAllocation.strategy_id == strategy_id
                ).delete()
                
                # 添加新配置
                for allocation_data in update_data["etf_allocations"]:
                    allocation = StrategyETFAllocation(
                        strategy_id=strategy_id,
                        etf_code=allocation_data["etf_code"],
                        etf_name=allocation_data["etf_name"],
                        allocation_percentage=allocation_data["weight"],
                        asset_class=allocation_data.get("asset_class"),
                        sector=allocation_data.get("sector")
                    )
                    self.db.add(allocation)
            
            self.db.commit()
            self.db.refresh(strategy)
            
            # 清除相关缓存
            await self.cache_service.delete_cache(f"strategy:data:{strategy_id}")
            await self.cache_service.delete_user_strategies(user_id)
            
            logger.info(f"策略更新成功: {strategy_id}")
            
            return {
                "success": True,
                "strategy": self._format_strategy_response(strategy)
            }
            
        except Exception as e:
            logger.error(f"更新策略失败: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_strategy(self, strategy_id: int, user_id: int) -> bool:
        """删除策略"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id
            ).first()
            
            if not strategy:
                return False
            
            # 软删除
            strategy.status = "deleted"
            self.db.commit()
            
            # 清除相关缓存
            await self.cache_service.delete_cache(f"strategy:data:{strategy_id}")
            await self.cache_service.delete_user_strategies(user_id)
            
            logger.info(f"策略删除成功: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除策略失败: {e}")
            self.db.rollback()
            return False
    
    async def run_backtest(self, strategy_id: int, user_id: int, 
                          period_days: int = 365) -> Dict[str, Any]:
        """执行策略回测"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id
            ).first()
            
            if not strategy:
                return {
                    "success": False,
                    "error": "策略不存在"
                }
            
            # 构建策略配置
            strategy_config = {
                "etf_allocations": [
                    {
                        "etf_code": alloc.etf_code,
                        "etf_name": alloc.etf_name,
                        "weight": alloc.allocation_percentage,
                        "asset_class": alloc.asset_class
                    }
                    for alloc in strategy.etf_allocations
                ]
            }
            
            # 执行回测
            result = await self.backtest_engine.run_backtest(strategy_config, period_days)
            
            # 保存回测结果
            if result.get("success"):
                await self.backtest_engine.save_backtest_results(strategy_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"执行回测失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_strategy_response(self, strategy: Strategy, 
                                include_allocations: bool = True) -> Dict[str, Any]:
        """格式化策略响应"""
        strategy_data = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "investment_philosophy": strategy.investment_philosophy,
            "target_return": strategy.target_return,
            "max_drawdown": strategy.max_drawdown,
            "risk_level": strategy.risk_level,
            "investment_amount": strategy.investment_amount,
            "rebalance_frequency": strategy.rebalance_frequency,
            "asset_allocation": strategy.asset_allocation,
            "status": strategy.status,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat()
        }
        
        if include_allocations:
            etf_allocations = []
            for allocation in strategy.etf_allocations:
                etf_allocations.append({
                    "etf_code": allocation.etf_code,
                    "etf_name": allocation.etf_name,
                    "weight": allocation.allocation_percentage,
                    "asset_class": allocation.asset_class,
                    "sector": allocation.sector
                })
            strategy_data["etf_allocations"] = etf_allocations
        
        return strategy_data
