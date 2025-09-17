/**
 * 策略状态管理
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../services/api';
import type { StrategyState, Strategy, BacktestResult } from '../types';

const initialState: StrategyState = {
  strategies: [],
  currentStrategy: null,
  backtestResult: null,
  loading: false,
  error: null,
};

// 异步actions
export const getStrategyHistoryAsync = createAsyncThunk(
  'strategy/getHistory',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.getStrategyHistory();
      return response.strategies;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '获取策略历史失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const saveStrategyAsync = createAsyncThunk(
  'strategy/save',
  async (strategy: Partial<Strategy>, { rejectWithValue }) => {
    try {
      const response = await apiService.saveStrategy(strategy);
      console.log('策略保存成功:', response.message);
      return { ...strategy, id: response.strategy_id };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '保存策略失败';
      console.error('策略保存失败:', errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const deleteStrategyAsync = createAsyncThunk(
  'strategy/delete',
  async (strategyId: number, { rejectWithValue }) => {
    try {
      const response = await apiService.deleteStrategy(strategyId);
      console.log('策略删除成功:', response.message);
      return strategyId;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '删除策略失败';
      console.error('策略删除失败:', errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const getStrategyBacktestAsync = createAsyncThunk(
  'strategy/getBacktest',
  async (strategyId: number, { rejectWithValue }) => {
    try {
      const result = await apiService.getStrategyBacktest(strategyId);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '获取回测结果失败';
      return rejectWithValue(errorMessage);
    }
  }
);

const strategySlice = createSlice({
  name: 'strategy',
  initialState,
  reducers: {
    setCurrentStrategy: (state, action: PayloadAction<Strategy | null>) => {
      state.currentStrategy = action.payload;
    },
    updateCurrentStrategy: (state, action: PayloadAction<Partial<Strategy>>) => {
      if (state.currentStrategy) {
        state.currentStrategy = { ...state.currentStrategy, ...action.payload };
      }
    },
    clearCurrentStrategy: (state) => {
      state.currentStrategy = null;
    },
    clearBacktestResult: (state) => {
      state.backtestResult = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 获取策略历史
    builder
      .addCase(getStrategyHistoryAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getStrategyHistoryAsync.fulfilled, (state, action: PayloadAction<Strategy[]>) => {
        state.loading = false;
        state.strategies = action.payload;
      })
      .addCase(getStrategyHistoryAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 保存策略
    builder
      .addCase(saveStrategyAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveStrategyAsync.fulfilled, (state, action) => {
        state.loading = false;
        const savedStrategy = action.payload as Strategy;
        
        // 更新策略列表
        const existingIndex = state.strategies.findIndex(s => s.id === savedStrategy.id);
        if (existingIndex !== -1) {
          state.strategies[existingIndex] = savedStrategy;
        } else {
          state.strategies.unshift(savedStrategy);
        }
        
        // 更新当前策略
        state.currentStrategy = savedStrategy;
      })
      .addCase(saveStrategyAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 删除策略
    builder
      .addCase(deleteStrategyAsync.fulfilled, (state, action: PayloadAction<number>) => {
        const strategyId = action.payload;
        state.strategies = state.strategies.filter(s => s.id !== strategyId);
        
        if (state.currentStrategy?.id === strategyId) {
          state.currentStrategy = null;
        }
      });

    // 获取回测结果
    builder
      .addCase(getStrategyBacktestAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getStrategyBacktestAsync.fulfilled, (state, action: PayloadAction<BacktestResult>) => {
        state.loading = false;
        state.backtestResult = action.payload;
      })
      .addCase(getStrategyBacktestAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setCurrentStrategy,
  updateCurrentStrategy,
  clearCurrentStrategy,
  clearBacktestResult,
  clearError,
} = strategySlice.actions;

export default strategySlice.reducer;
