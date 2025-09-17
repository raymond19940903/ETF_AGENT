/**
 * 策略管理自定义Hook
 */
import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { 
  getStrategyHistoryAsync, 
  saveStrategyAsync, 
  deleteStrategyAsync,
  getStrategyBacktestAsync,
  setCurrentStrategy,
  clearCurrentStrategy
} from '../store/strategySlice';
import type { Strategy } from '../types';

export const useStrategy = () => {
  const dispatch = useDispatch();
  const { strategies, currentStrategy, backtestResult, loading, error } = useSelector(
    (state: RootState) => state.strategy
  );

  // 获取策略历史
  const getStrategyHistory = useCallback(async () => {
    try {
      await dispatch(getStrategyHistoryAsync()).unwrap();
    } catch (error) {
      console.error('获取策略历史失败:', error);
    }
  }, [dispatch]);

  // 保存策略
  const saveStrategy = useCallback(async (strategy: Partial<Strategy>) => {
    try {
      const result = await dispatch(saveStrategyAsync(strategy)).unwrap();
      return result;
    } catch (error) {
      console.error('保存策略失败:', error);
      throw error;
    }
  }, [dispatch]);

  // 删除策略
  const deleteStrategy = useCallback(async (strategyId: number) => {
    try {
      await dispatch(deleteStrategyAsync(strategyId)).unwrap();
    } catch (error) {
      console.error('删除策略失败:', error);
      throw error;
    }
  }, [dispatch]);

  // 获取回测结果
  const getBacktestResult = useCallback(async (strategyId: number) => {
    try {
      const result = await dispatch(getStrategyBacktestAsync(strategyId)).unwrap();
      return result;
    } catch (error) {
      console.error('获取回测结果失败:', error);
      throw error;
    }
  }, [dispatch]);

  // 设置当前策略
  const selectStrategy = useCallback((strategy: Strategy | null) => {
    dispatch(setCurrentStrategy(strategy));
  }, [dispatch]);

  // 清除当前策略
  const clearStrategy = useCallback(() => {
    dispatch(clearCurrentStrategy());
  }, [dispatch]);

  // 获取最佳策略
  const getBestStrategy = useCallback((): Strategy | null => {
    if (!strategies.length) return null;
    
    return strategies.reduce((best, current) => {
      const bestReturn = best.target_return || 0;
      const currentReturn = current.target_return || 0;
      return currentReturn > bestReturn ? current : best;
    });
  }, [strategies]);

  // 按风险等级分组策略
  const getStrategiesByRiskLevel = useCallback(() => {
    const grouped: Record<string, Strategy[]> = {};
    
    strategies.forEach(strategy => {
      const riskLevel = strategy.risk_level || '稳健';
      if (!grouped[riskLevel]) {
        grouped[riskLevel] = [];
      }
      grouped[riskLevel].push(strategy);
    });
    
    return grouped;
  }, [strategies]);

  // 计算策略统计信息
  const getStrategyStats = useCallback(() => {
    if (!strategies.length) {
      return {
        totalStrategies: 0,
        avgTargetReturn: 0,
        avgInvestmentAmount: 0,
        riskDistribution: {}
      };
    }

    const totalStrategies = strategies.length;
    const avgTargetReturn = strategies.reduce((sum, s) => sum + (s.target_return || 0), 0) / totalStrategies;
    const avgInvestmentAmount = strategies.reduce((sum, s) => sum + (s.investment_amount || 0), 0) / totalStrategies;
    
    const riskDistribution: Record<string, number> = {};
    strategies.forEach(strategy => {
      const riskLevel = strategy.risk_level || '稳健';
      riskDistribution[riskLevel] = (riskDistribution[riskLevel] || 0) + 1;
    });

    return {
      totalStrategies,
      avgTargetReturn: Math.round(avgTargetReturn * 100) / 100,
      avgInvestmentAmount: Math.round(avgInvestmentAmount),
      riskDistribution
    };
  }, [strategies]);

  return {
    strategies,
    currentStrategy,
    backtestResult,
    loading,
    error,
    getStrategyHistory,
    saveStrategy,
    deleteStrategy,
    getBacktestResult,
    selectStrategy,
    clearStrategy,
    getBestStrategy,
    getStrategiesByRiskLevel,
    getStrategyStats
  };
};
