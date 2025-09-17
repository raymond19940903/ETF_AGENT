"""策略生成工具"""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.data.etf_service import ETFService
from app.tools.base_tool import ETFBaseTool
import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StrategyGenerationInput(BaseModel):
    """策略生成工具输入"""
    investment_elements: Dict[str, Any] = Field(description="投资要素")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="约束条件")
    optimization_target: str = Field(default="sharpe_ratio", description="优化目标")


class StrategyGenerationTool(ETFBaseTool):
    """策略生成工具"""
    name = "strategy_generation_tool"
    description = "基于用户对话提取的投资要素生成ETF配置策略"
    args_schema = StrategyGenerationInput
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.etf_service = ETFService(db)
    
    def _run(self, investment_elements: Dict[str, Any], 
             constraints: Dict[str, Any] = None,
             optimization_target: str = "sharpe_ratio") -> Dict[str, Any]:
        """执行策略生成"""
        try:
            if constraints is None:
                constraints = {}
            
            # 1. 根据投资要素筛选ETF池
            etf_pool = self._build_etf_pool(investment_elements, constraints)
            
            if not etf_pool:
                return {
                    "success": False,
                    "error": "未找到符合条件的ETF产品",
                    "strategy": None
                }
            
            # 2. 生成资产配置权重
            allocation_weights = self._generate_allocation_weights(
                etf_pool, investment_elements, optimization_target
            )
            
            # 3. 构建策略配置
            strategy_config = self._build_strategy_config(
                etf_pool, allocation_weights, investment_elements
            )
            
            # 4. 生成投资理念说明
            investment_philosophy = self._generate_investment_philosophy(
                investment_elements, strategy_config
            )
            
            # 5. 估算策略性能指标
            performance_estimates = self._estimate_performance(
                strategy_config, investment_elements
            )
            
            result = {
                "success": True,
                "strategy": {
                    "name": self._generate_strategy_name(investment_elements),
                    "description": self._generate_strategy_description(investment_elements),
                    "investment_philosophy": investment_philosophy,
                    "etf_allocations": strategy_config["allocations"],
                    "asset_allocation": strategy_config["asset_summary"],
                    "risk_level": investment_elements.get("risk_tolerance", "稳健"),
                    "target_return": investment_elements.get("target_return"),
                    "max_drawdown": investment_elements.get("max_drawdown_tolerance"),
                    "investment_amount": investment_elements.get("investment_amount"),
                    "rebalance_frequency": investment_elements.get("rebalance_frequency", "季度"),
                    "performance_estimates": performance_estimates,
                    "constraints": constraints,
                    "generation_time": datetime.now().isoformat()
                },
                "etf_count": len(strategy_config["allocations"]),
                "total_allocation": sum(alloc["weight"] for alloc in strategy_config["allocations"])
            }
            
            logger.info(f"策略生成成功，包含 {len(strategy_config['allocations'])} 个ETF")
            return result
            
        except Exception as e:
            logger.error(f"策略生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": None
            }
    
    async def _arun(self, investment_elements: Dict[str, Any],
                   constraints: Dict[str, Any] = None,
                   optimization_target: str = "sharpe_ratio") -> Dict[str, Any]:
        """异步执行策略生成"""
        return self._run(investment_elements, constraints, optimization_target)
    
    async def _build_etf_pool(self, elements: Dict[str, Any], 
                             constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """构建ETF候选池"""
        try:
            etf_pool = []
            
            # 获取偏好资产类别的ETF
            preferred_assets = elements.get("preferred_asset_classes", [])
            forbidden_assets = elements.get("forbidden_assets", [])
            
            if preferred_assets:
                for asset_class in preferred_assets:
                    etfs = await self.etf_service.get_etf_list(
                        asset_class=asset_class, limit=10
                    )
                    etf_pool.extend(etfs)
            else:
                # 如果没有指定偏好，获取主要资产类别的代表性ETF
                major_assets = ["股票", "债券", "商品", "房地产"]
                for asset_class in major_assets:
                    etfs = await self.etf_service.get_etf_list(
                        asset_class=asset_class, limit=5
                    )
                    etf_pool.extend(etfs)
            
            # 过滤禁忌资产
            if forbidden_assets:
                etf_pool = [
                    etf for etf in etf_pool
                    if not any(forbidden in (etf.get("asset_class", "") + etf.get("sector", ""))
                              for forbidden in forbidden_assets)
                ]
            
            # 应用约束条件
            if constraints.get("min_market_cap"):
                etf_pool = [
                    etf for etf in etf_pool
                    if etf.get("market_cap", 0) >= constraints["min_market_cap"]
                ]
            
            if constraints.get("max_expense_ratio"):
                etf_pool = [
                    etf for etf in etf_pool
                    if etf.get("expense_ratio", 0) <= constraints["max_expense_ratio"]
                ]
            
            # 去重并限制数量
            unique_etfs = []
            seen_codes = set()
            for etf in etf_pool:
                if etf["code"] not in seen_codes:
                    unique_etfs.append(etf)
                    seen_codes.add(etf["code"])
            
            # 限制ETF数量，避免过度分散
            max_etfs = constraints.get("max_etf_count", 10)
            return unique_etfs[:max_etfs]
            
        except Exception as e:
            logger.error(f"构建ETF池失败: {e}")
            return []
    
    def _generate_allocation_weights(self, etf_pool: List[Dict[str, Any]], 
                                   elements: Dict[str, Any], 
                                   optimization_target: str) -> List[float]:
        """生成资产配置权重"""
        try:
            n_etfs = len(etf_pool)
            if n_etfs == 0:
                return []
            
            risk_tolerance = elements.get("risk_tolerance", "稳健")
            
            # 根据风险偏好调整配置策略
            if risk_tolerance == "保守":
                # 保守型：债券为主
                weights = self._conservative_allocation(etf_pool)
            elif risk_tolerance == "稳健":
                # 稳健型：股债平衡
                weights = self._balanced_allocation(etf_pool)
            elif risk_tolerance == "积极":
                # 积极型：股票为主
                weights = self._aggressive_allocation(etf_pool)
            elif risk_tolerance == "激进":
                # 激进型：高风险资产
                weights = self._speculative_allocation(etf_pool)
            else:
                # 默认均等权重
                weights = [1.0 / n_etfs] * n_etfs
            
            # 确保权重和为1
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            
            return weights
            
        except Exception as e:
            logger.error(f"生成配置权重失败: {e}")
            # 返回均等权重作为备用
            return [1.0 / len(etf_pool)] * len(etf_pool)
    
    def _conservative_allocation(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """保守型配置"""
        weights = []
        bond_weight = 0.7
        stock_weight = 0.25
        other_weight = 0.05
        
        bond_etfs = []
        stock_etfs = []
        other_etfs = []
        
        for i, etf in enumerate(etf_pool):
            asset_class = etf.get("asset_class", "").lower()
            if "债券" in asset_class or "bond" in asset_class:
                bond_etfs.append(i)
            elif "股票" in asset_class or "equity" in asset_class:
                stock_etfs.append(i)
            else:
                other_etfs.append(i)
        
        weights = [0.0] * len(etf_pool)
        
        # 分配债券权重
        if bond_etfs:
            bond_weight_each = bond_weight / len(bond_etfs)
            for i in bond_etfs:
                weights[i] = bond_weight_each
        
        # 分配股票权重
        if stock_etfs:
            stock_weight_each = stock_weight / len(stock_etfs)
            for i in stock_etfs:
                weights[i] = stock_weight_each
        
        # 分配其他资产权重
        if other_etfs:
            other_weight_each = other_weight / len(other_etfs)
            for i in other_etfs:
                weights[i] = other_weight_each
        
        # 如果某类资产不存在，平均分配给其他资产
        total_assigned = sum(weights)
        if total_assigned < 1.0:
            remaining = 1.0 - total_assigned
            non_zero_count = sum(1 for w in weights if w > 0)
            if non_zero_count > 0:
                additional = remaining / non_zero_count
                weights = [w + additional if w > 0 else w for w in weights]
        
        return weights
    
    def _balanced_allocation(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """稳健型配置"""
        # 股债 6:4 配置
        return self._asset_class_allocation(etf_pool, {"股票": 0.6, "债券": 0.4})
    
    def _aggressive_allocation(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """积极型配置"""
        # 股票为主配置
        return self._asset_class_allocation(etf_pool, {"股票": 0.8, "债券": 0.15, "其他": 0.05})
    
    def _speculative_allocation(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """激进型配置"""
        # 高风险资产配置
        return self._asset_class_allocation(etf_pool, {"股票": 0.9, "其他": 0.1})
    
    def _asset_class_allocation(self, etf_pool: List[Dict[str, Any]], 
                              target_allocation: Dict[str, float]) -> List[float]:
        """按资产类别分配权重"""
        weights = [0.0] * len(etf_pool)
        asset_groups = {}
        
        # 按资产类别分组
        for i, etf in enumerate(etf_pool):
            asset_class = etf.get("asset_class", "其他")
            for target_class in target_allocation.keys():
                if target_class in asset_class:
                    if target_class not in asset_groups:
                        asset_groups[target_class] = []
                    asset_groups[target_class].append(i)
                    break
            else:
                if "其他" not in asset_groups:
                    asset_groups["其他"] = []
                asset_groups["其他"].append(i)
        
        # 分配权重
        for asset_class, target_weight in target_allocation.items():
            if asset_class in asset_groups:
                etf_indices = asset_groups[asset_class]
                weight_per_etf = target_weight / len(etf_indices)
                for i in etf_indices:
                    weights[i] = weight_per_etf
        
        return weights
    
    def _build_strategy_config(self, etf_pool: List[Dict[str, Any]], 
                             weights: List[float], 
                             elements: Dict[str, Any]) -> Dict[str, Any]:
        """构建策略配置"""
        allocations = []
        asset_summary = {}
        
        for i, (etf, weight) in enumerate(zip(etf_pool, weights)):
            if weight > 0.01:  # 过滤小于1%的配置
                allocation = {
                    "etf_code": etf["code"],
                    "etf_name": etf["name"],
                    "weight": round(weight * 100, 2),  # 转换为百分比
                    "asset_class": etf.get("asset_class", ""),
                    "sector": etf.get("sector", ""),
                    "market_cap": etf.get("market_cap"),
                    "expense_ratio": etf.get("expense_ratio")
                }
                allocations.append(allocation)
                
                # 统计资产类别汇总
                asset_class = etf.get("asset_class", "其他")
                if asset_class not in asset_summary:
                    asset_summary[asset_class] = 0
                asset_summary[asset_class] += weight * 100
        
        # 四舍五入资产汇总
        for asset_class in asset_summary:
            asset_summary[asset_class] = round(asset_summary[asset_class], 2)
        
        return {
            "allocations": allocations,
            "asset_summary": asset_summary
        }
    
    def _generate_investment_philosophy(self, elements: Dict[str, Any], 
                                      strategy_config: Dict[str, Any]) -> str:
        """生成投资理念"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        target_return = elements.get("target_return")
        preferred_assets = elements.get("preferred_asset_classes", [])
        
        philosophy_parts = []
        
        # 基于风险偏好的理念
        risk_philosophy = {
            "保守": "本策略采用保守稳健的投资理念，以资本保值为主要目标，通过债券等低风险资产配置，力求在控制风险的前提下获得稳定收益。",
            "稳健": "本策略遵循稳健平衡的投资理念，通过股债合理配置，在风险与收益之间寻求平衡，追求长期稳定增长。",
            "积极": "本策略采用积极成长的投资理念，重点配置成长性资产，在可控风险范围内追求较高收益。",
            "激进": "本策略采用激进投资理念，重点配置高成长潜力资产，追求超额收益，适合风险承受能力强的投资者。"
        }
        
        philosophy_parts.append(risk_philosophy.get(risk_tolerance, risk_philosophy["稳健"]))
        
        # 基于偏好资产的理念
        if preferred_assets:
            asset_desc = "、".join(preferred_assets)
            philosophy_parts.append(f"策略重点关注{asset_desc}等领域的投资机会，把握行业发展趋势。")
        
        # 基于目标收益的理念
        if target_return:
            philosophy_parts.append(f"目标年化收益率为{target_return}%，通过科学的资产配置和定期再平衡来实现收益目标。")
        
        # 添加分散化投资理念
        etf_count = len(strategy_config["allocations"])
        philosophy_parts.append(f"通过{etf_count}只ETF的组合配置，实现充分的分散化投资，降低单一资产风险。")
        
        return " ".join(philosophy_parts)
    
    def _generate_strategy_name(self, elements: Dict[str, Any]) -> str:
        """生成策略名称"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        preferred_assets = elements.get("preferred_asset_classes", [])
        
        name_parts = []
        
        if preferred_assets:
            if len(preferred_assets) == 1:
                name_parts.append(preferred_assets[0])
            else:
                name_parts.append("多元")
        
        name_parts.append(risk_tolerance)
        name_parts.append("ETF配置策略")
        
        return "".join(name_parts)
    
    def _generate_strategy_description(self, elements: Dict[str, Any]) -> str:
        """生成策略描述"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        target_return = elements.get("target_return")
        investment_amount = elements.get("investment_amount")
        
        desc_parts = []
        desc_parts.append(f"这是一个{risk_tolerance}型的ETF资产配置策略")
        
        if target_return:
            desc_parts.append(f"目标年化收益率{target_return}%")
        
        if investment_amount:
            desc_parts.append(f"适合{investment_amount:,}元的投资规模")
        
        desc_parts.append("通过多元化ETF配置实现风险分散和收益优化")
        
        return "，".join(desc_parts) + "。"
    
    def _estimate_performance(self, strategy_config: Dict[str, Any], 
                            elements: Dict[str, Any]) -> Dict[str, Any]:
        """估算策略性能指标"""
        try:
            # 基于风险偏好估算性能指标
            risk_tolerance = elements.get("risk_tolerance", "稳健")
            
            performance_estimates = {
                "保守": {
                    "expected_annual_return": 5.5,
                    "expected_volatility": 8.0,
                    "expected_max_drawdown": 6.0,
                    "expected_sharpe_ratio": 0.6
                },
                "稳健": {
                    "expected_annual_return": 8.0,
                    "expected_volatility": 12.0,
                    "expected_max_drawdown": 10.0,
                    "expected_sharpe_ratio": 0.8
                },
                "积极": {
                    "expected_annual_return": 12.0,
                    "expected_volatility": 18.0,
                    "expected_max_drawdown": 15.0,
                    "expected_sharpe_ratio": 0.9
                },
                "激进": {
                    "expected_annual_return": 15.0,
                    "expected_volatility": 25.0,
                    "expected_max_drawdown": 25.0,
                    "expected_sharpe_ratio": 0.8
                }
            }
            
            base_estimates = performance_estimates.get(risk_tolerance, performance_estimates["稳健"])
            
            # 根据资产配置调整估算
            asset_summary = strategy_config.get("asset_summary", {})
            stock_ratio = asset_summary.get("股票", 0) / 100
            
            # 股票比例越高，收益和风险都相应调整
            return_adjustment = (stock_ratio - 0.6) * 2  # 基准股票比例60%
            volatility_adjustment = (stock_ratio - 0.6) * 3
            
            final_estimates = {
                "expected_annual_return": round(base_estimates["expected_annual_return"] + return_adjustment, 2),
                "expected_volatility": round(base_estimates["expected_volatility"] + volatility_adjustment, 2),
                "expected_max_drawdown": round(base_estimates["expected_max_drawdown"] + volatility_adjustment * 0.6, 2),
                "expected_sharpe_ratio": round(base_estimates["expected_sharpe_ratio"], 2),
                "confidence_level": 0.7  # 估算置信度
            }
            
            return final_estimates
            
        except Exception as e:
            logger.error(f"估算策略性能失败: {e}")
            return {
                "expected_annual_return": 8.0,
                "expected_volatility": 12.0,
                "expected_max_drawdown": 10.0,
                "expected_sharpe_ratio": 0.8,
                "confidence_level": 0.5
            }
