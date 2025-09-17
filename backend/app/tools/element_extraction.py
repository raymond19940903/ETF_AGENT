"""投资要素提取工具"""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
import json
import re
import logging

logger = logging.getLogger(__name__)


class ElementExtractionInput(BaseModel):
    """投资要素提取工具输入"""
    conversation_content: str = Field(description="对话内容")
    context_info: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    previous_elements: Dict[str, Any] = Field(default_factory=dict, description="之前提取的要素")


class ElementExtractionTool(BaseTool):
    """投资要素提取工具"""
    name = "element_extraction_tool"
    description = "从对话中提取投资要素和偏好信息"
    args_schema = ElementExtractionInput
    
    def __init__(self, llm: LLM):
        super().__init__()
        self.llm = llm
    
    def _run(self, conversation_content: str, context_info: Dict[str, Any] = None, 
             previous_elements: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行投资要素提取"""
        try:
            if context_info is None:
                context_info = {}
            if previous_elements is None:
                previous_elements = {}
            
            # 构建提示词
            prompt = self._build_extraction_prompt(
                conversation_content, context_info, previous_elements
            )
            
            # 调用LLM进行要素提取
            response = self.llm(prompt)
            
            # 解析LLM响应
            extracted_elements = self._parse_llm_response(response)
            
            # 合并之前的要素
            final_elements = self._merge_elements(previous_elements, extracted_elements)
            
            # 计算置信度
            confidence_score = self._calculate_confidence(final_elements, conversation_content)
            
            result = {
                "success": True,
                "extracted_elements": final_elements,
                "confidence_score": confidence_score,
                "extraction_source": "llm_analysis",
                "raw_response": response
            }
            
            logger.info(f"投资要素提取成功，置信度: {confidence_score}")
            return result
            
        except Exception as e:
            logger.error(f"投资要素提取失败: {e}")
            
            # 使用规则提取作为备用方案
            fallback_elements = self._rule_based_extraction(conversation_content, previous_elements)
            
            return {
                "success": False,
                "error": str(e),
                "extracted_elements": fallback_elements,
                "confidence_score": 0.3,
                "extraction_source": "rule_based_fallback"
            }
    
    async def _arun(self, conversation_content: str, context_info: Dict[str, Any] = None,
                   previous_elements: Dict[str, Any] = None) -> Dict[str, Any]:
        """异步执行投资要素提取"""
        return self._run(conversation_content, context_info, previous_elements)
    
    def _build_extraction_prompt(self, content: str, context: Dict[str, Any], 
                               previous: Dict[str, Any]) -> str:
        """构建要素提取提示词"""
        prompt = f"""
你是一个专业的投资顾问助手，需要从用户对话中提取关键的投资要素信息。

对话内容：
{content}

上下文信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

之前已提取的要素：
{json.dumps(previous, ensure_ascii=False, indent=2)}

请从对话中提取以下投资要素，如果某个要素在对话中没有提到，则保持为null：

1. 偏好资产类别/板块 (preferred_asset_classes): 用户提到的感兴趣的资产类别或行业板块
2. 风险承受能力 (risk_tolerance): 用户的风险偏好（保守/稳健/积极/激进）
3. 目标收益率 (target_return): 用户期望的收益率（百分比）
4. 最大回撤容忍度 (max_drawdown_tolerance): 用户能接受的最大回撤（百分比）
5. 投资金额 (investment_amount): 用户计划投资的金额
6. 投资期限 (investment_horizon): 投资时间长度（短期/中期/长期）
7. 禁忌资产 (forbidden_assets): 用户明确表示不想投资的资产类别或行业
8. 特殊偏好 (special_preferences): 其他特殊要求或偏好
9. 再平衡频率 (rebalance_frequency): 用户偏好的调仓频率
10. 流动性需求 (liquidity_needs): 对资金流动性的要求

请以JSON格式返回提取结果，格式如下：
{{
    "preferred_asset_classes": ["科技", "医药"],
    "risk_tolerance": "稳健",
    "target_return": 8.5,
    "max_drawdown_tolerance": 15.0,
    "investment_amount": 100000,
    "investment_horizon": "中期",
    "forbidden_assets": ["房地产"],
    "special_preferences": ["ESG投资", "低费率"],
    "rebalance_frequency": "季度",
    "liquidity_needs": "中等"
}}

注意：
1. 只提取对话中明确提到的信息
2. 数值型数据请转换为数字格式
3. 如果用户修改了之前的偏好，以最新的为准
4. 保持JSON格式的严格性
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                elements = json.loads(json_str)
                return elements
            else:
                # 如果没有找到JSON，尝试解析结构化文本
                return self._parse_structured_text(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            return self._parse_structured_text(response)
    
    def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        """解析结构化文本"""
        elements = {}
        
        # 定义要素匹配模式
        patterns = {
            "preferred_asset_classes": r"偏好资产类别[：:]\s*(.+)",
            "risk_tolerance": r"风险承受能力[：:]\s*(.+)",
            "target_return": r"目标收益率[：:]\s*(\d+\.?\d*)%?",
            "max_drawdown_tolerance": r"最大回撤[：:]\s*(\d+\.?\d*)%?",
            "investment_amount": r"投资金额[：:]\s*(\d+)",
            "investment_horizon": r"投资期限[：:]\s*(.+)",
            "forbidden_assets": r"禁忌资产[：:]\s*(.+)",
            "special_preferences": r"特殊偏好[：:]\s*(.+)",
            "rebalance_frequency": r"再平衡频率[：:]\s*(.+)",
            "liquidity_needs": r"流动性需求[：:]\s*(.+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                
                # 处理不同类型的数据
                if key in ["target_return", "max_drawdown_tolerance"]:
                    try:
                        elements[key] = float(value)
                    except ValueError:
                        elements[key] = value
                elif key == "investment_amount":
                    try:
                        elements[key] = int(value)
                    except ValueError:
                        elements[key] = value
                elif key in ["preferred_asset_classes", "forbidden_assets", "special_preferences"]:
                    # 处理列表类型
                    elements[key] = [item.strip() for item in value.split("、") if item.strip()]
                else:
                    elements[key] = value
        
        return elements
    
    def _merge_elements(self, previous: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """合并投资要素"""
        merged = previous.copy()
        
        for key, value in new.items():
            if value is not None and value != "":
                if isinstance(value, list) and key in merged and isinstance(merged[key], list):
                    # 合并列表，去重
                    merged[key] = list(set(merged[key] + value))
                else:
                    # 新值覆盖旧值
                    merged[key] = value
        
        return merged
    
    def _calculate_confidence(self, elements: Dict[str, Any], content: str) -> float:
        """计算提取置信度"""
        try:
            # 基础置信度
            base_confidence = 0.5
            
            # 根据提取要素数量调整
            non_null_elements = sum(1 for v in elements.values() if v is not None and v != "")
            element_bonus = min(non_null_elements * 0.05, 0.3)
            
            # 根据对话长度调整
            content_length = len(content)
            if content_length > 100:
                length_bonus = min((content_length - 100) / 1000 * 0.1, 0.1)
            else:
                length_bonus = -0.1
            
            # 根据关键词匹配调整
            investment_keywords = ["投资", "收益", "风险", "回撤", "资产", "配置", "ETF"]
            keyword_count = sum(1 for keyword in investment_keywords if keyword in content)
            keyword_bonus = min(keyword_count * 0.02, 0.1)
            
            final_confidence = base_confidence + element_bonus + length_bonus + keyword_bonus
            return min(max(final_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"计算置信度失败: {e}")
            return 0.5
    
    def _rule_based_extraction(self, content: str, previous: Dict[str, Any]) -> Dict[str, Any]:
        """基于规则的要素提取（备用方案）"""
        elements = previous.copy()
        
        try:
            # 风险偏好关键词
            risk_keywords = {
                "保守": ["保守", "稳定", "低风险", "安全"],
                "稳健": ["稳健", "平衡", "中等风险"],
                "积极": ["积极", "成长", "高收益"],
                "激进": ["激进", "高风险", "投机"]
            }
            
            for risk_level, keywords in risk_keywords.items():
                if any(keyword in content for keyword in keywords):
                    elements["risk_tolerance"] = risk_level
                    break
            
            # 提取数字信息
            import re
            
            # 收益率
            return_match = re.search(r'(\d+\.?\d*)%.*收益', content)
            if return_match:
                elements["target_return"] = float(return_match.group(1))
            
            # 投资金额
            amount_match = re.search(r'(\d+)万', content)
            if amount_match:
                elements["investment_amount"] = int(amount_match.group(1)) * 10000
            
            # 资产类别
            asset_keywords = ["科技", "医药", "消费", "金融", "地产", "新能源", "军工"]
            mentioned_assets = [asset for asset in asset_keywords if asset in content]
            if mentioned_assets:
                elements["preferred_asset_classes"] = mentioned_assets
            
            return elements
            
        except Exception as e:
            logger.error(f"规则提取失败: {e}")
            return elements
