/**
 * 用户认证自定义Hook
 */
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { getCurrentUserAsync, logoutAsync } from '../store/authSlice';
import type { User, LoginRequest, RegisterRequest } from '../types';

export const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, token, isAuthenticated, loading, error } = useSelector((state: RootState) => state.auth);

  // 检查认证状态
  useEffect(() => {
    if (token && !user) {
      // 有token但没有用户信息，尝试获取用户信息
      dispatch(getCurrentUserAsync());
    }
  }, [token, user, dispatch]);

  // 登录
  const login = async (data: LoginRequest): Promise<void> => {
    const { loginAsync } = await import('../store/authSlice');
    await dispatch(loginAsync(data)).unwrap();
  };

  // 注册
  const register = async (data: RegisterRequest): Promise<void> => {
    const { registerAsync } = await import('../store/authSlice');
    await dispatch(registerAsync(data)).unwrap();
  };

  // 登出
  const logout = async (): Promise<void> => {
    await dispatch(logoutAsync());
    navigate('/login');
  };

  // 更新用户信息
  const updateUserInfo = async (data: Partial<User>): Promise<void> => {
    const { updateUserInfoAsync } = await import('../store/authSlice');
    await dispatch(updateUserInfoAsync(data)).unwrap();
  };

  // 检查是否需要重定向
  const checkAuthRedirect = () => {
    const publicPaths = ['/login', '/register'];
    const isPublicPath = publicPaths.includes(location.pathname);

    if (!isAuthenticated && !isPublicPath) {
      navigate('/login', { replace: true });
    } else if (isAuthenticated && isPublicPath) {
      navigate('/', { replace: true });
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateUserInfo,
    checkAuthRedirect
  };
};
