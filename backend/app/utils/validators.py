"""验证工具函数"""
import re
from typing import List, Dict, Any


def validate_etf_code(etf_code: str) -> bool:
    """验证ETF代码格式"""
    # ETF代码格式：6位数字.SH或.SZ
    pattern = r'^\d{6}\.(SH|SZ)$'
    return bool(re.match(pattern, etf_code))


def validate_phone_number(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_investment_amount(amount: float) -> Dict[str, Any]:
    """验证投资金额"""
    result = {"valid": True, "message": ""}
    
    if amount <= 0:
        result = {"valid": False, "message": "投资金额必须大于0"}
    elif amount < 1000:
        result = {"valid": False, "message": "投资金额不能少于1000元"}
    elif amount > 100000000:  # 1亿
        result = {"valid": False, "message": "投资金额不能超过1亿元"}
    
    return result


def validate_risk_level(risk_level: str) -> bool:
    """验证风险等级"""
    valid_levels = ["保守", "稳健", "积极", "激进"]
    return risk_level in valid_levels


def validate_target_return(target_return: float) -> Dict[str, Any]:
    """验证目标收益率"""
    result = {"valid": True, "message": ""}
    
    if target_return < 0:
        result = {"valid": False, "message": "目标收益率不能为负数"}
    elif target_return > 50:
        result = {"valid": False, "message": "目标收益率不能超过50%"}
    elif target_return > 30:
        result = {"valid": True, "message": "目标收益率较高，请注意风险"}
    
    return result


def validate_max_drawdown(max_drawdown: float) -> Dict[str, Any]:
    """验证最大回撤"""
    result = {"valid": True, "message": ""}
    
    if max_drawdown < 0:
        result = {"valid": False, "message": "最大回撤不能为负数"}
    elif max_drawdown > 50:
        result = {"valid": False, "message": "最大回撤不能超过50%"}
    elif max_drawdown < 5:
        result = {"valid": True, "message": "最大回撤设置较低，可能限制收益潜力"}
    
    return result


def validate_etf_allocations(allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证ETF配置"""
    result = {"valid": True, "message": "", "warnings": []}
    
    if not allocations:
        return {"valid": False, "message": "ETF配置不能为空"}
    
    # 检查权重总和
    total_weight = sum(alloc.get("weight", 0) for alloc in allocations)
    if abs(total_weight - 100) > 0.01:
        result = {"valid": False, "message": f"ETF权重总和必须为100%，当前为{total_weight}%"}
        return result
    
    # 检查单个ETF权重
    for i, allocation in enumerate(allocations):
        weight = allocation.get("weight", 0)
        etf_code = allocation.get("etf_code", "")
        
        if not validate_etf_code(etf_code):
            result = {"valid": False, "message": f"第{i+1}个ETF代码格式不正确: {etf_code}"}
            return result
        
        if weight < 0:
            result = {"valid": False, "message": f"第{i+1}个ETF权重不能为负数"}
            return result
        
        if weight > 50:
            result["warnings"].append(f"{etf_code}权重过高({weight}%)，建议不超过50%")
        
        if weight < 1 and weight > 0:
            result["warnings"].append(f"{etf_code}权重过低({weight}%)，可能不具备投资意义")
    
    # 检查ETF数量
    if len(allocations) > 20:
        result["warnings"].append("ETF数量过多，可能导致过度分散")
    elif len(allocations) < 3:
        result["warnings"].append("ETF数量过少，分散化效果有限")
    
    return result


def validate_investment_elements(elements: Dict[str, Any]) -> Dict[str, Any]:
    """验证投资要素"""
    result = {"valid": True, "message": "", "missing_elements": []}
    
    required_elements = {
        "risk_tolerance": "风险承受能力",
        "target_return": "目标收益率",
        "investment_amount": "投资金额"
    }
    
    for key, name in required_elements.items():
        if not elements.get(key):
            result["missing_elements"].append(name)
    
    if result["missing_elements"]:
        result["valid"] = False
        result["message"] = f"缺少必要信息: {', '.join(result['missing_elements'])}"
    
    # 验证具体字段
    if elements.get("target_return"):
        target_validation = validate_target_return(elements["target_return"])
        if not target_validation["valid"]:
            result["valid"] = False
            result["message"] = target_validation["message"]
    
    if elements.get("investment_amount"):
        amount_validation = validate_investment_amount(elements["investment_amount"])
        if not amount_validation["valid"]:
            result["valid"] = False
            result["message"] = amount_validation["message"]
    
    if elements.get("risk_tolerance"):
        if not validate_risk_level(elements["risk_tolerance"]):
            result["valid"] = False
            result["message"] = "风险等级不正确"
    
    return result


def validate_strategy_constraints(constraints: Dict[str, Any]) -> Dict[str, Any]:
    """验证策略约束条件"""
    result = {"valid": True, "message": "", "warnings": []}
    
    # 验证最小市值约束
    if constraints.get("min_market_cap"):
        min_cap = constraints["min_market_cap"]
        if min_cap < 0:
            result = {"valid": False, "message": "最小市值约束不能为负数"}
        elif min_cap > 100000000000:  # 1000亿
            result["warnings"].append("最小市值约束过高，可能筛选出的ETF过少")
    
    # 验证最大费用率约束
    if constraints.get("max_expense_ratio"):
        max_expense = constraints["max_expense_ratio"]
        if max_expense < 0:
            result = {"valid": False, "message": "最大费用率约束不能为负数"}
        elif max_expense > 3.0:
            result["warnings"].append("最大费用率约束过高")
        elif max_expense < 0.5:
            result["warnings"].append("最大费用率约束过低，可能筛选出的ETF过少")
    
    # 验证最大ETF数量约束
    if constraints.get("max_etf_count"):
        max_count = constraints["max_etf_count"]
        if max_count < 1:
            result = {"valid": False, "message": "最大ETF数量不能少于1"}
        elif max_count > 30:
            result["warnings"].append("ETF数量过多，可能导致过度分散")
        elif max_count < 3:
            result["warnings"].append("ETF数量过少，分散化效果有限")
    
    return result
