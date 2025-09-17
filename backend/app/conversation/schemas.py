"""对话相关数据模型"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationMessage(BaseModel):
    """对话消息模型"""
    user_id: int = Field(..., description="用户ID")
    message: str = Field(..., min_length=1, max_length=2000, description="消息内容")
    session_id: Optional[str] = Field(None, description="会话ID")


class ConversationResponse(BaseModel):
    """对话响应模型"""
    success: bool
    response: str
    session_id: str
    round_number: int
    stage: Optional[str] = None
    strategy_updated: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SessionStartRequest(BaseModel):
    """会话开始请求模型"""
    user_preference: Optional[Dict[str, Any]] = Field(None, description="用户偏好")


class SessionStartResponse(BaseModel):
    """会话开始响应模型"""
    session_id: str
    welcome_message: str
    is_new_user: bool
    user_type: str


class ConversationHistoryItem(BaseModel):
    """对话历史项模型"""
    id: int
    message_type: str
    content: str
    round_number: int
    created_at: str
    context_data: Optional[Dict[str, Any]] = None
    extracted_elements: Optional[Dict[str, Any]] = None


class ConversationHistoryResponse(BaseModel):
    """对话历史响应模型"""
    conversations: List[ConversationHistoryItem]
    total_count: int
    session_id: str


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str
    last_message: str
    last_message_time: str
    created_time: str
    message_count: int
    current_stage: Optional[str] = None


class UserSessionsResponse(BaseModel):
    """用户会话列表响应模型"""
    sessions: List[SessionInfo]
    total_count: int


class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")


class StatusUpdateMessage(BaseModel):
    """状态更新消息模型"""
    status: str = Field(..., description="状态")
    message: str = Field(..., description="状态描述")
    timestamp: float = Field(..., description="时间戳")


class StrategyUpdateMessage(BaseModel):
    """策略更新消息模型"""
    strategy: Dict[str, Any] = Field(..., description="策略数据")
    update_type: str = Field(..., description="更新类型")
    timestamp: float = Field(..., description="时间戳")
