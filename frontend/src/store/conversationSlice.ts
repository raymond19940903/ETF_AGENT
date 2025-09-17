/**
 * 对话状态管理
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../services/api';
import websocketService from '../services/websocket';
import type { ConversationState, Message, ConversationSession, StatusUpdate } from '../types';

const initialState: ConversationState = {
  sessions: [],
  currentSession: null,
  messages: [],
  loading: false,
  error: null,
  websocket: null,
  connectionStatus: 'disconnected',
  currentStatus: null,
};

// 异步actions
export const startConversationAsync = createAsyncThunk(
  'conversation/start',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.startConversation();
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '开始对话失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const getUserSessionsAsync = createAsyncThunk(
  'conversation/getUserSessions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.getUserSessions();
      return response.sessions;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '获取对话会话失败';
      return rejectWithValue(errorMessage);
    }
  }
);

const conversationSlice = createSlice({
  name: 'conversation',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    updateMessage: (state, action: PayloadAction<{ id: string; updates: Partial<Message> }>) => {
      const { id, updates } = action.payload;
      const messageIndex = state.messages.findIndex(msg => msg.id === id);
      if (messageIndex !== -1) {
        state.messages[messageIndex] = { ...state.messages[messageIndex], ...updates };
      }
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    setConnectionStatus: (state, action: PayloadAction<ConversationState['connectionStatus']>) => {
      state.connectionStatus = action.payload;
    },
    setCurrentStatus: (state, action: PayloadAction<StatusUpdate | null>) => {
      state.currentStatus = action.payload;
    },
    setWebSocket: (state, action: PayloadAction<WebSocket | null>) => {
      state.websocket = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 开始对话
    builder
      .addCase(startConversationAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startConversationAsync.fulfilled, (state, action) => {
        state.loading = false;
        state.currentSession = {
          session_id: action.payload.session_id,
          messages: [],
          extracted_elements: {},
        };
        // 添加欢迎消息
        const welcomeMessage: Message = {
          id: `welcome_${Date.now()}`,
          type: 'assistant',
          content: action.payload.welcome_message,
          timestamp: Date.now(),
        };
        state.messages = [welcomeMessage];
      })
      .addCase(startConversationAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取用户会话
    builder
      .addCase(getUserSessionsAsync.fulfilled, (state, action: PayloadAction<ConversationSession[]>) => {
        state.sessions = action.payload;
      });
  },
});

export const {
  addMessage,
  updateMessage,
  clearMessages,
  setConnectionStatus,
  setCurrentStatus,
  setWebSocket,
  clearError,
} = conversationSlice.actions;

export default conversationSlice.reducer;
