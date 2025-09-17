"""策略引擎核心"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sqlalchemy.orm import Session
from app.data.etf_service import ETFService
from app.cache.service import CacheService
import logging

logger = logging.getLogger(__name__)


class StrategyEngine:
    """策略引擎核心类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.etf_service = ETFService(db)
        self.cache_service = CacheService()
    
    async def generate_strategy(self, investment_elements: Dict[str, Any], 
                              constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成投资策略"""
        try:
            if constraints is None:
                constraints = {}
            
            # 1. 构建ETF候选池
            etf_pool = await self._build_etf_universe(investment_elements, constraints)
            
            if not etf_pool:
                return {
                    "success": False,
                    "error": "未找到符合条件的ETF产品",
                    "strategy": None
                }
            
            # 2. 计算最优权重
            optimal_weights = await self._optimize_portfolio(etf_pool, investment_elements)
            
            # 3. 构建策略配置
            strategy_config = self._build_strategy_config(etf_pool, optimal_weights, investment_elements)
            
            # 4. 生成策略说明
            strategy_description = self._generate_strategy_description(investment_elements, strategy_config)
            
            # 5. 估算策略性能
            performance_estimates = self._estimate_strategy_performance(strategy_config, investment_elements)
            
            result = {
                "success": True,
                "strategy": {
                    "name": self._generate_strategy_name(investment_elements),
                    "description": strategy_description,
                    "investment_philosophy": self._generate_investment_philosophy(investment_elements),
                    "etf_allocations": strategy_config["allocations"],
                    "asset_allocation": strategy_config["asset_summary"],
                    "risk_level": investment_elements.get("risk_tolerance", "稳健"),
                    "target_return": investment_elements.get("target_return"),
                    "max_drawdown": investment_elements.get("max_drawdown_tolerance"),
                    "investment_amount": investment_elements.get("investment_amount"),
                    "rebalance_frequency": investment_elements.get("rebalance_frequency", "季度"),
                    "performance_estimates": performance_estimates,
                    "constraints": constraints,
                    "generation_metadata": {
                        "etf_count": len(strategy_config["allocations"]),
                        "total_allocation": sum(alloc["weight"] for alloc in strategy_config["allocations"]),
                        "generation_time": pd.Timestamp.now().isoformat()
                    }
                }
            }
            
            logger.info(f"策略生成成功: {len(strategy_config['allocations'])} 个ETF")
            return result
            
        except Exception as e:
            logger.error(f"策略生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": None
            }
    
    async def optimize_strategy(self, current_strategy: Dict[str, Any], 
                              user_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """优化现有策略"""
        try:
            # 分析用户反馈
            feedback_analysis = self._analyze_feedback(user_feedback)
            
            # 应用优化调整
            optimized_strategy = self._apply_optimization(current_strategy, feedback_analysis)
            
            # 重新计算性能估算
            optimized_strategy["performance_estimates"] = self._estimate_strategy_performance(
                optimized_strategy, current_strategy.get("investment_elements", {})
            )
            
            # 生成变更说明
            changes_summary = self._summarize_changes(current_strategy, optimized_strategy)
            
            return {
                "success": True,
                "optimized_strategy": optimized_strategy,
                "changes_summary": changes_summary,
                "optimization_reason": feedback_analysis
            }
            
        except Exception as e:
            logger.error(f"策略优化失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "optimized_strategy": current_strategy
            }
    
    async def _build_etf_universe(self, elements: Dict[str, Any], 
                                constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """构建ETF投资域"""
        try:
            etf_pool = []
            
            # 获取偏好资产类别的ETF
            preferred_assets = elements.get("preferred_asset_classes", [])
            forbidden_assets = elements.get("forbidden_assets", [])
            
            if preferred_assets:
                for asset_class in preferred_assets:
                    etfs = await self.etf_service.get_etf_list(asset_class=asset_class, limit=15)
                    etf_pool.extend(etfs)
            else:
                # 默认获取主要资产类别的代表性ETF
                default_assets = ["股票", "债券", "商品", "REITS"]
                for asset_class in default_assets:
                    etfs = await self.etf_service.get_etf_list(asset_class=asset_class, limit=8)
                    etf_pool.extend(etfs)
            
            # 过滤禁忌资产
            if forbidden_assets:
                etf_pool = [
                    etf for etf in etf_pool
                    if not any(forbidden in (etf.get("asset_class", "") + etf.get("sector", ""))
                              for forbidden in forbidden_assets)
                ]
            
            # 应用约束条件
            etf_pool = self._apply_constraints(etf_pool, constraints)
            
            # 去重并排序
            unique_etfs = self._deduplicate_and_rank(etf_pool, elements)
            
            # 限制ETF数量
            max_etfs = constraints.get("max_etf_count", 12)
            return unique_etfs[:max_etfs]
            
        except Exception as e:
            logger.error(f"构建ETF投资域失败: {e}")
            return []
    
    async def _optimize_portfolio(self, etf_pool: List[Dict[str, Any]], 
                                elements: Dict[str, Any]) -> List[float]:
        """组合优化计算"""
        try:
            n_assets = len(etf_pool)
            if n_assets == 0:
                return []
            
            risk_tolerance = elements.get("risk_tolerance", "稳健")
            target_return = elements.get("target_return")
            
            # 根据风险偏好设置基础权重
            if risk_tolerance == "保守":
                weights = self._conservative_weights(etf_pool)
            elif risk_tolerance == "稳健":
                weights = self._balanced_weights(etf_pool)
            elif risk_tolerance == "积极":
                weights = self._aggressive_weights(etf_pool)
            elif risk_tolerance == "激进":
                weights = self._speculative_weights(etf_pool)
            else:
                weights = [1.0 / n_assets] * n_assets
            
            # 如果有目标收益率，进行优化调整
            if target_return:
                weights = self._adjust_weights_for_target_return(weights, etf_pool, target_return)
            
            # 确保权重和为1
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            
            return weights
            
        except Exception as e:
            logger.error(f"组合优化失败: {e}")
            # 返回等权重作为备用
            return [1.0 / len(etf_pool)] * len(etf_pool)
    
    def _conservative_weights(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """保守型权重分配"""
        weights = [0.0] * len(etf_pool)
        bond_indices = []
        stock_indices = []
        other_indices = []
        
        for i, etf in enumerate(etf_pool):
            asset_class = etf.get("asset_class", "").lower()
            if "债券" in asset_class or "bond" in asset_class:
                bond_indices.append(i)
            elif "股票" in asset_class or "equity" in asset_class:
                stock_indices.append(i)
            else:
                other_indices.append(i)
        
        # 债券70%，股票25%，其他5%
        if bond_indices:
            bond_weight = 0.7 / len(bond_indices)
            for i in bond_indices:
                weights[i] = bond_weight
        
        if stock_indices:
            stock_weight = 0.25 / len(stock_indices)
            for i in stock_indices:
                weights[i] = stock_weight
        
        if other_indices:
            other_weight = 0.05 / len(other_indices)
            for i in other_indices:
                weights[i] = other_weight
        
        return weights
    
    def _balanced_weights(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """平衡型权重分配"""
        # 股债6:4配置
        return self._asset_class_weights(etf_pool, {"股票": 0.6, "债券": 0.4})
    
    def _aggressive_weights(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """积极型权重分配"""
        # 股票80%，债券15%，其他5%
        return self._asset_class_weights(etf_pool, {"股票": 0.8, "债券": 0.15, "其他": 0.05})
    
    def _speculative_weights(self, etf_pool: List[Dict[str, Any]]) -> List[float]:
        """激进型权重分配"""
        # 股票90%，其他10%
        return self._asset_class_weights(etf_pool, {"股票": 0.9, "其他": 0.1})
    
    def _asset_class_weights(self, etf_pool: List[Dict[str, Any]], 
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
                if etf_indices:
                    weight_per_etf = target_weight / len(etf_indices)
                    for i in etf_indices:
                        weights[i] = weight_per_etf
        
        return weights
    
    def _apply_constraints(self, etf_pool: List[Dict[str, Any]], 
                         constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用投资约束"""
        filtered_pool = etf_pool.copy()
        
        # 最小市值约束
        if constraints.get("min_market_cap"):
            filtered_pool = [
                etf for etf in filtered_pool
                if etf.get("market_cap", 0) >= constraints["min_market_cap"]
            ]
        
        # 最大费用率约束
        if constraints.get("max_expense_ratio"):
            filtered_pool = [
                etf for etf in filtered_pool
                if etf.get("expense_ratio", 0) <= constraints["max_expense_ratio"]
            ]
        
        # 最小交易量约束
        if constraints.get("min_avg_volume"):
            # 这里需要从Wind获取交易量数据
            pass
        
        return filtered_pool
    
    def _deduplicate_and_rank(self, etf_pool: List[Dict[str, Any]], 
                            elements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """去重并排序ETF"""
        # 去重
        unique_etfs = []
        seen_codes = set()
        
        for etf in etf_pool:
            if etf["code"] not in seen_codes:
                unique_etfs.append(etf)
                seen_codes.add(etf["code"])
        
        # 排序：优先考虑市值、费用率、流动性
        def rank_score(etf):
            score = 0
            
            # 市值权重
            market_cap = etf.get("market_cap", 0)
            if market_cap > 10000000000:  # 100亿以上
                score += 3
            elif market_cap > 5000000000:  # 50亿以上
                score += 2
            elif market_cap > 1000000000:  # 10亿以上
                score += 1
            
            # 费用率权重（越低越好）
            expense_ratio = etf.get("expense_ratio", 1.0)
            if expense_ratio < 0.5:
                score += 2
            elif expense_ratio < 1.0:
                score += 1
            
            # 夏普比率权重
            sharpe_ratio = etf.get("sharpe_ratio", 0)
            if sharpe_ratio > 1.0:
                score += 2
            elif sharpe_ratio > 0.5:
                score += 1
            
            return score
        
        unique_etfs.sort(key=rank_score, reverse=True)
        return unique_etfs
    
    def _adjust_weights_for_target_return(self, base_weights: List[float], 
                                        etf_pool: List[Dict[str, Any]], 
                                        target_return: float) -> List[float]:
        """根据目标收益率调整权重"""
        try:
            # 简化的权重调整算法
            adjusted_weights = base_weights.copy()
            
            # 如果目标收益率较高，增加股票类ETF权重
            if target_return > 10:
                for i, etf in enumerate(etf_pool):
                    asset_class = etf.get("asset_class", "").lower()
                    if "股票" in asset_class:
                        adjusted_weights[i] *= 1.2  # 增加20%
                    elif "债券" in asset_class:
                        adjusted_weights[i] *= 0.8  # 减少20%
            
            # 如果目标收益率较低，增加债券类ETF权重
            elif target_return < 6:
                for i, etf in enumerate(etf_pool):
                    asset_class = etf.get("asset_class", "").lower()
                    if "债券" in asset_class:
                        adjusted_weights[i] *= 1.3  # 增加30%
                    elif "股票" in asset_class:
                        adjusted_weights[i] *= 0.7  # 减少30%
            
            return adjusted_weights
            
        except Exception as e:
            logger.error(f"权重调整失败: {e}")
            return base_weights
    
    def _build_strategy_config(self, etf_pool: List[Dict[str, Any]], 
                             weights: List[float], 
                             elements: Dict[str, Any]) -> Dict[str, Any]:
        """构建策略配置"""
        allocations = []
        asset_summary = {}
        
        for etf, weight in zip(etf_pool, weights):
            if weight > 0.01:  # 过滤小于1%的配置
                allocation = {
                    "etf_code": etf["code"],
                    "etf_name": etf["name"],
                    "weight": round(weight * 100, 2),
                    "asset_class": etf.get("asset_class", ""),
                    "sector": etf.get("sector", ""),
                    "market_cap": etf.get("market_cap"),
                    "expense_ratio": etf.get("expense_ratio"),
                    "nav": etf.get("nav")
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
    
    def _generate_strategy_name(self, elements: Dict[str, Any]) -> str:
        """生成策略名称"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        preferred_assets = elements.get("preferred_asset_classes", [])
        
        name_parts = []
        
        if preferred_assets:
            if len(preferred_assets) == 1:
                name_parts.append(preferred_assets[0])
            elif len(preferred_assets) == 2:
                name_parts.append("+".join(preferred_assets))
            else:
                name_parts.append("多元")
        
        name_parts.append(risk_tolerance)
        name_parts.append("ETF策略")
        
        return "".join(name_parts)
    
    def _generate_strategy_description(self, elements: Dict[str, Any], 
                                     config: Dict[str, Any]) -> str:
        """生成策略描述"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        target_return = elements.get("target_return")
        investment_amount = elements.get("investment_amount")
        etf_count = len(config["allocations"])
        
        desc_parts = []
        desc_parts.append(f"这是一个{risk_tolerance}型的ETF资产配置策略")
        
        if target_return:
            desc_parts.append(f"目标年化收益率{target_return}%")
        
        if investment_amount:
            desc_parts.append(f"适合{investment_amount:,.0f}元的投资规模")
        
        desc_parts.append(f"通过{etf_count}只ETF实现多元化配置")
        
        return "，".join(desc_parts) + "。"
    
    def _generate_investment_philosophy(self, elements: Dict[str, Any]) -> str:
        """生成投资理念"""
        risk_tolerance = elements.get("risk_tolerance", "稳健")
        preferred_assets = elements.get("preferred_asset_classes", [])
        target_return = elements.get("target_return")
        
        philosophy_templates = {
            "保守": "本策略采用保守稳健的投资理念，以资本保值为主要目标，通过债券等低风险资产配置，力求在控制风险的前提下获得稳定收益。",
            "稳健": "本策略遵循稳健平衡的投资理念，通过股债合理配置，在风险与收益之间寻求平衡，追求长期稳定增长。",
            "积极": "本策略采用积极成长的投资理念，重点配置成长性资产，在可控风险范围内追求较高收益。",
            "激进": "本策略采用激进投资理念，重点配置高成长潜力资产，追求超额收益，适合风险承受能力强的投资者。"
        }
        
        philosophy = philosophy_templates.get(risk_tolerance, philosophy_templates["稳健"])
        
        if preferred_assets:
            asset_desc = "、".join(preferred_assets)
            philosophy += f" 策略重点关注{asset_desc}等领域的投资机会。"
        
        if target_return:
            philosophy += f" 目标年化收益率为{target_return}%，通过科学的资产配置实现收益目标。"
        
        philosophy += " 策略强调分散化投资和动态再平衡，以降低单一资产风险。"
        
        return philosophy
    
    def _estimate_strategy_performance(self, strategy_config: Dict[str, Any], 
                                     elements: Dict[str, Any]) -> Dict[str, Any]:
        """估算策略性能"""
        try:
            risk_tolerance = elements.get("risk_tolerance", "稳健")
            asset_summary = strategy_config.get("asset_summary", {})
            
            # 基础性能估算
            base_performance = {
                "保守": {"return": 5.5, "volatility": 8.0, "drawdown": 6.0, "sharpe": 0.6},
                "稳健": {"return": 8.0, "volatility": 12.0, "drawdown": 10.0, "sharpe": 0.8},
                "积极": {"return": 12.0, "volatility": 18.0, "drawdown": 15.0, "sharpe": 0.9},
                "激进": {"return": 15.0, "volatility": 25.0, "drawdown": 25.0, "sharpe": 0.8}
            }
            
            base = base_performance.get(risk_tolerance, base_performance["稳健"])
            
            # 根据资产配置调整
            stock_ratio = asset_summary.get("股票", 0) / 100
            adjustment = (stock_ratio - 0.6) * 2  # 基准股票比例60%
            
            return {
                "expected_annual_return": round(base["return"] + adjustment, 2),
                "expected_volatility": round(base["volatility"] + adjustment * 1.5, 2),
                "expected_max_drawdown": round(base["drawdown"] + adjustment, 2),
                "expected_sharpe_ratio": round(base["sharpe"], 2),
                "confidence_level": 0.75
            }
            
        except Exception as e:
            logger.error(f"性能估算失败: {e}")
            return {
                "expected_annual_return": 8.0,
                "expected_volatility": 12.0,
                "expected_max_drawdown": 10.0,
                "expected_sharpe_ratio": 0.8,
                "confidence_level": 0.5
            }
    
    def _analyze_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户反馈"""
        content = feedback.get("content", "")
        
        analysis = {
            "feedback_type": "general",
            "adjustments": [],
            "sentiment": "neutral"
        }
        
        # 风险调整
        if "风险太高" in content or "回撤太大" in content:
            analysis["feedback_type"] = "risk_reduction"
            analysis["adjustments"].append("reduce_risk")
        
        if "收益太低" in content or "收益不够" in content:
            analysis["feedback_type"] = "return_enhancement"
            analysis["adjustments"].append("increase_return")
        
        # 配置调整
        if "比例" in content and ("调整" in content or "修改" in content):
            analysis["feedback_type"] = "allocation_adjustment"
            analysis["adjustments"].append("rebalance")
        
        return analysis
    
    def _apply_optimization(self, strategy: Dict[str, Any], 
                          analysis: Dict[str, Any]) -> Dict[str, Any]:
        """应用优化调整"""
        optimized = strategy.copy()
        adjustments = analysis.get("adjustments", [])
        
        if "reduce_risk" in adjustments:
            optimized = self._reduce_strategy_risk(optimized)
        
        if "increase_return" in adjustments:
            optimized = self._increase_strategy_return(optimized)
        
        if "rebalance" in adjustments:
            optimized = self._rebalance_strategy(optimized)
        
        return optimized
    
    def _reduce_strategy_risk(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """降低策略风险"""
        if "etf_allocations" not in strategy:
            return strategy
        
        allocations = strategy["etf_allocations"].copy()
        
        for allocation in allocations:
            asset_class = allocation.get("asset_class", "").lower()
            current_weight = allocation.get("weight", 0)
            
            if "股票" in asset_class:
                allocation["weight"] = max(current_weight * 0.8, 5)  # 减少股票权重
            elif "债券" in asset_class:
                allocation["weight"] = min(current_weight * 1.4, 60)  # 增加债券权重
        
        # 重新归一化
        total_weight = sum(alloc["weight"] for alloc in allocations)
        if total_weight > 0:
            for allocation in allocations:
                allocation["weight"] = round(allocation["weight"] / total_weight * 100, 2)
        
        strategy["etf_allocations"] = allocations
        return strategy
    
    def _increase_strategy_return(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """提高策略收益"""
        if "etf_allocations" not in strategy:
            return strategy
        
        allocations = strategy["etf_allocations"].copy()
        
        for allocation in allocations:
            asset_class = allocation.get("asset_class", "").lower()
            current_weight = allocation.get("weight", 0)
            
            if "股票" in asset_class:
                allocation["weight"] = min(current_weight * 1.3, 80)  # 增加股票权重
            elif "债券" in asset_class:
                allocation["weight"] = max(current_weight * 0.7, 10)  # 减少债券权重
        
        # 重新归一化
        total_weight = sum(alloc["weight"] for alloc in allocations)
        if total_weight > 0:
            for allocation in allocations:
                allocation["weight"] = round(allocation["weight"] / total_weight * 100, 2)
        
        strategy["etf_allocations"] = allocations
        return strategy
    
    def _rebalance_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """重新平衡策略"""
        if "etf_allocations" not in strategy:
            return strategy
        
        allocations = strategy["etf_allocations"]
        total_weight = sum(alloc.get("weight", 0) for alloc in allocations)
        
        if total_weight > 0:
            for allocation in allocations:
                allocation["weight"] = round(allocation["weight"] / total_weight * 100, 2)
        
        return strategy
    
    def _summarize_changes(self, original: Dict[str, Any], 
                         optimized: Dict[str, Any]) -> List[str]:
        """总结策略变更"""
        changes = []
        
        orig_allocations = original.get("etf_allocations", [])
        opt_allocations = optimized.get("etf_allocations", [])
        
        for orig, opt in zip(orig_allocations, opt_allocations):
            orig_weight = orig.get("weight", 0)
            opt_weight = opt.get("weight", 0)
            
            if abs(orig_weight - opt_weight) > 1:
                etf_name = orig.get("etf_name", "")
                if opt_weight > orig_weight:
                    changes.append(f"{etf_name}权重从{orig_weight}%增加到{opt_weight}%")
                else:
                    changes.append(f"{etf_name}权重从{orig_weight}%减少到{opt_weight}%")
        
        if not changes:
            changes.append("策略配置微调优化")
        
        return changes
