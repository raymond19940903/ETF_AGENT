"""对话API路由"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.conversation.service import ConversationService
from app.conversation.websocket_manager import websocket_manager
from app.agent.agent_core import AgentCore
from langchain.llms.base import LLM
from app.utils.helpers import generate_session_id
import json
# 移除uuid依赖，使用helpers中的ID生成函数
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversation", tags=["对话"])

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送消息失败: {e}")

manager = ConnectionManager()

# 模拟LLM（实际使用时需要配置真实的LLM）
class MockLLM(LLM):
    def _call(self, prompt: str, stop=None, run_manager=None):
        return "这是一个模拟的LLM响应，实际部署时需要配置真实的大语言模型。"
    
    @property
    def _llm_type(self):
        return "mock"


@router.post("/start", summary="开始对话")
async def start_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """开始新的对话会话"""
    try:
        # 生成会话ID
        session_id = generate_session_id()
        
        # 判断用户类型
        is_new_user = len(current_user.strategies) == 0
        
        # 生成欢迎消息
        if is_new_user:
            welcome_message = (
                "欢迎使用ETF资产配置策略系统！我是您的专属投资顾问助手。\n\n"
                "ETF资产配置策略可以帮助您：\n"
                "• 通过分散投资降低风险\n"
                "• 获得稳健的长期收益\n" 
                "• 实现动态再平衡\n\n"
                "让我们开始了解您的投资需求吧！请告诉我您的风险偏好和投资目标。"
            )
        else:
            # 获取用户最好的策略
            best_strategy = None
            if current_user.strategies:
                best_strategy = max(current_user.strategies, 
                                  key=lambda s: s.target_return or 0)
            
            strategy_info = ""
            if best_strategy:
                strategy_info = f"您的'{best_strategy.name}'策略表现不错，"
            
            welcome_message = (
                f"欢迎回来！{strategy_info}让我为您提供最新的投资建议。\n\n"
                "我可以帮您：\n"
                "• 查看和优化现有策略\n"
                "• 获取最新市场资讯\n"
                "• 制定新的投资策略\n\n"
                "请告诉我您想要做什么？"
            )
        
        return {
            "session_id": session_id,
            "welcome_message": welcome_message,
            "is_new_user": is_new_user
        }
        
    except Exception as e:
        logger.error(f"开始对话失败: {e}")
        raise HTTPException(status_code=500, detail="开始对话失败")


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket对话连接"""
    await manager.connect(websocket, session_id)
    
    # 初始化智能体（实际使用时需要配置真实的LLM）
    mock_llm = MockLLM()
    agent = AgentCore(db, mock_llm)
    
    # 设置状态更新回调
    async def status_callback(status_data):
        await manager.send_message(session_id, {
            "type": "status_update",
            "data": status_data
        })
    
    agent.set_status_callback(status_callback)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_id = message_data.get("user_id")
            message = message_data.get("message", "")
            
            if not user_id or not message:
                await manager.send_message(session_id, {
                    "type": "error",
                    "data": {"message": "缺少必要参数"}
                })
                continue
            
            # 保存用户消息到数据库
            user_conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                message_type="user",
                content=message,
                round_number=1  # 实际应用中需要计算轮次
            )
            db.add(user_conversation)
            db.commit()
            
            # 处理对话
            result = await agent.process_conversation(user_id, session_id, message)
            
            if result["success"]:
                response_message = result["response"]
                
                # 保存助手回复到数据库
                assistant_conversation = Conversation(
                    user_id=user_id,
                    session_id=session_id,
                    message_type="assistant",
                    content=response_message,
                    round_number=1,
                    context_data=result.get("execution_result")
                )
                db.add(assistant_conversation)
                db.commit()
                
                # 发送回复
                await manager.send_message(session_id, {
                    "type": "message",
                    "data": {
                        "message": response_message,
                        "stage": result.get("stage"),
                        "strategy_updated": "strategy" in result.get("execution_result", {})
                    }
                })
            else:
                await manager.send_message(session_id, {
                    "type": "error", 
                    "data": {"message": result.get("error", "处理失败")}
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket连接断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
        manager.disconnect(session_id)


@router.get("/history/{session_id}", summary="获取对话历史")
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.user_id == current_user.id
        ).order_by(Conversation.created_at).all()
        
        history = []
        for conv in conversations:
            history.append({
                "id": conv.id,
                "message_type": conv.message_type,
                "content": conv.content,
                "round_number": conv.round_number,
                "created_at": conv.created_at.isoformat(),
                "context_data": conv.context_data
            })
        
        return {"conversations": history}
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取对话历史失败")


@router.get("/sessions", summary="获取用户对话会话列表")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的对话会话列表"""
    try:
        # 获取用户的所有会话
        sessions = db.query(Conversation.session_id).filter(
            Conversation.user_id == current_user.id
        ).distinct().all()
        
        session_list = []
        for session in sessions:
            session_id = session[0]
            
            # 获取会话的最后一条消息
            last_message = db.query(Conversation).filter(
                Conversation.session_id == session_id,
                Conversation.user_id == current_user.id
            ).order_by(Conversation.created_at.desc()).first()
            
            if last_message:
                session_list.append({
                    "session_id": session_id,
                    "last_message": last_message.content[:50] + "..." if len(last_message.content) > 50 else last_message.content,
                    "last_message_time": last_message.created_at.isoformat(),
                    "message_count": db.query(Conversation).filter(
                        Conversation.session_id == session_id,
                        Conversation.user_id == current_user.id
                    ).count()
                })
        
        # 按最后消息时间排序
        session_list.sort(key=lambda x: x["last_message_time"], reverse=True)
        
        return {"sessions": session_list}
        
    except Exception as e:
        logger.error(f"获取用户会话失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户会话失败")
