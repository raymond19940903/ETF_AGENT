"""用户模型"""
from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    phone_number = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_new_user = Column(Boolean, default=True, nullable=False, comment="是否新用户")
    
    # 关联关系
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, phone_number={self.phone_number}, nickname={self.nickname})>"
    
    @property
    def is_old_user(self) -> bool:
        """是否为老用户（有保存的策略）"""
        return len(self.strategies) > 0
    
    def update_user_type(self):
        """更新用户类型"""
        self.is_new_user = len(self.strategies) == 0


# 创建索引
Index('idx_users_phone_number', User.phone_number)
Index('idx_users_is_active', User.is_active)
