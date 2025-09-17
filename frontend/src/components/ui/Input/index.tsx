import React, { InputHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react';
import classNames from 'classnames';
import styles from './Input.module.css';

interface BaseInputProps {
  size?: 'small' | 'medium' | 'large';
  status?: 'default' | 'success' | 'warning' | 'error';
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  label?: string;
  errorMessage?: string;
  helpText?: string;
  block?: boolean;
}

interface InputProps extends BaseInputProps, Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  multiline?: false;
}

interface TextareaProps extends BaseInputProps, Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'> {
  multiline: true;
  autoResize?: boolean;
  minRows?: number;
  maxRows?: number;
}

type CombinedInputProps = InputProps | TextareaProps;

/**
 * 自研输入框组件 - 科技风格设计
 * 
 * @param size - 输入框尺寸
 * @param status - 状态：default | success | warning | error
 * @param prefix - 前置元素（图标等）
 * @param suffix - 后置元素
 * @param label - 标签文本
 * @param errorMessage - 错误信息
 * @param helpText - 帮助文本
 * @param multiline - 是否多行输入
 * @param autoResize - 是否自动调整高度（仅多行）
 */
const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, CombinedInputProps>(
  ({
    size = 'medium',
    status = 'default',
    prefix,
    suffix,
    label,
    errorMessage,
    helpText,
    block = false,
    className,
    multiline,
    ...props
  }, ref) => {
    const containerClass = classNames(
      styles.container,
      {
        [styles.block]: block,
        [styles.hasLabel]: label,
      }
    );

    const inputWrapperClass = classNames(
      styles.inputWrapper,
      styles[size],
      styles[status],
      {
        [styles.hasPrefix]: prefix,
        [styles.hasSuffix]: suffix,
        [styles.focused]: false, // 动态设置
      }
    );

    const inputClass = classNames(
      styles.input,
      className
    );

    const renderInput = () => {
      if (multiline) {
        const textareaProps = props as TextareaProps;
        return (
          <textarea
            ref={ref as React.Ref<HTMLTextAreaElement>}
            className={inputClass}
            {...textareaProps}
          />
        );
      } else {
        const inputProps = props as InputProps;
        return (
          <input
            ref={ref as React.Ref<HTMLInputElement>}
            className={inputClass}
            {...inputProps}
          />
        );
      }
    };

    return (
      <div className={containerClass}>
        {label && (
          <label className={styles.label}>
            {label}
            {props.required && <span className={styles.required}>*</span>}
          </label>
        )}
        
        <div className={inputWrapperClass}>
          {prefix && <span className={styles.prefix}>{prefix}</span>}
          {renderInput()}
          {suffix && <span className={styles.suffix}>{suffix}</span>}
        </div>
        
        {errorMessage && (
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠</span>
            {errorMessage}
          </div>
        )}
        
        {helpText && !errorMessage && (
          <div className={styles.helpText}>{helpText}</div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
