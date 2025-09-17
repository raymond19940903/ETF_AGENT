"""用户认证API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.auth.service import AuthService
from app.auth.schemas import UserRegister, UserLogin, Token, UserResponse, PasswordChange
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token, summary="用户注册")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    return auth_service.authenticate_user(user_data)


@router.post("/logout", summary="用户登出")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    return {"success": True, "message": "登出成功"}


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user_info(
    user_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    auth_service = AuthService(db)
    return auth_service.update_user_info(current_user.id, user_data)


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    auth_service = AuthService(db)
    success = auth_service.change_password(current_user.id, password_data)
    
    if success:
        return {"success": True, "message": "密码修改成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码修改失败"
        )
