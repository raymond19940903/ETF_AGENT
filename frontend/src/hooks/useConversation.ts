/**
 * 对话管理自定义Hook
 */
import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { 
  startConversationAsync,
  getUserSessionsAsync,
  addMessage,
  clearMessages,
  setConnectionStatus
} from '../store/conversationSlice';
import { useWebSocket } from './useWebSocket';
import type { Message } from '../types';

export const useConversation = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { 
    sessions, 
    currentSession, 
    messages, 
    loading, 
    error,
    connectionStatus,
    currentStatus
  } = useSelector((state: RootState) => state.conversation);

  const { sendMessage: sendWebSocketMessage } = useWebSocket({
    sessionId: currentSession?.session_id,
    autoReconnect: true
  });

  // 开始新对话
  const startNewConversation = useCallback(async () => {
    try {
      await dispatch(startConversationAsync()).unwrap();
    } catch (error) {
      console.error('开始对话失败:', error);
      throw error;
    }
  }, [dispatch]);

  // 发送消息
  const sendMessage = useCallback(async (content: string) => {
    if (!currentSession || !user) {
      throw new Error('会话未建立或用户未登录');
    }

    // 添加用户消息到本地状态
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: Date.now(),
      status: 'sending'
    };
    dispatch(addMessage(userMessage));

    // 发送WebSocket消息
    const success = sendWebSocketMessage({
      user_id: user.id,
      message: content,
    });

    if (success) {
      // 更新消息状态为已发送
      dispatch(addMessage({ ...userMessage, status: 'sent' }));
    } else {
      // 更新消息状态为发送失败
      dispatch(addMessage({ ...userMessage, status: 'error' }));
      throw new Error('消息发送失败');
    }
  }, [currentSession, user, dispatch, sendWebSocketMessage]);

  // 获取用户会话列表
  const getUserSessions = useCallback(async () => {
    try {
      await dispatch(getUserSessionsAsync()).unwrap();
    } catch (error) {
      console.error('获取会话列表失败:', error);
    }
  }, [dispatch]);

  // 清除消息
  const clearConversationMessages = useCallback(() => {
    dispatch(clearMessages());
  }, [dispatch]);

  // 重连WebSocket
  const reconnectWebSocket = useCallback(() => {
    if (currentSession?.session_id) {
      dispatch(setConnectionStatus('connecting'));
      // WebSocket会自动重连
    }
  }, [currentSession, dispatch]);

  // 获取对话统计信息
  const getConversationStats = useCallback(() => {
    const userMessages = messages.filter(msg => msg.type === 'user');
    const assistantMessages = messages.filter(msg => msg.type === 'assistant');
    
    return {
      totalMessages: messages.length,
      userMessages: userMessages.length,
      assistantMessages: assistantMessages.length,
      conversationRounds: Math.max(userMessages.length, assistantMessages.length),
      lastMessageTime: messages.length > 0 ? messages[messages.length - 1].timestamp : null
    };
  }, [messages]);

  // 检查是否可以发送消息
  const canSendMessage = useCallback(() => {
    return connectionStatus === 'connected' && currentSession && user;
  }, [connectionStatus, currentSession, user]);

  // 自动开始对话（如果需要）
  useEffect(() => {
    if (user && !currentSession && !loading) {
      startNewConversation();
    }
  }, [user, currentSession, loading, startNewConversation]);

  return {
    sessions,
    currentSession,
    messages,
    loading,
    error,
    connectionStatus,
    currentStatus,
    startNewConversation,
    sendMessage,
    getUserSessions,
    clearConversationMessages,
    reconnectWebSocket,
    getConversationStats,
    canSendMessage
  };
};
