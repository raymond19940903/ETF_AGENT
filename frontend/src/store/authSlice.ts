/**
 * 用户认证状态管理
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../services/api';
import type { AuthState, User, LoginRequest, RegisterRequest, AuthResponse } from '../types';

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('auth_token'),
  isAuthenticated: !!localStorage.getItem('auth_token'),
  loading: false,
  error: null,
};

// 异步actions
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (data: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await apiService.login(data);
      
      // 保存到本地存储
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_info', JSON.stringify(response.user));
      
      console.log('登录成功');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '登录失败';
      console.error('登录失败:', errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const registerAsync = createAsyncThunk(
  'auth/register',
  async (data: RegisterRequest, { rejectWithValue }) => {
    try {
      const response = await apiService.register(data);
      
      // 保存到本地存储
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_info', JSON.stringify(response.user));
      
      message.success('注册成功');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '注册失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const logoutAsync = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await apiService.logout();
      
      // 清除本地存储
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      
      message.success('退出登录成功');
    } catch (error: any) {
      // 即使API调用失败，也要清除本地存储
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      
      const errorMessage = error.response?.data?.detail || '退出登录失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const getCurrentUserAsync = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await apiService.getCurrentUser();
      
      // 更新本地存储
      localStorage.setItem('user_info', JSON.stringify(user));
      
      return user;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '获取用户信息失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const updateUserInfoAsync = createAsyncThunk(
  'auth/updateUserInfo',
  async (data: Partial<User>, { rejectWithValue }) => {
    try {
      const user = await apiService.updateUserInfo(data);
      
      // 更新本地存储
      localStorage.setItem('user_info', JSON.stringify(user));
      
      message.success('用户信息更新成功');
      return user;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '更新用户信息失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    initializeAuth: (state) => {
      const token = localStorage.getItem('auth_token');
      const userInfo = localStorage.getItem('user_info');
      
      if (token && userInfo) {
        try {
          state.token = token;
          state.user = JSON.parse(userInfo);
          state.isAuthenticated = true;
        } catch (error) {
          // 如果解析失败，清除本地存储
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_info');
          state.token = null;
          state.user = null;
          state.isAuthenticated = false;
        }
      }
    },
  },
  extraReducers: (builder) => {
    // 登录
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action: PayloadAction<AuthResponse>) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // 注册
    builder
      .addCase(registerAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerAsync.fulfilled, (state, action: PayloadAction<AuthResponse>) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(registerAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // 退出登录
    builder
      .addCase(logoutAsync.pending, (state) => {
        state.loading = true;
      })
      .addCase(logoutAsync.fulfilled, (state) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
      })
      .addCase(logoutAsync.rejected, (state, action) => {
        state.loading = false;
        // 即使退出失败，也要清除状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      });

    // 获取当前用户
    builder
      .addCase(getCurrentUserAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCurrentUserAsync.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(getCurrentUserAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        // 如果获取用户信息失败，可能token已过期
        if (action.payload === '401') {
          state.user = null;
          state.token = null;
          state.isAuthenticated = false;
        }
      });

    // 更新用户信息
    builder
      .addCase(updateUserInfoAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserInfoAsync.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(updateUserInfoAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, initializeAuth } = authSlice.actions;
export default authSlice.reducer;
