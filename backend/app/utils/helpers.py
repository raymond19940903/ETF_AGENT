"""辅助工具函数"""
# 移除uuid依赖，使用时间戳生成ID
import hashlib
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    """生成会话ID"""
    import time
    import random
    timestamp = int(time.time() * 1000000)
    random_suffix = random.randint(1000, 9999)
    return f"session_{timestamp}_{random_suffix}"


def generate_task_id() -> str:
    """生成任务ID"""
    import time
    import random
    timestamp = int(time.time() * 1000000)
    random_suffix = random.randint(1000, 9999)
    return f"task_{timestamp}_{random_suffix}"


def generate_strategy_hash(strategy_config: Dict[str, Any]) -> str:
    """生成策略哈希值"""
    try:
        # 提取关键配置信息
        key_info = {
            "etf_allocations": strategy_config.get("etf_allocations", []),
            "risk_level": strategy_config.get("risk_level"),
            "target_return": strategy_config.get("target_return"),
            "investment_amount": strategy_config.get("investment_amount")
        }
        
        # 转换为字符串并生成哈希
        config_str = str(sorted(key_info.items()))
        return hashlib.md5(config_str.encode()).hexdigest()
        
    except Exception:
        import time
        import random
        timestamp = int(time.time() * 1000000)
        random_suffix = random.randint(1000, 9999)
        return f"fallback_{timestamp}_{random_suffix}"


def calculate_portfolio_metrics(returns: List[float]) -> Dict[str, float]:
    """计算组合绩效指标"""
    try:
        if not returns:
            return {}
        
        returns_series = pd.Series(returns)
        
        # 基础指标
        total_return = (1 + returns_series).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns_series.std() * np.sqrt(252)
        
        # 最大回撤
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 夏普比率
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 胜率
        win_rate = (returns_series > 0).sum() / len(returns_series)
        
        return {
            "total_return": float(total_return),
            "annual_return": float(annual_return),
            "volatility": float(volatility),
            "max_drawdown": float(abs(max_drawdown)),
            "sharpe_ratio": float(sharpe_ratio),
            "win_rate": float(win_rate)
        }
        
    except Exception as e:
        logger.error(f"计算组合指标失败: {e}")
        return {}


def normalize_weights(weights: List[float]) -> List[float]:
    """归一化权重"""
    try:
        total = sum(weights)
        if total <= 0:
            return [1.0 / len(weights)] * len(weights)
        return [w / total for w in weights]
    except:
        return [1.0 / len(weights)] * len(weights) if weights else []


def validate_etf_allocation_sum(allocations: List[Dict[str, Any]]) -> bool:
    """验证ETF配置权重总和"""
    try:
        total_weight = sum(alloc.get("weight", 0) for alloc in allocations)
        return abs(total_weight - 100) < 0.01  # 允许0.01%的误差
    except:
        return False


def clean_text(text: str) -> str:
    """清理文本"""
    if not text:
        return ""
    
    # 移除多余空白
    text = " ".join(text.split())
    
    # 移除特殊字符
    import re
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）。，！？；：]', '', text)
    
    return text.strip()


def extract_numbers_from_text(text: str) -> List[float]:
    """从文本中提取数字"""
    import re
    
    # 匹配数字（包括小数）
    pattern = r'\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    try:
        return [float(match) for match in matches]
    except:
        return []


def parse_investment_amount(text: str) -> Optional[float]:
    """解析投资金额"""
    try:
        numbers = extract_numbers_from_text(text)
        if not numbers:
            return None
        
        amount = numbers[0]
        
        # 处理单位
        if "万" in text:
            amount *= 10000
        elif "亿" in text:
            amount *= 100000000
        elif "千" in text:
            amount *= 1000
        
        return amount
        
    except:
        return None


def parse_percentage(text: str) -> Optional[float]:
    """解析百分比"""
    try:
        numbers = extract_numbers_from_text(text)
        if not numbers:
            return None
        
        percentage = numbers[0]
        
        # 如果数字大于1且文本中包含%，可能是百分比形式
        if "%" in text and percentage > 1:
            return percentage
        elif percentage <= 1:
            return percentage * 100
        else:
            return percentage
            
    except:
        return None


def create_error_response(error_message: str, error_code: str = None) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "success": False,
        "error": error_message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }


def create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建成功响应"""
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并字典"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制数值范围"""
    return max(min_val, min(max_val, value))
