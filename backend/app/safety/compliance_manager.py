"""合规性管理器

管理投资建议的合规性检查和免责声明添加。
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComplianceManager:
    """合规性管理器"""
    
    def __init__(self):
        self.guarantee_patterns = [
            r"保证.*收益", r"稳赚.*", r"无风险.*收益", r"一定.*赚钱",
            r"必然.*上涨", r"绝对.*安全", r"零风险", r"百分百.*", 
            r"确保.*盈利", r"肯定.*赚", r"包赚.*"
        ]
        
        self.misleading_patterns = [
            r"内幕.*消息", r"小道.*消息", r"独家.*消息",
            r"操纵.*市场", r"拉升.*股价", r"做庄.*"
        ]
        
        self.risk_keywords = [
            "风险", "谨慎", "可能", "建议", "仅供参考", "不保证",
            "历史业绩不代表未来", "投资需谨慎"
        ]
        
        self.disclaimers = {
            "investment_advice": (
                "【风险提示】投资有风险，入市需谨慎。\n"
                "【免责声明】本内容仅为投资策略建议，不构成具体的投资推荐。"
                "历史业绩不代表未来表现，请根据自身风险承受能力谨慎决策。"
            ),
            "market_analysis": (
                "【分析说明】以上市场分析基于公开信息和历史数据，"
                "不保证分析结论的准确性，市场情况可能发生变化。"
            ),
            "strategy_recommendation": (
                "【策略说明】本策略建议基于历史数据分析，"
                "实际投资效果可能与预期存在差异，请结合个人情况谨慎决策。"
            ),
            "backtest_results": (
                "【回测说明】回测结果基于历史数据计算，不代表未来实际表现。"
                "实际投资收益可能与回测结果存在差异。"
            )
        }
    
    def check_compliance(self, content: str, content_type: str = "general") -> Dict[str, Any]:
        """检查内容合规性"""
        
        violations = []
        
        try:
            # 1. 检查保证性表述
            guarantee_violations = self._check_guarantee_statements(content)
            violations.extend(guarantee_violations)
            
            # 2. 检查误导性内容
            misleading_violations = self._check_misleading_content(content)
            violations.extend(misleading_violations)
            
            # 3. 检查风险提示
            if content_type in ["investment_advice", "strategy_recommendation"]:
                risk_violations = self._check_risk_warnings(content)
                violations.extend(risk_violations)
            
            # 4. 检查绝对化表述
            absolute_violations = self._check_absolute_statements(content)
            violations.extend(absolute_violations)
            
            # 5. 计算合规性评分
            compliance_score = self._calculate_compliance_score(violations)
            
            return {
                "is_compliant": len([v for v in violations if v.get("severity") in ["high", "critical"]]) == 0,
                "compliance_score": compliance_score,
                "violations": violations,
                "required_disclaimers": self._get_required_disclaimers(content_type, violations),
                "suggestions": self._generate_compliance_suggestions(violations)
            }
            
        except Exception as e:
            logger.error(f"合规性检查失败: {e}")
            return self._get_safe_compliance_result()
    
    def _check_guarantee_statements(self, content: str) -> List[Dict]:
        """检查保证性表述"""
        violations = []
        
        for pattern in self.guarantee_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": "guarantee_statement",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.start(),
                    "severity": "high",
                    "description": "包含保证性表述，违反投资建议规范"
                })
        
        return violations
    
    def _check_misleading_content(self, content: str) -> List[Dict]:
        """检查误导性内容"""
        violations = []
        
        for pattern in self.misleading_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": "misleading_content",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.start(),
                    "severity": "critical",
                    "description": "包含误导性内容，可能涉及违法违规"
                })
        
        return violations
    
    def _check_risk_warnings(self, content: str) -> List[Dict]:
        """检查风险提示"""
        violations = []
        
        # 检查是否包含风险提示
        has_risk_warning = any(keyword in content for keyword in self.risk_keywords)
        
        if not has_risk_warning:
            violations.append({
                "type": "missing_risk_warning",
                "severity": "medium",
                "description": "缺少风险提示，建议添加相关表述"
            })
        
        return violations
    
    def _check_absolute_statements(self, content: str) -> List[Dict]:
        """检查绝对化表述"""
        violations = []
        
        absolute_patterns = [
            r"一定会.*", r"必然.*", r"绝对.*", r"永远.*",
            r"从不.*", r"总是.*", r"完全.*", r"百分之百.*"
        ]
        
        for pattern in absolute_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": "absolute_statement",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.start(),
                    "severity": "medium",
                    "description": "包含绝对化表述，建议使用更温和的表达"
                })
        
        return violations
    
    def _calculate_compliance_score(self, violations: List[Dict]) -> float:
        """计算合规性评分"""
        
        if not violations:
            return 1.0
        
        penalty = 0
        for violation in violations:
            severity = violation.get("severity", "low")
            if severity == "critical":
                penalty += 0.5
            elif severity == "high":
                penalty += 0.3
            elif severity == "medium":
                penalty += 0.1
            else:
                penalty += 0.05
        
        score = max(0, 1.0 - penalty)
        return round(score, 2)
    
    def _get_required_disclaimers(self, content_type: str, violations: List[Dict]) -> List[str]:
        """获取需要的免责声明"""
        required = []
        
        # 基于内容类型添加免责声明
        if content_type in self.disclaimers:
            required.append(self.disclaimers[content_type])
        
        # 基于违规类型添加特殊声明
        for violation in violations:
            if violation["type"] == "guarantee_statement":
                required.append("【特别提示】任何投资都存在风险，过往业绩不预示未来表现。")
            elif violation["type"] == "misleading_content":
                required.append("【合规声明】请以官方公开信息为准，谨防虚假信息。")
        
        return list(set(required))  # 去重
    
    def _generate_compliance_suggestions(self, violations: List[Dict]) -> List[str]:
        """生成合规建议"""
        suggestions = []
        
        violation_types = set(v["type"] for v in violations)
        
        if "guarantee_statement" in violation_types:
            suggestions.append("请避免使用保证性表述，改用'预期'、'可能'等词汇")
        
        if "misleading_content" in violation_types:
            suggestions.append("请确保信息来源可靠，避免传播未经证实的消息")
        
        if "missing_risk_warning" in violation_types:
            suggestions.append("请添加适当的风险提示和投资建议免责声明")
        
        if "absolute_statement" in violation_types:
            suggestions.append("请避免绝对化表述，使用更客观的表达方式")
        
        return suggestions
    
    def add_compliance_disclaimers(self, content: str, content_type: str) -> str:
        """添加合规免责声明"""
        
        processed_content = content
        
        # 添加对应的免责声明
        if content_type in self.disclaimers:
            disclaimer = self.disclaimers[content_type]
            if disclaimer not in processed_content:
                processed_content = f"{processed_content}\n\n{disclaimer}"
        
        return processed_content
    
    def _get_safe_compliance_result(self) -> Dict[str, Any]:
        """获取安全的合规检查结果"""
        return {
            "is_compliant": False,
            "compliance_score": 0.0,
            "violations": [{"type": "system_error", "severity": "high"}],
            "required_disclaimers": [self.disclaimers["investment_advice"]],
            "suggestions": ["系统检查异常，请重新输入内容"]
        }


# 全局合规管理器实例
compliance_manager = ComplianceManager()


def check_investment_compliance(content: str, content_type: str = "investment_advice") -> Dict[str, Any]:
    """便捷函数：检查投资建议合规性"""
    return compliance_manager.check_compliance(content, content_type)


def add_investment_disclaimers(content: str, content_type: str = "investment_advice") -> str:
    """便捷函数：添加投资免责声明"""
    return compliance_manager.add_compliance_disclaimers(content, content_type)


if __name__ == "__main__":
    # 测试代码
    test_content = "我保证这个策略一定能赚钱，绝对无风险。"
    
    result = check_investment_compliance(test_content)
    print(f"合规检查结果: {result['is_compliant']}")
    print(f"合规评分: {result['compliance_score']}")
    print(f"违规项数: {len(result['violations'])}")
    
    processed_content = add_investment_disclaimers(test_content)
    print(f"添加免责声明后: {processed_content}")
