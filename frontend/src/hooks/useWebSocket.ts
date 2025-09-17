/**
 * WebSocket自定义Hook
 */
import { useEffect, useCallback, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { setConnectionStatus, setCurrentStatus, addMessage } from '../store/conversationSlice';
import { setCurrentStrategy } from '../store/strategySlice';
import websocketService from '../services/websocket';
import type { Message } from '../types';

interface UseWebSocketOptions {
  sessionId?: string;
  onMessage?: (message: any) => void;
  onStatusUpdate?: (status: any) => void;
  onError?: (error: any) => void;
  autoReconnect?: boolean;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const dispatch = useDispatch();
  const {
    sessionId,
    onMessage,
    onStatusUpdate,
    onError,
    autoReconnect = true
  } = options;
  
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(async () => {
    if (!sessionId) return;

    try {
      dispatch(setConnectionStatus('connecting'));
      await websocketService.connect(sessionId);
      dispatch(setConnectionStatus('connected'));
      reconnectAttemptsRef.current = 0;
    } catch (error) {
      dispatch(setConnectionStatus('error'));
      
      if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current++;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000 * reconnectAttemptsRef.current);
      }
    }
  }, [sessionId, dispatch, autoReconnect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    websocketService.disconnect();
    dispatch(setConnectionStatus('disconnected'));
  }, [dispatch]);

  const sendMessage = useCallback((data: any) => {
    return websocketService.sendMessage(data);
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    // 设置事件处理器
    websocketService.on('message', (data) => {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: data.message,
        timestamp: Date.now(),
      };
      dispatch(addMessage(assistantMessage));

      if (data.strategy_updated && data.strategy) {
        dispatch(setCurrentStrategy(data.strategy));
      }

      onMessage?.(data);
    });

    websocketService.on('status_update', (statusData) => {
      dispatch(setCurrentStatus(statusData));
      onStatusUpdate?.(statusData);
    });

    websocketService.on('error', (errorData) => {
      console.error('WebSocket错误:', errorData);
      onError?.(errorData);
    });

    websocketService.on('disconnect', () => {
      dispatch(setConnectionStatus('disconnected'));
    });

    websocketService.on('reconnect', () => {
      dispatch(setConnectionStatus('connecting'));
    });

    // 建立连接
    connect();

    return () => {
      disconnect();
    };
  }, [sessionId, connect, disconnect, dispatch, onMessage, onStatusUpdate, onError]);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected: websocketService.isConnected(),
    connectionState: websocketService.getConnectionState()
  };
};
