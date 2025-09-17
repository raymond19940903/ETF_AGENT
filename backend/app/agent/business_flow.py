"""业务流程管理器"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BusinessFlowManager:
    """业务流程管理器"""
    
    def __init__(self):
        self.flow_stages = {
            "new_user_introduction": {
                "description": "新用户介绍阶段",
                "triggers": ["新用户", "首次使用", "介绍"],
                "next_stages": ["element_collection", "market_recommendation"]
            },
            "old_user_welcome": {
                "description": "老用户欢迎阶段", 
                "triggers": ["老用户", "历史策略", "欢迎回来"],
                "next_stages": ["strategy_review", "market_recommendation", "strategy_optimization"]
            },
            "element_collection": {
                "description": "投资要素收集阶段",
                "triggers": ["投资偏好", "风险", "收益", "资金", "期限"],
                "next_stages": ["strategy_generation", "element_collection"]
            },
            "strategy_generation": {
                "description": "策略生成阶段",
                "triggers": ["生成策略", "制定方案", "投资建议"],
                "next_stages": ["strategy_presentation", "strategy_optimization"]
            },
            "strategy_presentation": {
                "description": "策略展示阶段",
                "triggers": ["查看策略", "展示方案", "策略详情"],
                "next_stages": ["strategy_optimization", "strategy_save", "element_collection"]
            },
            "strategy_optimization": {
                "description": "策略优化阶段",
                "triggers": ["修改", "调整", "优化", "不满意", "改进"],
                "next_stages": ["strategy_presentation", "strategy_save", "element_collection"]
            },
            "strategy_review": {
                "description": "策略回顾阶段",
                "triggers": ["历史策略", "之前的", "回顾", "查看"],
                "next_stages": ["strategy_optimization", "market_recommendation", "strategy_generation"]
            },
            "market_recommendation": {
                "description": "市场推荐阶段",
                "triggers": ["推荐", "热点", "机会", "资讯", "新闻"],
                "next_stages": ["element_collection", "strategy_generation", "strategy_optimization"]
            },
            "strategy_save": {
                "description": "策略保存阶段",
                "triggers": ["保存", "确认", "采用", "使用这个策略"],
                "next_stages": ["conversation_end", "market_recommendation"]
            },
            "conversation_end": {
                "description": "对话结束阶段",
                "triggers": ["谢谢", "再见", "结束", "满意"],
                "next_stages": []
            }
        }
    
    def determine_stage(self, user_info: Dict[str, Any], 
                       context: Dict[str, Any], 
                       message: str) -> str:
        """判断当前业务流程阶段"""
        try:
            # 获取用户类型
            user_type = user_info.get("user_type", "unknown")
            is_new_user = user_info.get("is_new_user", True)
            
            # 获取上一阶段
            last_stage = context.get("last_stage")
            
            # 分析消息内容
            message_lower = message.lower()
            
            # 1. 首次对话判断
            if not last_stage:
                if is_new_user:
                    return "new_user_introduction"
                else:
                    return "old_user_welcome"
            
            # 2. 基于消息内容的阶段判断
            stage_scores = {}
            
            for stage, config in self.flow_stages.items():
                score = 0
                triggers = config.get("triggers", [])
                
                for trigger in triggers:
                    if trigger.lower() in message_lower:
                        score += 1
                
                if score > 0:
                    stage_scores[stage] = score
            
            # 3. 选择得分最高的阶段
            if stage_scores:
                best_stage = max(stage_scores, key=stage_scores.get)
                
                # 验证阶段转换的合理性
                if self._is_valid_transition(last_stage, best_stage):
                    return best_stage
            
            # 4. 基于上下文的默认流程
            return self._get_default_next_stage(last_stage, context, user_info)
            
        except Exception as e:
            logger.error(f"判断业务流程阶段失败: {e}")
            return "element_collection"  # 默认阶段
    
    def _is_valid_transition(self, from_stage: Optional[str], to_stage: str) -> bool:
        """验证阶段转换是否合理"""
        if not from_stage:
            return True
        
        stage_config = self.flow_stages.get(from_stage, {})
        next_stages = stage_config.get("next_stages", [])
        
        # 允许转换到指定的下一阶段，或者相同阶段（重复处理）
        return to_stage in next_stages or to_stage == from_stage
    
    def _get_default_next_stage(self, current_stage: Optional[str], 
                               context: Dict[str, Any],
                               user_info: Dict[str, Any]) -> str:
        """获取默认的下一阶段"""
        if not current_stage:
            return "new_user_introduction" if user_info.get("is_new_user", True) else "old_user_welcome"
        
        # 基于当前阶段的默认流程
        stage_defaults = {
            "new_user_introduction": "element_collection",
            "old_user_welcome": "strategy_review",
            "element_collection": self._should_generate_strategy(context),
            "strategy_generation": "strategy_presentation", 
            "strategy_presentation": "strategy_optimization",
            "strategy_optimization": "strategy_presentation",
            "strategy_review": "strategy_optimization",
            "market_recommendation": "element_collection",
            "strategy_save": "conversation_end"
        }
        
        return stage_defaults.get(current_stage, "element_collection")
    
    def _should_generate_strategy(self, context: Dict[str, Any]) -> str:
        """判断是否应该生成策略"""
        extracted_elements = context.get("extracted_elements", {})
        
        # 检查关键要素是否已收集
        required_elements = ["risk_tolerance", "target_return", "preferred_asset_classes"]
        collected_count = sum(1 for elem in required_elements if extracted_elements.get(elem))
        
        # 如果收集了足够的要素，进入策略生成阶段
        if collected_count >= 2:
            return "strategy_generation"
        else:
            return "element_collection"
    
    def get_stage_description(self, stage: str) -> str:
        """获取阶段描述"""
        stage_config = self.flow_stages.get(stage, {})
        return stage_config.get("description", "未知阶段")
    
    def get_next_stages(self, current_stage: str) -> list:
        """获取可能的下一阶段"""
        stage_config = self.flow_stages.get(current_stage, {})
        return stage_config.get("next_stages", [])
    
    def get_stage_progress(self, stage: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取阶段进度"""
        progress = {
            "current_stage": stage,
            "stage_description": self.get_stage_description(stage),
            "completion_percentage": 0,
            "next_suggested_actions": []
        }
        
        # 根据不同阶段计算进度
        if stage == "element_collection":
            extracted_elements = context.get("extracted_elements", {})
            required_elements = [
                "risk_tolerance", "target_return", "preferred_asset_classes", 
                "investment_amount", "max_drawdown_tolerance"
            ]
            
            collected_count = sum(1 for elem in required_elements if extracted_elements.get(elem))
            progress["completion_percentage"] = (collected_count / len(required_elements)) * 100
            
            missing_elements = [elem for elem in required_elements if not extracted_elements.get(elem)]
            if missing_elements:
                progress["next_suggested_actions"] = [f"请提供{elem}"for elem in missing_elements[:2]]
        
        elif stage == "strategy_generation":
            progress["completion_percentage"] = 50  # 策略生成中
            progress["next_suggested_actions"] = ["正在生成投资策略，请稍等"]
        
        elif stage == "strategy_presentation":
            progress["completion_percentage"] = 80
            progress["next_suggested_actions"] = ["查看策略详情", "提出修改意见", "保存策略"]
        
        elif stage == "strategy_optimization":
            progress["completion_percentage"] = 90
            progress["next_suggested_actions"] = ["确认优化结果", "继续调整", "保存策略"]
        
        return progress
