import React, { useEffect, useRef, useState } from 'react';
import classNames from 'classnames';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { 
  startConversationAsync, 
  addMessage, 
  updateMessage,
  setConnectionStatus,
  setCurrentStatus
} from '../store/conversationSlice';
import { setCurrentStrategy } from '../store/strategySlice';
import websocketService from '../services/websocket';
import Button from './ui/Button';
import Input from './ui/Input';
import type { Message } from '../types';
import styles from './ConversationPanel.module.css';

interface ConversationPanelProps {
  className?: string;
}

/**
 * 对话面板组件 - 科技风格设计
 * 提供用户与智能体交互的对话界面，支持实时消息展示和输入
 */
const ConversationPanel: React.FC<ConversationPanelProps> = ({ className }) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { 
    currentSession, 
    messages, 
    loading, 
    connectionStatus,
    currentStatus 
  } = useSelector((state: RootState) => state.conversation);
  
  const [inputValue, setInputValue] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 初始化对话
  useEffect(() => {
    if (!currentSession) {
      dispatch(startConversationAsync());
    }
  }, [dispatch, currentSession]);

  // 建立WebSocket连接
  useEffect(() => {
    if (currentSession?.session_id && user) {
      const sessionId = currentSession.session_id;
      
      dispatch(setConnectionStatus('connecting'));
      
      websocketService.connect(sessionId)
        .then(() => {
          dispatch(setConnectionStatus('connected'));
        })
        .catch(() => {
          dispatch(setConnectionStatus('error'));
        });

      // 设置事件处理器
      websocketService.on('message', (data) => {
        const assistantMessage: Message = {
          id: generateId(),
          type: 'assistant',
          content: data.message,
          timestamp: Date.now(),
        };
        dispatch(addMessage(assistantMessage));

        // 如果有策略更新
        if (data.strategy_updated && data.strategy) {
          dispatch(setCurrentStrategy(data.strategy));
        }
      });

      websocketService.on('status_update', (statusData) => {
        dispatch(setCurrentStatus(statusData));
      });

      websocketService.on('error', (errorData) => {
        console.error('WebSocket错误:', errorData);
      });

      websocketService.on('disconnect', () => {
        dispatch(setConnectionStatus('disconnected'));
      });

      websocketService.on('reconnect', () => {
        dispatch(setConnectionStatus('connecting'));
      });

      return () => {
        websocketService.disconnect();
      };
    }
  }, [currentSession?.session_id, user, dispatch]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !currentSession || !user) return;

    const messageContent = inputValue.trim();
    setInputValue('');
    setSending(true);

    // 添加用户消息
    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content: messageContent,
      timestamp: Date.now(),
      status: 'sending',
    };
    dispatch(addMessage(userMessage));

    // 发送WebSocket消息
    const success = websocketService.sendMessage({
      user_id: user.id,
      message: messageContent,
    });

    if (success) {
      dispatch(updateMessage({
        id: userMessage.id,
        updates: { status: 'sent' }
      }));
    } else {
      dispatch(updateMessage({
        id: userMessage.id,
        updates: { status: 'error' }
      }));
    }

    setSending(false);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const generateId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    
    return (
      <div 
        key={message.id}
        className={classNames(styles.messageItem, {
          [styles.userMessage]: isUser,
          [styles.assistantMessage]: !isUser
        })}
      >
        <div className={styles.messageContent}>
          <div className={classNames(styles.avatar, {
            [styles.userAvatar]: isUser,
            [styles.assistantAvatar]: !isUser
          })}>
            {isUser ? '👤' : '🤖'}
          </div>
          
          <div className={styles.messageBubble}>
            <div className={styles.messageText}>
              {message.content}
            </div>
            <div className={styles.messageMeta}>
              <span className={styles.timestamp}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
              {message.status === 'sending' && (
                <span className={styles.statusIcon}>⏳</span>
              )}
              {message.status === 'error' && (
                <span className={styles.errorIcon}>❌</span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const getConnectionStatusIndicator = () => {
    const statusConfig = {
      connecting: { className: styles.connecting, text: '连接中', icon: '🔄' },
      connected: { className: styles.connected, text: '已连接', icon: '🟢' },
      disconnected: { className: styles.disconnected, text: '未连接', icon: '🔴' },
      error: { className: styles.error, text: '连接错误', icon: '⚠️' },
    };
    
    const config = statusConfig[connectionStatus];
    return (
      <div className={classNames(styles.statusIndicator, config.className)}>
        <span className={styles.statusIcon}>{config.icon}</span>
        <span className={styles.statusText}>{config.text}</span>
      </div>
    );
  };

  return (
    <div className={classNames(styles.conversationPanel, className)}>
      <div className={styles.conversationHeader}>
        <div className={styles.headerTitle}>
          <h3>智能投顾助手</h3>
          {getConnectionStatusIndicator()}
        </div>
        {currentStatus && (
          <div className={styles.currentStatus}>
            <div className={styles.statusDot}></div>
            <span>{currentStatus.message}</span>
          </div>
        )}
      </div>

      <div className={styles.messagesContainer}>
        {loading && (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner}></div>
            <span className={styles.loadingText}>正在初始化对话...</span>
          </div>
        )}
        
        {connectionStatus === 'error' && (
          <div className={styles.errorAlert}>
            <div className={styles.errorIcon}>⚠️</div>
            <div className={styles.errorContent}>
              <div className={styles.errorTitle}>连接错误</div>
              <div className={styles.errorDescription}>
                WebSocket连接失败，请刷新页面重试
              </div>
            </div>
          </div>
        )}

        <div className={styles.messagesList}>
          {messages.map(renderMessage)}
        </div>
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputContainer}>
        <div className={styles.inputWrapper}>
          <Input
            ref={inputRef}
            multiline={true}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="请输入您的投资需求..."
            disabled={connectionStatus !== 'connected' || sending}
            status={connectionStatus === 'error' ? 'error' : 'default'}
          />
          <Button
            variant="primary"
            onClick={handleSendMessage}
            loading={sending}
            disabled={!inputValue.trim() || connectionStatus !== 'connected'}
            className={styles.sendButton}
          >
            📤 发送
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ConversationPanel;