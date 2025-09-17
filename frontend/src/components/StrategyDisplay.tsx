import React, { useEffect, useState } from 'react';
import classNames from 'classnames';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { saveStrategyAsync, getStrategyBacktestAsync } from '../store/strategySlice';
import Button from './ui/Button';
import Card from './ui/Card';
import PieChart from './charts/PieChart';
import type { Strategy, ETFAllocation } from '../types';
import styles from './StrategyDisplay.module.css';

interface StrategyDisplayProps {
  strategy?: Strategy;
  className?: string;
}

/**
 * 策略展示组件 - 科技风格设计
 * 展示ETF配置策略，包括策略详情、配置比例、回测结果等
 */
const StrategyDisplay: React.FC<StrategyDisplayProps> = ({ strategy, className }) => {
  const dispatch = useDispatch();
  const { loading, backtestResult } = useSelector((state: RootState) => state.strategy);
  const [saving, setSaving] = useState(false);

  const handleSaveStrategy = async () => {
    if (!strategy) return;
    
    setSaving(true);
    try {
      await dispatch(saveStrategyAsync(strategy)).unwrap();
    } catch (error) {
      // 错误已在slice中处理
    } finally {
      setSaving(false);
    }
  };

  const handleViewBacktest = async () => {
    if (!strategy?.id) return;
    
    try {
      await dispatch(getStrategyBacktestAsync(strategy.id)).unwrap();
    } catch (error) {
      // 错误已在slice中处理
    }
  };

  // 准备饼图数据
  const getPieChartData = () => {
    if (!strategy?.etf_allocations) return [];
    
    return strategy.etf_allocations.map((allocation: ETFAllocation) => ({
      label: allocation.etf_name || allocation.etf_code,
      value: allocation.allocation_percentage,
      color: getETFColor(allocation.etf_code)
    }));
  };

  // 获取ETF颜色
  const getETFColor = (etfCode: string): string => {
    const colors = [
      '#1890FF', '#52C41A', '#FAAD14', '#FF4D4F', '#722ED1',
      '#13C2C2', '#EB2F96', '#F5222D', '#FA8C16', '#A0D911'
    ];
    const index = etfCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  // 格式化数字
  const formatNumber = (value: number | undefined, decimals: number = 2): string => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(decimals);
  };

  // 格式化百分比
  const formatPercentage = (value: number | undefined, decimals: number = 2): string => {
    if (value === undefined || value === null) return 'N/A';
    return `${value.toFixed(decimals)}%`;
  };

  if (!strategy) {
    return (
      <div className={classNames(styles.strategyDisplay, className)}>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📊</div>
          <h3>暂无策略</h3>
          <p>请通过对话生成您的投资策略</p>
        </div>
      </div>
    );
  }

  return (
    <div className={classNames(styles.strategyDisplay, className)}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <h2 className={styles.title}>{strategy.name || '我的投资策略'}</h2>
          <p className={styles.description}>{strategy.description}</p>
        </div>
        <div className={styles.actions}>
          <Button
            variant="secondary"
            onClick={handleViewBacktest}
            loading={loading}
          >
            📈 查看回测
          </Button>
          <Button
            variant="primary"
            onClick={handleSaveStrategy}
            loading={saving}
          >
            💾 保存策略
          </Button>
        </div>
      </div>

      {/* 投资理念 */}
      {strategy.investment_philosophy && (
        <Card className={styles.philosophyCard}>
          <h3>投资理念</h3>
          <p>{strategy.investment_philosophy}</p>
        </Card>
      )}

      {/* ETF配置 */}
      {strategy.etf_allocations && strategy.etf_allocations.length > 0 && (
        <Card className={styles.allocationCard}>
          <h3>资产配置</h3>
          <div className={styles.allocationContent}>
            <div className={styles.chartSection}>
              <PieChart
                data={getPieChartData()}
                width={300}
                height={300}
                showLegend={true}
                showTooltip={true}
              />
            </div>
            <div className={styles.tableSection}>
              <div className={styles.tableHeader}>
                <div>ETF代码</div>
                <div>ETF名称</div>
                <div>配置比例</div>
                <div>类别</div>
              </div>
              {strategy.etf_allocations.map((allocation: ETFAllocation) => (
                <div key={allocation.etf_code} className={styles.tableRow}>
                  <div className={styles.etfCode}>{allocation.etf_code}</div>
                  <div className={styles.etfName}>{allocation.etf_name}</div>
                  <div className={styles.percentage}>
                    {formatPercentage(allocation.allocation_percentage)}
                  </div>
                  <div className={styles.category}>{allocation.category || 'N/A'}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* 绩效指标 */}
      {strategy.performance_estimates && (
        <Card className={styles.performanceCard}>
          <h3>预期绩效</h3>
          <div className={styles.metricsGrid}>
            <div className={styles.metricItem}>
              <div className={styles.metricValue}>
                {formatPercentage(strategy.performance_estimates.expected_annual_return)}
              </div>
              <div className={styles.metricLabel}>预期年化收益</div>
            </div>
            <div className={styles.metricItem}>
              <div className={styles.metricValue}>
                {formatPercentage(strategy.performance_estimates.expected_volatility)}
              </div>
              <div className={styles.metricLabel}>预期波动率</div>
            </div>
            <div className={styles.metricItem}>
              <div className={styles.metricValue}>
                {formatNumber(strategy.performance_estimates.expected_sharpe_ratio)}
              </div>
              <div className={styles.metricLabel}>预期夏普比率</div>
            </div>
          </div>
        </Card>
      )}

      {/* 回测结果 */}
      {backtestResult && (
        <Card className={styles.backtestCard}>
          <h3>回测结果</h3>
          <div className={styles.backtestContent}>
            <div className={styles.backtestSummary}>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>回测期间:</span>
                <span className={styles.summaryValue}>
                  {backtestResult.start_date} 至 {backtestResult.end_date}
                </span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>总收益率:</span>
                <span className={classNames(styles.summaryValue, {
                  [styles.positive]: (backtestResult.total_return || 0) > 0,
                  [styles.negative]: (backtestResult.total_return || 0) < 0
                })}>
                  {formatPercentage(backtestResult.total_return)}
                </span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryLabel}>最大回撤:</span>
                <span className={styles.summaryValue}>
                  {formatPercentage(backtestResult.max_drawdown)}
                </span>
              </div>
            </div>
            
            {backtestResult.performance_chart_data && (
              <div className={styles.chartPlaceholder}>
                {/* 这里将来实现LineChart组件 */}
                <p>回测曲线图（待实现LineChart组件）</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* 风险提示 */}
      <div className={styles.riskWarning}>
        <div className={styles.warningIcon}>⚠️</div>
        <div className={styles.warningContent}>
          <div className={styles.warningTitle}>风险提示</div>
          <div className={styles.warningText}>
            本策略建议基于历史数据分析，实际投资效果可能与预期存在差异。
            投资有风险，入市需谨慎，请根据自身风险承受能力谨慎决策。
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyDisplay;