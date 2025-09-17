"""用户认证相关数据模型"""
from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class UserRegister(BaseModel):
    """用户注册模型"""
    phone_number: str = Field(..., description="手机号")
    password: str = Field(..., min_length=8, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    phone_number: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    phone_number: str
    nickname: Optional[str]
    is_active: bool
    is_new_user: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None


class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    
    
class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
