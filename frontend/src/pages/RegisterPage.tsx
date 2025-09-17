import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { registerAsync } from '../store/authSlice';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import type { RegisterFormData } from '../types';
import styles from './AuthPages.module.css';

const RegisterPage: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState<RegisterFormData>({
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    nickname: '',
  });
  const [errors, setErrors] = useState<{
    phoneNumber?: string;
    password?: string;
    confirmPassword?: string;
    nickname?: string;
  }>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // 清除对应字段的错误
    if (errors[name as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = () => {
    const newErrors: typeof errors = {};

    // 手机号验证
    if (!formData.phoneNumber) {
      newErrors.phoneNumber = '手机号不能为空';
    } else if (!/^1[3-9]\d{9}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = '请输入有效的手机号';
    }

    // 密码验证
    if (!formData.password) {
      newErrors.password = '密码不能为空';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码长度至少6位';
    }

    // 确认密码验证
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    // 昵称验证
    if (!formData.nickname) {
      newErrors.nickname = '昵称不能为空';
    } else if (formData.nickname.length < 2) {
      newErrors.nickname = '昵称长度至少2位';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      await dispatch(registerAsync(formData) as any).unwrap();
      navigate('/');
    } catch (error: any) {
      console.error('注册失败:', error);
      // 这里可以根据错误类型设置特定的错误消息
      if (error.includes('手机号已存在')) {
        setErrors({ phoneNumber: '该手机号已被注册' });
      }
    }
  };

  return (
    <div className={styles.authPage}>
      <Card className={styles.authCard}>
        <div className={styles.authHeader}>
          <h1>用户注册</h1>
          <p>创建您的ETF策略账户</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className={styles.formGroup}>
            <label htmlFor="phoneNumber" className={styles.formLabel}>
              手机号 <span className={styles.required}>*</span>
            </label>
            <Input
              type="tel"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              placeholder="请输入手机号"
              fullWidth
              variant={errors.phoneNumber ? 'error' : 'default'}
              prefix="📱"
            />
            {errors.phoneNumber && (
              <p className={styles.errorMessage}>{errors.phoneNumber}</p>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="nickname" className={styles.formLabel}>
              昵称 <span className={styles.required}>*</span>
            </label>
            <Input
              type="text"
              id="nickname"
              name="nickname"
              value={formData.nickname}
              onChange={handleChange}
              placeholder="请输入昵称"
              fullWidth
              variant={errors.nickname ? 'error' : 'default'}
              prefix="👤"
            />
            {errors.nickname && (
              <p className={styles.errorMessage}>{errors.nickname}</p>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.formLabel}>
              密码 <span className={styles.required}>*</span>
            </label>
            <Input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="请输入密码（至少6位）"
              fullWidth
              variant={errors.password ? 'error' : 'default'}
              prefix="🔒"
            />
            {errors.password && (
              <p className={styles.errorMessage}>{errors.password}</p>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword" className={styles.formLabel}>
              确认密码 <span className={styles.required}>*</span>
            </label>
            <Input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="请再次输入密码"
              fullWidth
              variant={errors.confirmPassword ? 'error' : 'default'}
              prefix="🔒"
            />
            {errors.confirmPassword && (
              <p className={styles.errorMessage}>{errors.confirmPassword}</p>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            loading={loading}
            fullWidth
            className={styles.submitButton}
            disabled={loading}
          >
            {loading ? '注册中...' : '立即注册'}
          </Button>
        </form>

        <div className={styles.authFooter}>
          <span className={styles.footerText}>已有账户？</span>
          <Link to="/login" className={styles.loginLink}>
            立即登录
          </Link>
        </div>

        <div className={styles.terms}>
          <p>
            注册即表示您同意我们的
            <a href="#" className={styles.termsLink}>服务条款</a>
            和
            <a href="#" className={styles.termsLink}>隐私政策</a>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default RegisterPage;