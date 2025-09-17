import React, { HTMLAttributes } from 'react';
import classNames from 'classnames';
import styles from './Card.module.css';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  extra?: React.ReactNode;
  size?: 'small' | 'default' | 'large';
  hoverable?: boolean;
  bordered?: boolean;
  loading?: boolean;
  children: React.ReactNode;
}

/**
 * 自研卡片组件 - 科技风格设计
 * 
 * @param title - 卡片标题
 * @param extra - 额外的头部内容
 * @param size - 卡片尺寸
 * @param hoverable - 是否支持悬停效果
 * @param bordered - 是否显示边框
 * @param loading - 加载状态
 */
const Card: React.FC<CardProps> = ({
  title,
  extra,
  size = 'default',
  hoverable = false,
  bordered = true,
  loading = false,
  children,
  className,
  ...props
}) => {
  const cardClass = classNames(
    styles.card,
    styles[size],
    {
      [styles.hoverable]: hoverable,
      [styles.bordered]: bordered,
      [styles.loading]: loading,
    },
    className
  );

  return (
    <div className={cardClass} {...props}>
      {(title || extra) && (
        <div className={styles.cardHeader}>
          {title && <div className={styles.cardTitle}>{title}</div>}
          {extra && <div className={styles.cardExtra}>{extra}</div>}
        </div>
      )}
      
      <div className={styles.cardBody}>
        {loading ? (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner}></div>
            <span className={styles.loadingText}>加载中...</span>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default Card;
