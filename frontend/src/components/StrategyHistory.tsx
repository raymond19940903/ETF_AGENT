import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { getStrategyHistoryAsync, deleteStrategyAsync, setCurrentStrategy } from '../store/strategySlice';
import type { Strategy, StrategyHistoryProps } from '../types';
import Card from './ui/Card';
import Button from './ui/Button';
import styles from './StrategyHistory.module.css';

const StrategyHistory: React.FC<StrategyHistoryProps> = ({ className }) => {
  const dispatch = useDispatch();
  const { strategies, loading } = useSelector((state: RootState) => state.strategy);

  useEffect(() => {
    dispatch(getStrategyHistoryAsync() as any);
  }, [dispatch]);

  const handleViewStrategy = (strategy: Strategy) => {
    dispatch(setCurrentStrategy(strategy));
    console.log('已切换到策略:', strategy.name);
  };

  const handleDeleteStrategy = async (strategyId: number) => {
    if (window.confirm('确定要删除这个策略吗？此操作无法撤销。')) {
      try {
        await dispatch(deleteStrategyAsync(strategyId) as any).unwrap();
      } catch (error) {
        console.error('删除策略失败:', error);
      }
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    const colorMap: Record<string, string> = {
      '保守': '#52c41a',
      '稳健': '#1890ff',
      '积极': '#fa8c16',
      '激进': '#ff4d4f',
    };
    return colorMap[riskLevel] || '#8c8c8c';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null) return '--';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <Card className={`${styles.historyContainer} ${className || ''}`}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p className={styles.loadingText}>正在加载策略历史...</p>
        </div>
      </Card>
    );
  }

  if (!strategies || strategies.length === 0) {
    return (
      <Card className={`${styles.historyContainer} ${className || ''}`}>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📈</div>
          <h3 className={styles.emptyTitle}>暂无策略记录</h3>
          <p className={styles.emptyDescription}>
            您还没有保存任何策略，快去对话页面创建您的第一个策略吧！
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`${styles.historyContainer} ${className || ''}`}>
      <div className={styles.header}>
        <h2 className={styles.title}>策略历史记录</h2>
        <div className={styles.stats}>
          <span className={styles.statItem}>
            共 <strong>{strategies.length}</strong> 个策略
          </span>
        </div>
      </div>

      <div className={styles.strategiesList}>
        {strategies.map((strategy) => (
          <div key={strategy.id} className={styles.strategyCard}>
            <div className={styles.cardHeader}>
              <div className={styles.strategyInfo}>
                <h3 className={styles.strategyName}>{strategy.name}</h3>
                <div className={styles.strategyMeta}>
                  <span 
                    className={styles.riskTag}
                    style={{ backgroundColor: getRiskLevelColor(strategy.riskLevel) }}
                  >
                    {strategy.riskLevel}
                  </span>
                  <span className={styles.createDate}>
                    创建于 {formatDate(strategy.createdAt)}
                  </span>
                </div>
              </div>
              <div className={styles.cardActions}>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => handleViewStrategy(strategy)}
                >
                  查看详情
                </Button>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => handleDeleteStrategy(strategy.id)}
                  className={styles.deleteButton}
                >
                  删除
                </Button>
              </div>
            </div>

            <div className={styles.cardContent}>
              <div className={styles.description}>
                {strategy.description || '暂无描述'}
              </div>

              {strategy.performance && (
                <div className={styles.performanceMetrics}>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>年化收益</span>
                    <span 
                      className={`${styles.metricValue} ${
                        (strategy.performance.annualReturn || 0) > 0 
                          ? styles.positive 
                          : styles.negative
                      }`}
                    >
                      {formatPercentage(strategy.performance.annualReturn)}
                    </span>
                  </div>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>最大回撤</span>
                    <span className={`${styles.metricValue} ${styles.negative}`}>
                      {formatPercentage(strategy.performance.maxDrawdown)}
                    </span>
                  </div>
                  <div className={styles.metric}>
                    <span className={styles.metricLabel}>夏普比率</span>
                    <span className={styles.metricValue}>
                      {strategy.performance.sharpeRatio?.toFixed(2) || '--'}
                    </span>
                  </div>
                </div>
              )}

              {strategy.allocations && strategy.allocations.length > 0 && (
                <div className={styles.allocationsPreview}>
                  <span className={styles.allocationsLabel}>配置概览：</span>
                  <div className={styles.allocationTags}>
                    {strategy.allocations.slice(0, 3).map((alloc, index) => (
                      <span key={index} className={styles.allocationTag}>
                        {alloc.etfName} ({alloc.percentage}%)
                      </span>
                    ))}
                    {strategy.allocations.length > 3 && (
                      <span className={styles.moreTag}>
                        +{strategy.allocations.length - 3} 更多
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default StrategyHistory;