// 用户相关类型
export interface User {
  id: number;
  phone_number: string;
  nickname?: string;
  is_active: boolean;
  is_new_user: boolean;
}

export interface LoginRequest {
  phone_number: string;
  password: string;
}

export interface RegisterRequest {
  phone_number: string;
  password: string;
  nickname?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 对话相关类型
export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  status?: 'sending' | 'sent' | 'error';
}

export interface ConversationSession {
  session_id: string;
  last_message: string;
  last_message_time: string;
  message_count: number;
}

export interface ConversationContext {
  session_id: string;
  messages: Message[];
  current_stage?: string;
  extracted_elements?: Record<string, any>;
  current_strategy?: Strategy;
}

// 策略相关类型
export interface ETFAllocation {
  etf_code: string;
  etf_name: string;
  weight: number;
  asset_class?: string;
  sector?: string;
  allocation_percentage?: number;
}

export interface Strategy {
  id?: number;
  name: string;
  description?: string;
  investment_philosophy?: string;
  target_return?: number;
  max_drawdown?: number;
  risk_level?: string;
  investment_amount?: number;
  rebalance_frequency?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  etf_allocations: ETFAllocation[];
  asset_allocation?: Record<string, number>;
  performance_estimates?: PerformanceMetrics;
}

export interface PerformanceMetrics {
  expected_annual_return?: number;
  expected_volatility?: number;
  expected_max_drawdown?: number;
  expected_sharpe_ratio?: number;
  total_return?: number;
  annual_return?: number;
  volatility?: number;
  max_drawdown?: number;
  sharpe_ratio?: number;
  win_rate?: number;
  confidence_level?: number;
}

export interface BacktestResult {
  strategy_id: number;
  backtest_period: string;
  performance_metrics: PerformanceMetrics;
  daily_data: BacktestDataPoint[];
}

export interface BacktestDataPoint {
  date: string;
  portfolio_value: number;
  daily_return: number;
  cumulative_return: number;
}

// ETF相关类型
export interface ETFProduct {
  id?: number;
  code: string;
  name: string;
  full_name?: string;
  asset_class?: string;
  sector?: string;
  region?: string;
  nav?: number;
  market_cap?: number;
  expense_ratio?: number;
  dividend_yield?: number;
  volatility?: number;
  beta?: number;
  sharpe_ratio?: number;
  listing_date?: string;
  performance_metrics?: PerformanceMetrics;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'message' | 'status_update' | 'error' | 'strategy_update';
  data: any;
}

export interface StatusUpdate {
  status: string;
  message: string;
  timestamp: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 状态管理类型
export interface RootState {
  auth: AuthState;
  conversation: ConversationState;
  strategy: StrategyState;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface ConversationState {
  sessions: ConversationSession[];
  currentSession: ConversationContext | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  websocket: WebSocket | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  currentStatus: StatusUpdate | null;
}

export interface StrategyState {
  strategies: Strategy[];
  currentStrategy: Strategy | null;
  backtestResult: BacktestResult | null;
  loading: boolean;
  error: string | null;
}

// 组件Props类型
export interface ConversationPanelProps {
  className?: string;
}

export interface StrategyDisplayProps {
  strategy?: Strategy;
  className?: string;
}

export interface StrategyHistoryProps {
  className?: string;
}

// 表单类型
export interface LoginFormData {
  phone_number: string;
  password: string;
}

export interface RegisterFormData {
  phone_number: string;
  password: string;
  confirm_password: string;
  nickname?: string;
}

// 配置类型
export interface AppConfig {
  apiBaseUrl: string;
  websocketUrl: string;
  maxMessageLength: number;
  reconnectInterval: number;
  maxReconnectAttempts: number;
}
