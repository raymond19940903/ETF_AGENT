"""智能体核心模块"""
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
from langchain.llms.base import LLM
from langchain.schema import AgentAction, AgentFinish
from app.tools import *
from app.agent.business_flow import BusinessFlowManager
from app.cache.service import CacheService
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class AgentCore:
    """智能体核心类"""
    
    def __init__(self, db: Session, llm: LLM):
        self.db = db
        self.llm = llm
        self.cache_service = CacheService()
        self.business_flow = BusinessFlowManager()
        
        # 初始化工具
        self.tools = {
            "user_identification_tool": UserIdentificationTool(db),
            "element_extraction_tool": ElementExtractionTool(llm),
            "etf_data_fetch_tool": ETFDataFetchTool(db),
            "strategy_generation_tool": StrategyGenerationTool(db),
            "strategy_backtest_tool": StrategyBacktestTool(),
            "market_news_fetch_tool": MarketNewsFetchTool(),
            "strategy_optimization_tool": StrategyOptimizationTool()
        }
        
        self.status_callback: Optional[Callable] = None
    
    def set_status_callback(self, callback: Callable):
        """设置状态更新回调函数"""
        self.status_callback = callback
    
    async def process_conversation(self, user_id: int, session_id: str, 
                                 message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理对话消息"""
        try:
            if context is None:
                context = {}
            
            await self._update_status("思考中", "正在分析用户需求和规划任务")
            
            # 1. 获取对话上下文
            conversation_context = await self._get_conversation_context(session_id)
            conversation_context.update(context)
            
            # 2. 识别用户身份和状态
            user_info = await self._identify_user(user_id)
            
            # 3. 判断业务流程阶段
            current_stage = self.business_flow.determine_stage(
                user_info, conversation_context, message
            )
            
            await self._update_status("数据获取中", f"当前处于{current_stage}阶段")
            
            # 4. 生成任务规划
            task_plan = self._generate_task_plan(current_stage, message, conversation_context)
            
            # 5. 执行任务规划
            execution_result = await self._execute_task_plan(task_plan, {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "context": conversation_context,
                "user_info": user_info
            })
            
            await self._update_status("结果汇总中", "正在汇总结果生成回复")
            
            # 6. 生成最终回复
            final_response = await self._generate_final_response(
                execution_result, current_stage, message
            )
            
            # 7. 更新对话上下文
            await self._update_conversation_context(session_id, {
                "last_message": message,
                "last_stage": current_stage,
                "last_response": final_response,
                "execution_result": execution_result
            })
            
            await self._update_status("完成", "对话处理完成")
            
            return {
                "success": True,
                "response": final_response,
                "stage": current_stage,
                "task_plan": task_plan,
                "execution_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            await self._update_status("错误", f"处理失败: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，处理您的请求时遇到了问题，请稍后再试。"
            }
    
    async def _identify_user(self, user_id: int) -> Dict[str, Any]:
        """识别用户身份"""
        try:
            tool = self.tools["user_identification_tool"]
            result = await tool._arun(user_id=user_id, include_strategies=True)
            return result
        except Exception as e:
            logger.error(f"用户身份识别失败: {e}")
            return {"success": False, "user_type": "unknown"}
    
    def _generate_task_plan(self, stage: str, message: str, 
                           context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成任务规划"""
        task_plan = []
        
        if stage == "new_user_introduction":
            task_plan = [
                {
                    "tool": "market_news_fetch_tool",
                    "params": {"category": "etf", "limit": 5},
                    "description": "获取ETF市场资讯"
                }
            ]
            
        elif stage == "element_collection":
            task_plan = [
                {
                    "tool": "element_extraction_tool",
                    "params": {
                        "conversation_content": message,
                        "context_info": context,
                        "previous_elements": context.get("extracted_elements", {})
                    },
                    "description": "提取投资要素"
                }
            ]
            
        elif stage == "strategy_generation":
            task_plan = [
                {
                    "tool": "element_extraction_tool",
                    "params": {
                        "conversation_content": message,
                        "context_info": context,
                        "previous_elements": context.get("extracted_elements", {})
                    },
                    "description": "更新投资要素"
                },
                {
                    "tool": "etf_data_fetch_tool",
                    "params": {
                        "asset_class": None,
                        "limit": 20
                    },
                    "description": "获取ETF数据"
                },
                {
                    "tool": "strategy_generation_tool",
                    "params": {
                        "investment_elements": {},  # 将从上一步结果中填充
                        "constraints": {},
                        "optimization_target": "sharpe_ratio"
                    },
                    "description": "生成投资策略"
                },
                {
                    "tool": "strategy_backtest_tool",
                    "params": {
                        "strategy_config": {},  # 将从上一步结果中填充
                        "backtest_period": 365
                    },
                    "description": "执行策略回测"
                }
            ]
            
        elif stage == "strategy_optimization":
            task_plan = [
                {
                    "tool": "element_extraction_tool",
                    "params": {
                        "conversation_content": message,
                        "context_info": context
                    },
                    "description": "分析用户反馈"
                },
                {
                    "tool": "strategy_optimization_tool",
                    "params": {
                        "current_strategy": context.get("current_strategy", {}),
                        "user_feedback": {"content": message},
                        "optimization_target": "user_satisfaction"
                    },
                    "description": "优化策略"
                }
            ]
            
        elif stage == "market_recommendation":
            task_plan = [
                {
                    "tool": "market_news_fetch_tool",
                    "params": {
                        "keywords": ["ETF", "投资机会"],
                        "limit": 10
                    },
                    "description": "获取市场推荐资讯"
                }
            ]
        
        return task_plan
    
    async def _execute_task_plan(self, task_plan: List[Dict[str, Any]], 
                               execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务规划"""
        results = {}
        
        for i, task in enumerate(task_plan):
            try:
                tool_name = task["tool"]
                tool_params = task["params"]
                description = task["description"]
                
                await self._update_status("执行中", f"正在{description}")
                
                # 获取工具
                tool = self.tools.get(tool_name)
                if not tool:
                    logger.warning(f"工具不存在: {tool_name}")
                    continue
                
                # 处理参数依赖
                tool_params = self._resolve_parameter_dependencies(tool_params, results)
                
                # 执行工具
                result = await tool._arun(**tool_params)
                results[f"task_{i}_{tool_name}"] = result
                
                # 处理特殊结果
                if tool_name == "element_extraction_tool" and result.get("success"):
                    execution_context["extracted_elements"] = result["extracted_elements"]
                
                logger.info(f"任务完成: {description}")
                
            except Exception as e:
                logger.error(f"任务执行失败 {task['description']}: {e}")
                results[f"task_{i}_error"] = str(e)
        
        return results
    
    def _resolve_parameter_dependencies(self, params: Dict[str, Any], 
                                      results: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数依赖"""
        resolved_params = params.copy()
        
        # 处理策略生成工具的参数依赖
        if "investment_elements" in resolved_params and not resolved_params["investment_elements"]:
            # 从要素提取结果中获取
            for key, result in results.items():
                if "element_extraction_tool" in key and result.get("success"):
                    resolved_params["investment_elements"] = result["extracted_elements"]
                    break
        
        # 处理回测工具的参数依赖
        if "strategy_config" in resolved_params and not resolved_params["strategy_config"]:
            # 从策略生成结果中获取
            for key, result in results.items():
                if "strategy_generation_tool" in key and result.get("success"):
                    resolved_params["strategy_config"] = result["strategy"]
                    break
        
        return resolved_params
    
    async def _generate_final_response(self, execution_result: Dict[str, Any],
                                     stage: str, user_message: str) -> str:
        """生成最终回复"""
        try:
            # 构建回复生成提示词
            prompt = self._build_response_prompt(execution_result, stage, user_message)
            
            # 调用LLM生成回复
            response = self.llm(prompt)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"生成最终回复失败: {e}")
            return self._generate_fallback_response(stage)
    
    def _build_response_prompt(self, execution_result: Dict[str, Any],
                             stage: str, user_message: str) -> str:
        """构建回复生成提示词"""
        prompt = f"""
你是一个专业的ETF投资顾问助手，正在与用户进行投资策略咨询。

当前阶段：{stage}
用户消息：{user_message}

执行结果：
{json.dumps(execution_result, ensure_ascii=False, indent=2)}

请根据执行结果生成一个专业、友好、有用的回复。回复应该：
1. 直接回应用户的问题或需求
2. 基于执行结果提供具体的信息或建议
3. 引导用户进行下一步操作
4. 保持专业但易懂的语调

请生成回复：
"""
        return prompt
    
    def _generate_fallback_response(self, stage: str) -> str:
        """生成备用回复"""
        fallback_responses = {
            "new_user_introduction": "欢迎使用ETF资产配置策略系统！我可以帮助您制定个性化的ETF投资策略。请告诉我您的投资偏好和目标。",
            "element_collection": "我正在了解您的投资需求。请继续告诉我您的风险偏好、目标收益率等信息。",
            "strategy_generation": "我正在为您生成投资策略，请稍等片刻。",
            "strategy_optimization": "我会根据您的反馈来优化策略配置。",
            "market_recommendation": "让我为您推荐一些当前市场上的投资机会。"
        }
        
        return fallback_responses.get(stage, "感谢您的咨询，我会尽力为您提供专业的投资建议。")
    
    async def _get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """获取对话上下文"""
        try:
            context = await self.cache_service.get_conversation_context(session_id)
            return context or {}
        except Exception as e:
            logger.error(f"获取对话上下文失败: {e}")
            return {}
    
    async def _update_conversation_context(self, session_id: str, 
                                         context_update: Dict[str, Any]):
        """更新对话上下文"""
        try:
            await self.cache_service.update_conversation_context(session_id, context_update)
        except Exception as e:
            logger.error(f"更新对话上下文失败: {e}")
    
    async def _update_status(self, status: str, message: str):
        """更新处理状态"""
        try:
            if self.status_callback:
                await self.status_callback({
                    "status": status,
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                })
        except Exception as e:
            logger.error(f"状态更新失败: {e}")
