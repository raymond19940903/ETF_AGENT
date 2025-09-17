/**
 * WebSocket服务模块
 */
import type { WebSocketMessage, StatusUpdate } from '../types';

export type WebSocketEventHandler = (data: any) => void;

export interface WebSocketEventHandlers {
  message?: WebSocketEventHandler;
  status_update?: WebSocketEventHandler;
  error?: WebSocketEventHandler;
  strategy_update?: WebSocketEventHandler;
  connect?: () => void;
  disconnect?: () => void;
  reconnect?: () => void;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private eventHandlers: WebSocketEventHandlers = {};
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectInterval: number = 3000;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isConnecting: boolean = false;
  private shouldReconnect: boolean = true;

  constructor() {
    this.url = this.getWebSocketUrl();
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_HOST || window.location.host;
    return `${protocol}//${host}`;
  }

  connect(sessionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('正在连接中...'));
        return;
      }

      this.isConnecting = true;
      const wsUrl = `${this.url}/api/conversation/ws/${sessionId}`;
      
      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket连接已建立');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.eventHandlers.connect?.();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason);
          this.isConnecting = false;
          this.ws = null;
          this.eventHandlers.disconnect?.();

          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect(sessionId);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误:', error);
          this.isConnecting = false;
          this.eventHandlers.error?.({ message: 'WebSocket连接错误' });
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    const { type, data } = message;

    switch (type) {
      case 'message':
        this.eventHandlers.message?.(data);
        break;
      case 'status_update':
        this.eventHandlers.status_update?.(data as StatusUpdate);
        break;
      case 'error':
        this.eventHandlers.error?.(data);
        break;
      case 'strategy_update':
        this.eventHandlers.strategy_update?.(data);
        break;
      default:
        console.warn('未知的WebSocket消息类型:', type);
    }
  }

  private scheduleReconnect(sessionId: string) {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`尝试重连WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      this.eventHandlers.reconnect?.();
      
      this.connect(sessionId).catch((error) => {
        console.error('WebSocket重连失败:', error);
      });
    }, this.reconnectInterval);
  }

  sendMessage(data: any): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接');
      return false;
    }

    try {
      this.ws.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('发送WebSocket消息失败:', error);
      return false;
    }
  }

  disconnect() {
    this.shouldReconnect = false;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, '主动断开连接');
      this.ws = null;
    }
  }

  on(event: keyof WebSocketEventHandlers, handler: any) {
    this.eventHandlers[event] = handler;
  }

  off(event: keyof WebSocketEventHandlers) {
    delete this.eventHandlers[event];
  }

  getConnectionState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  setReconnectConfig(maxAttempts: number, interval: number) {
    this.maxReconnectAttempts = maxAttempts;
    this.reconnectInterval = interval;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
