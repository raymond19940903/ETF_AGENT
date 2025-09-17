import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { loginAsync } from '../store/authSlice';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import type { LoginFormData } from '../types';
import styles from './AuthPages.module.css';

/**
 * 登录页面 - 科技风格设计
 */
const LoginPage: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state: RootState) => state.auth);
  
  const [formData, setFormData] = useState<LoginFormData>({
    phoneNumber: '',
    password: ''
  });
  const [errors, setErrors] = useState<Partial<LoginFormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginFormData> = {};
    
    if (!formData.phoneNumber) {
      newErrors.phoneNumber = '请输入手机号';
    } else if (!/^1[3-9]\d{9}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = '请输入正确的手机号';
    }
    
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6位';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await dispatch(loginAsync(formData)).unwrap();
      navigate('/');
    } catch (error) {
      // 错误已在slice中处理
    }
  };

  const handleInputChange = (field: keyof LoginFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
    
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <Card className={styles.authCard}>
          <div className={styles.authHeader}>
            <h1 className={styles.authTitle}>欢迎登录</h1>
            <p className={styles.authSubtitle}>ETF资产配置策略系统</p>
          </div>

          <form className={styles.authForm} onSubmit={handleSubmit}>
            <div className={styles.formGroup}>
              <Input
                type="tel"
                placeholder="请输入手机号"
                value={formData.phoneNumber}
                onChange={handleInputChange('phoneNumber')}
                status={errors.phoneNumber ? 'error' : 'default'}
                errorMessage={errors.phoneNumber}
                prefix="📱"
                size="large"
                block
              />
            </div>

            <div className={styles.formGroup}>
              <Input
                type="password"
                placeholder="请输入密码"
                value={formData.password}
                onChange={handleInputChange('password')}
                status={errors.password ? 'error' : 'default'}
                errorMessage={errors.password}
                prefix="🔒"
                size="large"
                block
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="large"
              loading={loading}
              block
              className={styles.submitButton}
            >
              登录
            </Button>
          </form>

          <div className={styles.authFooter}>
            <div className={styles.divider}>
              <span>还没有账户？</span>
            </div>
            <Link to="/register" className={styles.switchLink}>
              立即注册
            </Link>
          </div>
        </Card>
      </div>
      
      <div className={styles.authBackground}>
        <div className={styles.backgroundPattern}></div>
      </div>
    </div>
  );
};

export default LoginPage;