"""内容安全检查器

对大模型生成的内容进行安全性检查和合规性验证。
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class ContentSafetyChecker:
    """内容安全检查器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "data/safety_config/content_safety.yaml"
        self.config = self._load_config()
        self.blocked_keywords = self._load_keywords()
        self.compliance_templates = self._load_compliance_templates()
    
    def _load_config(self) -> Dict:
        """加载安全配置"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            logger.warning(f"加载安全配置失败，使用默认配置: {e}")
            return self._get_default_config()
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """加载敏感词库"""
        keywords = {}
        keywords_dir = Path("data/safety_config/keywords")
        
        if not keywords_dir.exists():
            return self._get_default_keywords()
        
        try:
            for keyword_file in keywords_dir.glob("*.txt"):
                category = keyword_file.stem
                with open(keyword_file, 'r', encoding='utf-8') as f:
                    keywords[category] = [
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    ]
        except Exception as e:
            logger.warning(f"加载敏感词库失败，使用默认词库: {e}")
            return self._get_default_keywords()
        
        return keywords
    
    def _load_compliance_templates(self) -> Dict[str, str]:
        """加载合规模板"""
        try:
            templates_file = Path("data/safety_config/compliance_templates/disclaimers.yaml")
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_templates()
        except Exception as e:
            logger.warning(f"加载合规模板失败，使用默认模板: {e}")
            return self._get_default_templates()
    
    def check_content_safety(self, content: str, content_type: str = "general") -> Dict[str, Any]:
        """检查内容安全性"""
        
        violations = []
        risk_level = "low"
        
        try:
            # 1. 关键词检查
            keyword_violations = self._check_keywords(content)
            violations.extend(keyword_violations)
            
            # 2. 投资建议合规性检查
            if content_type == "investment_advice":
                compliance_violations = self._check_investment_compliance(content)
                violations.extend(compliance_violations)
            
            # 3. 确定风险等级
            if violations:
                severity_levels = [v.get("severity", "low") for v in violations]
                if "high" in severity_levels:
                    risk_level = "high"
                elif "medium" in severity_levels:
                    risk_level = "medium"
            
            # 4. 生成处理后的内容
            processed_content = self._process_content(content, violations, content_type)
            
            return {
                "is_safe": len([v for v in violations if v.get("severity") in ["high", "critical"]]) == 0,
                "risk_level": risk_level,
                "violations": violations,
                "processed_content": processed_content,
                "suggestions": self._generate_suggestions(violations),
                "safety_score": self._calculate_safety_score(violations)
            }
            
        except Exception as e:
            logger.error(f"内容安全检查失败: {e}")
            return self._get_safe_fallback_result(content)
    
    def _check_keywords(self, content: str) -> List[Dict]:
        """检查敏感词"""
        violations = []
        
        for category, keywords in self.blocked_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    severity = self._get_keyword_severity(category)
                    violations.append({
                        "type": "keyword_violation",
                        "category": category,
                        "keyword": keyword,
                        "severity": severity,
                        "position": content.find(keyword)
                    })
        
        return violations
    
    def _check_investment_compliance(self, content: str) -> List[Dict]:
        """检查投资建议合规性"""
        violations = []
        
        # 检查保证性表述
        guarantee_patterns = [
            r"保证.*收益", r"稳赚.*", r"无风险.*收益", r"一定.*赚钱",
            r"必然.*上涨", r"绝对.*安全", r"零风险"
        ]
        
        for pattern in guarantee_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                violations.append({
                    "type": "compliance_violation",
                    "category": "guarantee_statement",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "severity": "high",
                    "position": match.start()
                })
        
        # 检查风险提示
        risk_keywords = ["风险", "谨慎", "可能", "建议"]
        if not any(keyword in content for keyword in risk_keywords):
            violations.append({
                "type": "compliance_violation",
                "category": "missing_risk_warning",
                "severity": "medium",
                "suggestion": "建议添加风险提示"
            })
        
        return violations
    
    def _process_content(self, content: str, violations: List[Dict], content_type: str) -> str:
        """处理内容，添加合规声明"""
        processed = content
        
        # 移除违规内容
        for violation in violations:
            if violation.get("severity") == "high" and violation.get("matched_text"):
                processed = processed.replace(
                    violation["matched_text"],
                    "[已移除不当内容]"
                )
        
        # 添加风险提示
        if content_type in ["investment_advice", "strategy_recommendation"]:
            risk_warning = "【风险提示】投资有风险，入市需谨慎。"
            if risk_warning not in processed:
                processed = f"{risk_warning}\n\n{processed}"
        
        # 添加免责声明
        if content_type in ["investment_advice", "strategy_recommendation", "market_analysis"]:
            disclaimer = self._get_disclaimer(content_type)
            if disclaimer not in processed:
                processed += f"\n\n{disclaimer}"
        
        return processed
    
    def _get_disclaimer(self, content_type: str) -> str:
        """获取免责声明"""
        
        disclaimers = {
            "investment_advice": (
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
            )
        }
        
        return disclaimers.get(content_type, disclaimers["investment_advice"])
    
    def _generate_suggestions(self, violations: List[Dict]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for violation in violations:
            if violation["type"] == "keyword_violation":
                suggestions.append(f"请避免使用敏感词汇：{violation['keyword']}")
            elif violation["category"] == "guarantee_statement":
                suggestions.append("请避免使用保证性表述，改用'可能'、'预期'等词汇")
            elif violation["category"] == "missing_risk_warning":
                suggestions.append("请添加适当的风险提示")
        
        return list(set(suggestions))
    
    def _calculate_safety_score(self, violations: List[Dict]) -> float:
        """计算安全评分（0-1）"""
        
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
    
    def _get_keyword_severity(self, category: str) -> str:
        """获取关键词严重程度"""
        
        severity_mapping = {
            "political": "high",
            "nsfw": "high",
            "financial_violations": "medium",
            "discrimination": "high"
        }
        
        return severity_mapping.get(category, "low")
    
    def _get_default_config(self) -> Dict:
        """获取默认安全配置"""
        return {
            "content_safety": {
                "keyword_filters": {
                    "political_sensitive": {
                        "enabled": True,
                        "severity": "high",
                        "action": "block"
                    },
                    "nsfw_content": {
                        "enabled": True,
                        "severity": "high",
                        "action": "block"
                    },
                    "financial_violations": {
                        "enabled": True,
                        "severity": "medium",
                        "action": "warn_and_modify"
                    }
                },
                "review_settings": {
                    "auto_review_threshold": 0.8,
                    "human_review_threshold": 0.6
                }
            }
        }
    
    def _get_default_keywords(self) -> Dict[str, List[str]]:
        """获取默认敏感词库"""
        return {
            "political": ["政治敏感词汇示例"],
            "nsfw": ["不适宜内容示例"],
            "financial_violations": ["保证收益", "稳赚不赔", "无风险高收益", "内幕消息"]
        }
    
    def _get_default_templates(self) -> Dict[str, str]:
        """获取默认合规模板"""
        return {
            "investment_advice": (
                "【免责声明】本内容仅为投资策略建议，不构成具体的投资推荐。"
                "投资有风险，入市需谨慎。"
            )
        }
    
    def _get_safe_fallback_result(self, content: str) -> Dict[str, Any]:
        """获取安全的备用结果"""
        return {
            "is_safe": False,
            "risk_level": "high",
            "violations": [{"type": "system_error", "severity": "high"}],
            "processed_content": "抱歉，内容处理出现问题，请稍后重试。",
            "suggestions": ["请重新输入内容"],
            "safety_score": 0.0
        }


def check_content_safety(content: str, content_type: str = "general") -> Dict[str, Any]:
    """便捷函数：检查内容安全性"""
    checker = ContentSafetyChecker()
    return checker.check_content_safety(content, content_type)


if __name__ == "__main__":
    # 测试代码
    test_content = "我推荐这个ETF，保证你能赚钱，绝对无风险。"
    result = check_content_safety(test_content, "investment_advice")
    
    print(f"安全检查结果: {result['is_safe']}")
    print(f"风险等级: {result['risk_level']}")
    print(f"违规项: {len(result['violations'])}")
    print(f"处理后内容: {result['processed_content']}")
