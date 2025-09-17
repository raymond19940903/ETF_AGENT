import React, { ButtonHTMLAttributes } from 'react';
import classNames from 'classnames';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'text' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  icon?: React.ReactNode;
  block?: boolean;
}

/**
 * 自研按钮组件 - 科技风格设计
 * 
 * @param variant - 按钮类型：primary(主要) | secondary(次要) | text(文字) | danger(危险)
 * @param size - 按钮尺寸：small | medium | large
 * @param loading - 加载状态
 * @param icon - 前置图标
 * @param block - 是否为块级按钮
 */
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  icon,
  block = false,
  children,
  className,
  disabled,
  ...props
}) => {
  const buttonClass = classNames(
    styles.button,
    styles[variant],
    styles[size],
    {
      [styles.loading]: loading,
      [styles.disabled]: disabled || loading,
      [styles.block]: block,
      [styles.iconOnly]: !children && icon,
    },
    className
  );

  return (
    <button
      className={buttonClass}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className={styles.spinner} />}
      {icon && !loading && <span className={styles.icon}>{icon}</span>}
      {children && <span className={styles.content}>{children}</span>}
    </button>
  );
};

export default Button;
