/**
 * API服务模块
 */
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User,
  Strategy,
  ConversationSession,
  BacktestResult,
  ApiResponse 
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // 清除本地存储的认证信息
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_info');
          // 重定向到登录页面
          window.location.href = '/login';
        } else if (error.response?.status === 500) {
          console.error('服务器内部错误，请稍后重试');
        } else if (error.code === 'ECONNABORTED') {
          console.error('请求超时，请检查网络连接');
        }
        return Promise.reject(error);
      }
    );
  }

  // 用户认证相关API
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/api/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/api/auth/logout');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/api/auth/me');
    return response.data;
  }

  async updateUserInfo(data: Partial<User>): Promise<User> {
    const response = await this.api.put<User>('/api/auth/me', data);
    return response.data;
  }

  // 对话相关API
  async startConversation(): Promise<{ session_id: string; welcome_message: string; is_new_user: boolean }> {
    const response = await this.api.post('/api/conversation/start');
    return response.data;
  }

  async getConversationHistory(sessionId: string): Promise<{ conversations: any[] }> {
    const response = await this.api.get(`/api/conversation/history/${sessionId}`);
    return response.data;
  }

  async getUserSessions(): Promise<{ sessions: ConversationSession[] }> {
    const response = await this.api.get('/api/conversation/sessions');
    return response.data;
  }

  // 策略相关API
  async getStrategyDetail(strategyId: number): Promise<Strategy> {
    const response = await this.api.get<Strategy>(`/api/strategy/${strategyId}`);
    return response.data;
  }

  async saveStrategy(data: Partial<Strategy>): Promise<{ success: boolean; strategy_id: number; message: string }> {
    const response = await this.api.post('/api/strategy/save', data);
    return response.data;
  }

  async getStrategyHistory(): Promise<{ strategies: Strategy[] }> {
    const response = await this.api.get('/api/strategy/history');
    return response.data;
  }

  async deleteStrategy(strategyId: number): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete(`/api/strategy/${strategyId}`);
    return response.data;
  }

  async getStrategyBacktest(strategyId: number): Promise<BacktestResult> {
    const response = await this.api.get<BacktestResult>(`/api/strategy/${strategyId}/backtest`);
    return response.data;
  }

  // 系统信息API
  async getSystemInfo(): Promise<any> {
    const response = await this.api.get('/');
    return response.data;
  }

  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
