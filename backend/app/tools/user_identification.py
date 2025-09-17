"""用户身份识别工具"""
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.strategy import Strategy
import logging

logger = logging.getLogger(__name__)


class UserIdentificationInput(BaseModel):
    """用户身份识别工具输入"""
    user_id: int = Field(description="用户ID")
    include_strategies: bool = Field(default=True, description="是否包含策略信息")


class UserIdentificationTool(BaseTool):
    """用户身份识别工具"""
    name = "user_identification_tool"
    description = "识别用户身份类型和历史信息获取"
    args_schema = UserIdentificationInput
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    def _run(self, user_id: int, include_strategies: bool = True) -> Dict[str, Any]:
        """执行用户身份识别"""
        try:
            # 查询用户信息
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "error": "用户不存在",
                    "user_type": "unknown"
                }
            
            # 获取用户策略数量
            strategy_count = self.db.query(Strategy).filter(
                Strategy.user_id == user_id,
                Strategy.status == "active"
            ).count()
            
            # 判断用户类型
            is_new_user = strategy_count == 0
            user_type = "new_user" if is_new_user else "old_user"
            
            result = {
                "success": True,
                "user_id": user_id,
                "user_type": user_type,
                "is_new_user": is_new_user,
                "phone_number": user.phone_number,
                "nickname": user.nickname,
                "strategy_count": strategy_count,
                "is_active": user.is_active
            }
            
            # 如果是老用户且需要策略信息，获取历史策略
            if not is_new_user and include_strategies:
                strategies = self.db.query(Strategy).filter(
                    Strategy.user_id == user_id,
                    Strategy.status == "active"
                ).order_by(Strategy.updated_at.desc()).limit(5).all()
                
                strategy_list = []
                for strategy in strategies:
                    strategy_info = {
                        "id": strategy.id,
                        "name": strategy.name,
                        "description": strategy.description,
                        "target_return": strategy.target_return,
                        "max_drawdown": strategy.max_drawdown,
                        "risk_level": strategy.risk_level,
                        "created_at": strategy.created_at.isoformat(),
                        "updated_at": strategy.updated_at.isoformat()
                    }
                    strategy_list.append(strategy_info)
                
                result["recent_strategies"] = strategy_list
                
                # 找出表现最好的策略
                if strategy_list:
                    best_strategy = max(strategy_list, 
                                      key=lambda s: s.get("target_return", 0) or 0)
                    result["best_strategy"] = best_strategy
            
            # 更新用户类型标记
            if user.is_new_user != is_new_user:
                user.is_new_user = is_new_user
                self.db.commit()
            
            logger.info(f"用户身份识别成功: {user_id} -> {user_type}")
            return result
            
        except Exception as e:
            logger.error(f"用户身份识别失败 {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_type": "unknown"
            }
    
    async def _arun(self, user_id: int, include_strategies: bool = True) -> Dict[str, Any]:
        """异步执行用户身份识别"""
        return self._run(user_id, include_strategies)
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        try:
            # 从历史策略中分析用户偏好
            strategies = self.db.query(Strategy).filter(
                Strategy.user_id == user_id,
                Strategy.status == "active"
            ).all()
            
            if not strategies:
                return {"preferences": {}, "preference_confidence": 0.0}
            
            # 分析偏好模式
            risk_levels = [s.risk_level for s in strategies if s.risk_level]
            asset_classes = []
            sectors = []
            
            for strategy in strategies:
                if strategy.preferences:
                    prefs = strategy.preferences
                    if isinstance(prefs, dict):
                        asset_classes.extend(prefs.get("preferred_asset_classes", []))
                        sectors.extend(prefs.get("preferred_sectors", []))
            
            # 统计最常见的偏好
            from collections import Counter
            
            risk_counter = Counter(risk_levels)
            asset_counter = Counter(asset_classes)
            sector_counter = Counter(sectors)
            
            preferences = {
                "preferred_risk_level": risk_counter.most_common(1)[0][0] if risk_counter else None,
                "preferred_asset_classes": [item[0] for item in asset_counter.most_common(3)],
                "preferred_sectors": [item[0] for item in sector_counter.most_common(3)],
                "average_target_return": sum(s.target_return for s in strategies if s.target_return) / len(strategies) if strategies else None,
                "average_max_drawdown": sum(s.max_drawdown for s in strategies if s.max_drawdown) / len(strategies) if strategies else None
            }
            
            # 计算偏好置信度
            confidence = min(len(strategies) / 5.0, 1.0)  # 最多5个策略达到满分
            
            return {
                "preferences": preferences,
                "preference_confidence": confidence,
                "strategy_count": len(strategies)
            }
            
        except Exception as e:
            logger.error(f"获取用户偏好失败 {user_id}: {e}")
            return {"preferences": {}, "preference_confidence": 0.0}
