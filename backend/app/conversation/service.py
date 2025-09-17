"""对话服务"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.user import User
from app.cache.service import CacheService
from app.agent.agent_core import AgentCore
from app.utils.helpers import generate_session_id
from langchain.llms.base import LLM
# 移除uuid依赖，使用helpers中的ID生成函数
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationService:
    """对话服务类"""
    
    def __init__(self, db: Session, llm: LLM):
        self.db = db
        self.llm = llm
        self.cache_service = CacheService()
        self.agent_core = AgentCore(db, llm)
    
    async def create_session(self, user_id: int) -> Dict[str, Any]:
        """创建对话会话"""
        try:
            # 生成会话ID
            session_id = generate_session_id()
            
            # 获取用户信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("用户不存在")
            
            # 判断用户类型
            is_new_user = len(user.strategies) == 0
            
            # 生成欢迎消息
            welcome_message = self._generate_welcome_message(user, is_new_user)
            
            # 初始化会话上下文
            session_context = {
                "session_id": session_id,
                "user_id": user_id,
                "is_new_user": is_new_user,
                "created_at": datetime.now().isoformat(),
                "message_count": 0,
                "current_stage": "new_user_introduction" if is_new_user else "old_user_welcome",
                "extracted_elements": {},
                "conversation_history": []
            }
            
            # 缓存会话上下文
            await self.cache_service.set_conversation_context(session_id, session_context)
            
            # 保存欢迎消息到数据库
            welcome_conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                message_type="system",
                content=welcome_message,
                round_number=1,
                context_data={"session_start": True}
            )
            self.db.add(welcome_conversation)
            self.db.commit()
            
            return {
                "session_id": session_id,
                "welcome_message": welcome_message,
                "is_new_user": is_new_user,
                "user_type": "new_user" if is_new_user else "old_user"
            }
            
        except Exception as e:
            logger.error(f"创建对话会话失败: {e}")
            raise
    
    async def process_message(self, user_id: int, session_id: str, 
                            message: str) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            # 获取会话上下文
            context = await self.cache_service.get_conversation_context(session_id)
            if not context:
                raise ValueError("会话不存在或已过期")
            
            # 更新消息计数
            context["message_count"] += 1
            round_number = context["message_count"]
            
            # 保存用户消息到数据库
            user_conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                message_type="user",
                content=message,
                round_number=round_number,
                context_data={"stage": context.get("current_stage")}
            )
            self.db.add(user_conversation)
            self.db.commit()
            
            # 使用智能体处理消息
            result = await self.agent_core.process_conversation(
                user_id, session_id, message, context
            )
            
            if result["success"]:
                response_message = result["response"]
                
                # 保存助手回复到数据库
                assistant_conversation = Conversation(
                    user_id=user_id,
                    session_id=session_id,
                    message_type="assistant",
                    content=response_message,
                    round_number=round_number,
                    context_data=result.get("execution_result"),
                    extracted_elements=result.get("execution_result", {}).get("extracted_elements")
                )
                self.db.add(assistant_conversation)
                self.db.commit()
                
                # 更新会话上下文
                context.update({
                    "last_message": message,
                    "last_response": response_message,
                    "current_stage": result.get("stage"),
                    "last_execution_result": result.get("execution_result")
                })
                await self.cache_service.set_conversation_context(session_id, context)
                
                return {
                    "success": True,
                    "response": response_message,
                    "stage": result.get("stage"),
                    "session_id": session_id,
                    "round_number": round_number,
                    "strategy_updated": "strategy" in result.get("execution_result", {}),
                    "execution_result": result.get("execution_result")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "response": "抱歉，处理您的消息时遇到了问题，请稍后再试。"
                }
                
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "系统暂时无法处理您的请求，请稍后再试。"
            }
    
    async def get_conversation_history(self, user_id: int, session_id: str, 
                                     limit: int = 50) -> List[Dict[str, Any]]:
        """获取对话历史"""
        try:
            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            
            history = []
            for conv in reversed(conversations):  # 按时间正序
                history.append({
                    "id": conv.id,
                    "message_type": conv.message_type,
                    "content": conv.content,
                    "round_number": conv.round_number,
                    "created_at": conv.created_at.isoformat(),
                    "context_data": conv.context_data,
                    "extracted_elements": conv.extracted_elements
                })
            
            return history
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户对话会话列表"""
        try:
            # 获取用户的所有会话ID
            sessions_query = self.db.query(Conversation.session_id).filter(
                Conversation.user_id == user_id
            ).distinct().all()
            
            session_list = []
            for session_tuple in sessions_query:
                session_id = session_tuple[0]
                
                # 获取会话的最后一条消息和第一条消息
                last_message = self.db.query(Conversation).filter(
                    Conversation.session_id == session_id,
                    Conversation.user_id == user_id
                ).order_by(Conversation.created_at.desc()).first()
                
                first_message = self.db.query(Conversation).filter(
                    Conversation.session_id == session_id,
                    Conversation.user_id == user_id
                ).order_by(Conversation.created_at.asc()).first()
                
                message_count = self.db.query(Conversation).filter(
                    Conversation.session_id == session_id,
                    Conversation.user_id == user_id
                ).count()
                
                if last_message and first_message:
                    session_info = {
                        "session_id": session_id,
                        "last_message": last_message.content[:50] + "..." if len(last_message.content) > 50 else last_message.content,
                        "last_message_time": last_message.created_at.isoformat(),
                        "created_time": first_message.created_at.isoformat(),
                        "message_count": message_count,
                        "current_stage": last_message.context_data.get("stage") if last_message.context_data else None
                    }
                    session_list.append(session_info)
            
            # 按最后消息时间排序
            session_list.sort(key=lambda x: x["last_message_time"], reverse=True)
            
            return session_list
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return []
    
    async def delete_session(self, user_id: int, session_id: str) -> bool:
        """删除对话会话"""
        try:
            # 删除数据库中的对话记录
            deleted_count = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id
            ).delete()
            
            self.db.commit()
            
            # 删除缓存中的会话上下文
            await self.cache_service.delete_conversation_context(session_id)
            
            logger.info(f"删除会话成功: {session_id}, 删除消息数: {deleted_count}")
            return True
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            self.db.rollback()
            return False
    
    def _generate_welcome_message(self, user: User, is_new_user: bool) -> str:
        """生成欢迎消息"""
        if is_new_user:
            return (
                f"欢迎使用ETF资产配置策略系统！我是您的专属投资顾问助手。\n\n"
                f"ETF资产配置策略可以帮助您：\n"
                f"• 通过分散投资降低风险\n"
                f"• 获得稳健的长期收益\n"
                f"• 实现动态再平衡\n\n"
                f"让我们开始了解您的投资需求吧！请告诉我您的风险偏好和投资目标。"
            )
        else:
            # 获取用户最好的策略
            best_strategy = None
            if user.strategies:
                best_strategy = max(user.strategies, key=lambda s: s.target_return or 0)
            
            strategy_info = ""
            if best_strategy:
                strategy_info = f"您的'{best_strategy.name}'策略表现不错，"
            
            return (
                f"欢迎回来！{strategy_info}让我为您提供最新的投资建议。\n\n"
                f"我可以帮您：\n"
                f"• 查看和优化现有策略\n"
                f"• 获取最新市场资讯\n"
                f"• 制定新的投资策略\n\n"
                f"请告诉我您想要做什么？"
            )
    
    async def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话上下文"""
        return await self.cache_service.get_conversation_context(session_id)
    
    async def update_session_context(self, session_id: str, 
                                   context_update: Dict[str, Any]) -> bool:
        """更新会话上下文"""
        try:
            await self.cache_service.update_conversation_context(session_id, context_update)
            return True
        except Exception as e:
            logger.error(f"更新会话上下文失败: {e}")
            return False
