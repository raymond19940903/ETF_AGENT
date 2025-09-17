"""策略优化工具"""
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class StrategyOptimizationInput(BaseModel):
    """策略优化工具输入"""
    current_strategy: Dict[str, Any] = Field(description="当前策略")
    user_feedback: Dict[str, Any] = Field(description="用户反馈")
    optimization_target: str = Field("user_satisfaction", description="优化目标")


class StrategyOptimizationTool(BaseTool):
    """策略优化工具"""
    name = "strategy_optimization_tool"
    description = "根据用户对话反馈优化策略配置"
    args_schema = StrategyOptimizationInput
    
    def _run(self, current_strategy: Dict[str, Any],
             user_feedback: Dict[str, Any],
             optimization_target: str = "user_satisfaction") -> Dict[str, Any]:
        """执行策略优化"""
        try:
            # 分析用户反馈
            feedback_analysis = self._analyze_user_feedback(user_feedback)
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                current_strategy, feedback_analysis
            )
            
            # 应用优化
            optimized_strategy = self._apply_optimizations(
                current_strategy, optimization_suggestions
            )
            
            result = {
                "success": True,
                "optimized_strategy": optimized_strategy,
                "optimization_suggestions": optimization_suggestions,
                "feedback_analysis": feedback_analysis,
                "changes_made": self._summarize_changes(current_strategy, optimized_strategy)
            }
            
            logger.info("策略优化完成")
            return result
            
        except Exception as e:
            logger.error(f"策略优化失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "optimized_strategy": current_strategy,
                "optimization_suggestions": [],
                "changes_made": []
            }
    
    async def _arun(self, current_strategy: Dict[str, Any],
                   user_feedback: Dict[str, Any],
                   optimization_target: str = "user_satisfaction") -> Dict[str, Any]:
        """异步执行策略优化"""
        return self._run(current_strategy, user_feedback, optimization_target)
    
    def _analyze_user_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户反馈"""
        analysis = {
            "feedback_type": "general",
            "specific_concerns": [],
            "requested_changes": [],
            "sentiment": "neutral"
        }
        
        feedback_text = feedback.get("content", "")
        
        # 识别反馈类型
        if "风险" in feedback_text and ("太高" in feedback_text or "降低" in feedback_text):
            analysis["feedback_type"] = "risk_reduction"
            analysis["specific_concerns"].append("风险过高")
            analysis["requested_changes"].append("降低投资组合风险")
        
        if "收益" in feedback_text and ("太低" in feedback_text or "提高" in feedback_text):
            analysis["feedback_type"] = "return_enhancement"
            analysis["specific_concerns"].append("收益不足")
            analysis["requested_changes"].append("提高预期收益")
        
        if "比例" in feedback_text:
            analysis["feedback_type"] = "allocation_adjustment"
            analysis["specific_concerns"].append("资产配置比例")
            analysis["requested_changes"].append("调整配置比例")
        
        return analysis
    
    def _generate_optimization_suggestions(self, strategy: Dict[str, Any],
                                         analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        
        feedback_type = analysis.get("feedback_type", "general")
        
        if feedback_type == "risk_reduction":
            suggestions.append({
                "type": "risk_reduction",
                "description": "增加债券类ETF配置，降低股票类ETF比例",
                "priority": "high",
                "expected_impact": "降低组合波动率和最大回撤"
            })
        
        elif feedback_type == "return_enhancement":
            suggestions.append({
                "type": "return_enhancement", 
                "description": "增加成长型ETF配置，提高股票类资产比例",
                "priority": "high",
                "expected_impact": "提高预期收益率"
            })
        
        elif feedback_type == "allocation_adjustment":
            suggestions.append({
                "type": "rebalancing",
                "description": "根据用户偏好调整各类资产配置比例",
                "priority": "medium",
                "expected_impact": "更符合用户投资偏好"
            })
        
        return suggestions
    
    def _apply_optimizations(self, strategy: Dict[str, Any],
                           suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """应用优化建议"""
        optimized_strategy = strategy.copy()
        
        for suggestion in suggestions:
            if suggestion["type"] == "risk_reduction":
                # 降低风险：增加债券配置
                optimized_strategy = self._adjust_risk_level(optimized_strategy, "conservative")
            
            elif suggestion["type"] == "return_enhancement":
                # 提高收益：增加股票配置
                optimized_strategy = self._adjust_risk_level(optimized_strategy, "aggressive")
            
            elif suggestion["type"] == "rebalancing":
                # 重新平衡配置
                optimized_strategy = self._rebalance_allocations(optimized_strategy)
        
        return optimized_strategy
    
    def _adjust_risk_level(self, strategy: Dict[str, Any], direction: str) -> Dict[str, Any]:
        """调整风险水平"""
        if "etf_allocations" not in strategy:
            return strategy
        
        allocations = strategy["etf_allocations"].copy()
        
        for allocation in allocations:
            asset_class = allocation.get("asset_class", "").lower()
            current_weight = allocation.get("weight", 0)
            
            if direction == "conservative":
                # 降低风险：减少股票，增加债券
                if "股票" in asset_class or "equity" in asset_class:
                    allocation["weight"] = max(current_weight * 0.8, 5)  # 减少20%，最低5%
                elif "债券" in asset_class or "bond" in asset_class:
                    allocation["weight"] = min(current_weight * 1.3, 50)  # 增加30%，最高50%
            
            elif direction == "aggressive":
                # 提高收益：增加股票，减少债券
                if "股票" in asset_class or "equity" in asset_class:
                    allocation["weight"] = min(current_weight * 1.2, 70)  # 增加20%，最高70%
                elif "债券" in asset_class or "bond" in asset_class:
                    allocation["weight"] = max(current_weight * 0.7, 10)  # 减少30%，最低10%
        
        # 重新归一化权重
        total_weight = sum(alloc["weight"] for alloc in allocations)
        if total_weight > 0:
            for allocation in allocations:
                allocation["weight"] = round(allocation["weight"] / total_weight * 100, 2)
        
        strategy["etf_allocations"] = allocations
        return strategy
    
    def _rebalance_allocations(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """重新平衡配置"""
        # 简单的重新平衡：确保权重和为100%
        if "etf_allocations" not in strategy:
            return strategy
        
        allocations = strategy["etf_allocations"]
        total_weight = sum(alloc.get("weight", 0) for alloc in allocations)
        
        if total_weight > 0:
            for allocation in allocations:
                allocation["weight"] = round(allocation["weight"] / total_weight * 100, 2)
        
        return strategy
    
    def _summarize_changes(self, original: Dict[str, Any], 
                          optimized: Dict[str, Any]) -> List[str]:
        """总结变更内容"""
        changes = []
        
        # 比较ETF配置变化
        orig_allocations = original.get("etf_allocations", [])
        opt_allocations = optimized.get("etf_allocations", [])
        
        for i, (orig, opt) in enumerate(zip(orig_allocations, opt_allocations)):
            orig_weight = orig.get("weight", 0)
            opt_weight = opt.get("weight", 0)
            
            if abs(orig_weight - opt_weight) > 1:  # 变化超过1%
                etf_name = orig.get("etf_name", f"ETF{i+1}")
                if opt_weight > orig_weight:
                    changes.append(f"{etf_name}配置比例从{orig_weight}%增加到{opt_weight}%")
                else:
                    changes.append(f"{etf_name}配置比例从{orig_weight}%减少到{opt_weight}%")
        
        if not changes:
            changes.append("策略配置未发生显著变化")
        
        return changes
