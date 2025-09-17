/**
 * 工具函数
 */

// 格式化数字
export const formatNumber = (num: number, decimals: number = 2): string => {
  return num.toFixed(decimals);
};

// 格式化百分比
export const formatPercentage = (num: number, decimals: number = 2): string => {
  return `${formatNumber(num, decimals)}%`;
};

// 格式化金额
export const formatCurrency = (amount: number): string => {
  return `¥${amount.toLocaleString()}`;
};

// 格式化日期
export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN');
};

// 格式化时间
export const formatDateTime = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleString('zh-CN');
};

// 生成随机ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

// 防抖函数
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// 节流函数
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// 深拷贝
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

// 验证手机号
export const validatePhoneNumber = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

// 验证密码强度
export const validatePassword = (password: string): {
  isValid: boolean;
  message: string;
} => {
  if (password.length < 8) {
    return { isValid: false, message: '密码长度不能少于8位' };
  }
  
  if (!/[A-Za-z]/.test(password)) {
    return { isValid: false, message: '密码必须包含字母' };
  }
  
  if (!/\d/.test(password)) {
    return { isValid: false, message: '密码必须包含数字' };
  }
  
  return { isValid: true, message: '密码强度良好' };
};

// 获取风险等级颜色
export const getRiskLevelColor = (riskLevel: string): string => {
  const colorMap: Record<string, string> = {
    '保守': '#52c41a',
    '稳健': '#1890ff', 
    '积极': '#fa8c16',
    '激进': '#f5222d',
  };
  return colorMap[riskLevel] || '#1890ff';
};

// 获取资产类别颜色
export const getAssetClassColor = (assetClass: string): string => {
  const colorMap: Record<string, string> = {
    '股票': '#1890ff',
    '债券': '#52c41a',
    '商品': '#fa8c16',
    '房地产': '#722ed1',
    '货币': '#13c2c2',
  };
  
  for (const [key, color] of Object.entries(colorMap)) {
    if (assetClass.includes(key)) {
      return color;
    }
  }
  
  return '#8c8c8c';
};

// 计算收益率颜色
export const getReturnColor = (returnValue: number): string => {
  if (returnValue > 0) return '#52c41a';
  if (returnValue < 0) return '#f5222d';
  return '#8c8c8c';
};

// 本地存储工具
export const storage = {
  get: (key: string): any => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },
  
  set: (key: string, value: any): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('存储数据失败:', error);
    }
  },
  
  remove: (key: string): void => {
    localStorage.removeItem(key);
  },
  
  clear: (): void => {
    localStorage.clear();
  }
};

// URL参数工具
export const urlParams = {
  get: (name: string): string | null => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  },
  
  set: (name: string, value: string): void => {
    const url = new URL(window.location.href);
    url.searchParams.set(name, value);
    window.history.replaceState({}, '', url.toString());
  },
  
  remove: (name: string): void => {
    const url = new URL(window.location.href);
    url.searchParams.delete(name);
    window.history.replaceState({}, '', url.toString());
  }
};

// 错误处理
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return '操作失败，请稍后重试';
};

// 文件下载
export const downloadFile = (content: string, filename: string, type: string = 'text/plain'): void => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// 复制到剪贴板
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textArea);
    return success;
  }
};
