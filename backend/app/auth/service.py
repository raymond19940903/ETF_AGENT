"""用户认证服务"""
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.auth.schemas import UserRegister, UserLogin, Token, UserResponse, PasswordChange
from config.settings import settings


class AuthService:
    """用户认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserRegister) -> Token:
        """用户注册"""
        # 检查手机号是否已存在
        existing_user = self.db.query(User).filter(
            User.phone_number == user_data.phone_number
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
        
        # 创建新用户
        password_hash = get_password_hash(user_data.password)
        new_user = User(
            phone_number=user_data.phone_number,
            password_hash=password_hash,
            nickname=user_data.nickname,
            is_new_user=True,
            is_active=True
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id)}, 
            expires_delta=access_token_expires
        )
        
        user_response = UserResponse.from_orm(new_user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    def authenticate_user(self, user_data: UserLogin) -> Token:
        """用户登录认证"""
        user = self.db.query(User).filter(
            User.phone_number == user_data.phone_number
        ).first()
        
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="手机号或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户已被禁用"
            )
        
        # 更新用户类型
        user.update_user_type()
        self.db.commit()
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        
        user_response = UserResponse.from_orm(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """根据手机号获取用户"""
        return self.db.query(User).filter(User.phone_number == phone_number).first()
    
    def update_user_info(self, user_id: int, user_data: dict) -> UserResponse:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """修改密码"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码
        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        
        # 更新密码
        user.password_hash = get_password_hash(password_data.new_password)
        self.db.commit()
        
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """禁用用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.is_active = False
        self.db.commit()
        
        return True
    
    def is_new_user(self, user_id: int) -> bool:
        """判断是否为新用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        return user.is_new_user
    
    def mark_as_old_user(self, user_id: int) -> bool:
        """标记为老用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_new_user = False
        self.db.commit()
        
        return True
