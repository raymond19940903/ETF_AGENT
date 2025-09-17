"""策略API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.strategy import Strategy, StrategyETFAllocation
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategy", tags=["策略"])


class StrategyResponse(BaseModel):
    """策略响应模型"""
    id: int
    name: str
    description: Optional[str]
    investment_philosophy: Optional[str]
    target_return: Optional[float]
    max_drawdown: Optional[float]
    risk_level: Optional[str]
    investment_amount: Optional[float]
    status: str
    created_at: str
    updated_at: str
    etf_allocations: List[dict]
    
    class Config:
        from_attributes = True


class StrategySaveRequest(BaseModel):
    """策略保存请求模型"""
    strategy_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    investment_philosophy: Optional[str] = None
    target_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    risk_level: Optional[str] = None
    investment_amount: Optional[float] = None
    etf_allocations: List[dict]
    asset_allocation: Optional[dict] = None
    constraints: Optional[dict] = None
    preferences: Optional[dict] = None


@router.get("/{strategy_id}", response_model=StrategyResponse, summary="获取策略详情")
async def get_strategy_detail(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略详情"""
    try:
        strategy = db.query(Strategy).filter(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 获取ETF配置
        etf_allocations = db.query(StrategyETFAllocation).filter(
            StrategyETFAllocation.strategy_id == strategy_id
        ).all()
        
        etf_list = []
        for allocation in etf_allocations:
            etf_list.append({
                "etf_code": allocation.etf_code,
                "etf_name": allocation.etf_name,
                "allocation_percentage": allocation.allocation_percentage,
                "asset_class": allocation.asset_class,
                "sector": allocation.sector
            })
        
        strategy_data = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "investment_philosophy": strategy.investment_philosophy,
            "target_return": strategy.target_return,
            "max_drawdown": strategy.max_drawdown,
            "risk_level": strategy.risk_level,
            "investment_amount": strategy.investment_amount,
            "status": strategy.status,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat(),
            "etf_allocations": etf_list
        }
        
        return strategy_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取策略详情失败")


@router.post("/save", summary="保存策略")
async def save_strategy(
    strategy_data: StrategySaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存策略"""
    try:
        if strategy_data.strategy_id:
            # 更新现有策略
            strategy = db.query(Strategy).filter(
                Strategy.id == strategy_data.strategy_id,
                Strategy.user_id == current_user.id
            ).first()
            
            if not strategy:
                raise HTTPException(status_code=404, detail="策略不存在")
        else:
            # 创建新策略
            strategy = Strategy(user_id=current_user.id)
            db.add(strategy)
        
        # 更新策略信息
        strategy.name = strategy_data.name
        strategy.description = strategy_data.description
        strategy.investment_philosophy = strategy_data.investment_philosophy
        strategy.target_return = strategy_data.target_return
        strategy.max_drawdown = strategy_data.max_drawdown
        strategy.risk_level = strategy_data.risk_level
        strategy.investment_amount = strategy_data.investment_amount
        strategy.asset_allocation = strategy_data.asset_allocation
        strategy.constraints = strategy_data.constraints
        strategy.preferences = strategy_data.preferences
        strategy.status = "active"
        
        db.commit()
        db.refresh(strategy)
        
        # 删除现有的ETF配置
        if strategy_data.strategy_id:
            db.query(StrategyETFAllocation).filter(
                StrategyETFAllocation.strategy_id == strategy.id
            ).delete()
        
        # 添加新的ETF配置
        for allocation_data in strategy_data.etf_allocations:
            allocation = StrategyETFAllocation(
                strategy_id=strategy.id,
                etf_code=allocation_data["etf_code"],
                etf_name=allocation_data["etf_name"],
                allocation_percentage=allocation_data["weight"],
                asset_class=allocation_data.get("asset_class"),
                sector=allocation_data.get("sector")
            )
            db.add(allocation)
        
        db.commit()
        
        # 更新用户类型（标记为老用户）
        if current_user.is_new_user:
            current_user.is_new_user = False
            db.commit()
        
        return {
            "success": True,
            "strategy_id": strategy.id,
            "message": "策略保存成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存策略失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="保存策略失败")


@router.get("/history", summary="获取策略历史")
async def get_strategy_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的策略历史"""
    try:
        strategies = db.query(Strategy).filter(
            Strategy.user_id == current_user.id,
            Strategy.status == "active"
        ).order_by(Strategy.updated_at.desc()).all()
        
        strategy_list = []
        for strategy in strategies:
            # 计算简单的绩效指标（实际应用中需要真实的回测数据）
            performance = {
                "annual_return": strategy.target_return or 0,
                "max_drawdown": strategy.max_drawdown or 0
            }
            
            strategy_info = {
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "risk_level": strategy.risk_level,
                "target_return": strategy.target_return,
                "investment_amount": strategy.investment_amount,
                "created_at": strategy.created_at.isoformat(),
                "updated_at": strategy.updated_at.isoformat(),
                "performance": performance
            }
            strategy_list.append(strategy_info)
        
        return {"strategies": strategy_list}
        
    except Exception as e:
        logger.error(f"获取策略历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取策略历史失败")


@router.delete("/{strategy_id}", summary="删除策略")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除策略"""
    try:
        strategy = db.query(Strategy).filter(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 软删除
        strategy.status = "deleted"
        db.commit()
        
        return {"success": True, "message": "策略删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {e}")
        raise HTTPException(status_code=500, detail="删除策略失败")


@router.get("/{strategy_id}/backtest", summary="获取策略回测结果")
async def get_strategy_backtest(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取策略回测结果"""
    try:
        strategy = db.query(Strategy).filter(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 获取回测数据（实际应用中从回测数据表获取）
        # 这里返回模拟数据
        backtest_result = {
            "strategy_id": strategy_id,
            "backtest_period": "2023-01-01 to 2024-01-01",
            "performance_metrics": {
                "total_return": 12.5,
                "annual_return": 12.5,
                "volatility": 15.2,
                "max_drawdown": 8.3,
                "sharpe_ratio": 0.82,
                "win_rate": 65.4
            },
            "daily_data": [
                # 模拟的日度数据
                {
                    "date": "2023-01-01",
                    "portfolio_value": 100000,
                    "daily_return": 0.0,
                    "cumulative_return": 0.0
                }
                # 实际应用中需要完整的历史数据
            ]
        }
        
        return backtest_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略回测失败: {e}")
        raise HTTPException(status_code=500, detail="获取策略回测失败")
