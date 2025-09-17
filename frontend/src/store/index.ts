/**
 * Redux Store配置
 */
import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import authSlice from './authSlice';
import conversationSlice from './conversationSlice';
import strategySlice from './strategySlice';
// RootState类型将在这里定义

export const store = configureStore({
  reducer: {
    auth: authSlice,
    conversation: conversationSlice,
    strategy: strategySlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['conversation/setWebSocket'],
        ignoredPaths: ['conversation.websocket'],
      },
    }),
  devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 使用标准的React Redux hooks

export default store;
