"""对话模型"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import Base


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id = Column(String(100), nullable=False, index=True, comment="会话ID")
    message_type = Column(String(20), nullable=False, comment="消息类型：user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # 对话上下文
    context_data = Column(JSON, nullable=True, comment="上下文数据")
    extracted_elements = Column(JSON, nullable=True, comment="提取的投资要素")
    
    # 对话状态
    round_number = Column(Integer, default=1, nullable=False, comment="对话轮次")
    status = Column(String(20), default="active", nullable=False, comment="对话状态")
    
    # 关联的策略
    related_strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="关联策略ID")
    
    # 关联关系
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, session_id={self.session_id}, type={self.message_type})>"


# 创建索引
Index('idx_conversations_user_id', Conversation.user_id)
Index('idx_conversations_session_id', Conversation.session_id)
Index('idx_conversations_status', Conversation.status)
Index('idx_conversations_created_at', Conversation.created_at)