"""格式化工具函数"""
from typing import Union, Optional
from datetime import datetime, date
import locale

# 设置中文locale（如果可用）
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    pass


def format_percentage(value: Union[float, int], decimals: int = 2) -> str:
    """格式化百分比"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_currency(amount: Union[float, int], currency: str = "CNY") -> str:
    """格式化货币"""
    if amount is None:
        return "N/A"
    
    if currency == "CNY":
        if amount >= 100000000:  # 1亿
            return f"¥{amount/100000000:.2f}亿"
        elif amount >= 10000:  # 1万
            return f"¥{amount/10000:.2f}万"
        else:
            return f"¥{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def format_number(value: Union[float, int], decimals: int = 2) -> str:
    """格式化数字"""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_large_number(value: Union[float, int]) -> str:
    """格式化大数字"""
    if value is None:
        return "N/A"
    
    if value >= 100000000:  # 1亿
        return f"{value/100000000:.2f}亿"
    elif value >= 10000:  # 1万
        return f"{value/10000:.2f}万"
    else:
        return f"{value:,.0f}"


def format_date(date_value: Union[str, datetime, date], format_type: str = "date") -> str:
    """格式化日期"""
    if date_value is None:
        return "N/A"
    
    if isinstance(date_value, str):
        try:
            # 尝试解析ISO格式
            if 'T' in date_value:
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
        except:
            return date_value
    elif isinstance(date_value, date):
        date_obj = datetime.combine(date_value, datetime.min.time())
    else:
        date_obj = date_value
    
    if format_type == "date":
        return date_obj.strftime('%Y-%m-%d')
    elif format_type == "datetime":
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    elif format_type == "time":
        return date_obj.strftime('%H:%M:%S')
    elif format_type == "chinese_date":
        return date_obj.strftime('%Y年%m月%d日')
    elif format_type == "chinese_datetime":
        return date_obj.strftime('%Y年%m月%d日 %H:%M')
    else:
        return date_obj.strftime('%Y-%m-%d')


def format_risk_level(risk_level: str) -> str:
    """格式化风险等级"""
    risk_map = {
        "conservative": "保守",
        "balanced": "稳健", 
        "aggressive": "积极",
        "speculative": "激进"
    }
    return risk_map.get(risk_level.lower(), risk_level)


def format_rebalance_frequency(frequency: str) -> str:
    """格式化再平衡频率"""
    frequency_map = {
        "monthly": "月度",
        "quarterly": "季度",
        "semi_annually": "半年度",
        "annually": "年度"
    }
    return frequency_map.get(frequency.lower(), frequency)


def format_etf_code(etf_code: str) -> str:
    """格式化ETF代码"""
    if not etf_code:
        return "N/A"
    
    # 确保代码格式正确
    if len(etf_code) == 6 and etf_code.isdigit():
        # 根据代码判断交易所
        if etf_code.startswith(('50', '51', '52', '56', '58')):
            return f"{etf_code}.SH"
        else:
            return f"{etf_code}.SZ"
    
    return etf_code.upper()


def format_asset_class(asset_class: str) -> str:
    """格式化资产类别"""
    if not asset_class:
        return "其他"
    
    asset_map = {
        "equity": "股票",
        "bond": "债券", 
        "commodity": "商品",
        "real_estate": "房地产",
        "money_market": "货币市场"
    }
    
    for eng, chn in asset_map.items():
        if eng.lower() in asset_class.lower():
            return chn
    
    return asset_class


def format_strategy_status(status: str) -> str:
    """格式化策略状态"""
    status_map = {
        "active": "活跃",
        "inactive": "非活跃",
        "deleted": "已删除",
        "draft": "草稿"
    }
    return status_map.get(status.lower(), status)


def format_performance_metric(metric_name: str, value: Union[float, int], 
                            unit: str = "") -> str:
    """格式化绩效指标"""
    if value is None:
        return "N/A"
    
    if metric_name in ["return", "volatility", "drawdown"]:
        return format_percentage(value)
    elif metric_name in ["sharpe_ratio", "information_ratio"]:
        return f"{value:.2f}"
    elif metric_name == "win_rate":
        return format_percentage(value)
    else:
        return f"{value:.2f}{unit}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """截断文本"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
