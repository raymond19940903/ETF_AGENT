"""ETF数据获取工具 - 集成数据补全功能"""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.data.etf_service import ETFService
from app.data_processing.data_enricher import DataEnricher
import logging

logger = logging.getLogger(__name__)


class ETFDataFetchInput(BaseModel):
    """ETF数据获取工具输入"""
    asset_class: Optional[str] = Field(None, description="资产类别")
    sector: Optional[str] = Field(None, description="行业板块")
    etf_codes: Optional[List[str]] = Field(None, description="指定ETF代码列表")
    limit: int = Field(20, description="返回数量限制")
    include_enrichment: bool = Field(True, description="是否包含数据补全")


class ETFDataFetchTool(BaseTool):
    """ETF数据获取工具 - 集成智能数据补全"""
    name = "etf_data_fetch_tool"
    description = "从Wind数据库获取ETF数据并进行智能补全，提供完整的投资分析信息"
    args_schema = ETFDataFetchInput
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.etf_service = ETFService(db)
        self.data_enricher = DataEnricher(db)
    
    def _run(self, asset_class: Optional[str] = None, 
             sector: Optional[str] = None,
             etf_codes: Optional[List[str]] = None,
             limit: int = 20,
             include_enrichment: bool = True) -> str:
        """执行ETF数据获取和补全"""
        try:
            # 1. 获取原始Wind数据
            raw_result = self._fetch_raw_etf_data(asset_class, sector, etf_codes, limit)
            
            if not raw_result["success"]:
                return f"ETF数据获取失败: {raw_result.get('error', '未知错误')}"
            
            # 2. 数据补全（如果启用）
            if include_enrichment and raw_result["etf_data"]:
                enriched_data = self.data_enricher.enrich_etf_data(raw_result["etf_data"])
                raw_result["etf_data"] = enriched_data
                raw_result["data_enriched"] = True
            else:
                raw_result["data_enriched"] = False
            
            # 3. 格式化输出给大模型
            return self._format_for_llm(raw_result)
            
        except Exception as e:
            logger.error(f"ETF数据获取失败: {e}")
            return f"ETF数据获取失败: {str(e)}"
    
    def _fetch_raw_etf_data(self, asset_class: Optional[str], sector: Optional[str],
                           etf_codes: Optional[List[str]], limit: int) -> Dict[str, Any]:
        """获取原始ETF数据"""
        
        result = {
            "success": True,
            "etf_data": [],
            "total_count": 0
        }
        
        if etf_codes:
            # 获取指定ETF的详细信息
            for code in etf_codes:
                etf_detail = self.etf_service.get_etf_detail(code)
                if etf_detail:
                    result["etf_data"].append(etf_detail)
        else:
            # 根据条件获取ETF列表
            etf_list = self.etf_service.get_etf_list(
                asset_class=asset_class,
                sector=sector, 
                limit=limit
            )
            result["etf_data"] = etf_list
        
        result["total_count"] = len(result["etf_data"])
        return result
    
    def _format_for_llm(self, data: Dict[str, Any]) -> str:
        """格式化数据供大模型使用"""
        
        if not data["etf_data"]:
            return "未找到符合条件的ETF产品。"
        
        output_lines = [f"找到 {data['total_count']} 个ETF产品："]
        
        for etf in data["etf_data"]:
            etf_info = [
                f"ETF代码: {etf.get('etf_code', 'N/A')}",
                f"ETF名称: {etf.get('etf_name', 'N/A')}",
                f"资产类别: {etf.get('asset_class', 'N/A')}",
                f"基金公司: {etf.get('fund_company', 'N/A')}",
                f"基金规模: {etf.get('fund_scale', 'N/A')}万元"
            ]
            
            # 添加补全的信息（如果有）
            if data.get("data_enriched"):
                if etf.get("derived_category"):
                    etf_info.append(f"推导分类: {etf['derived_category']}")
                if etf.get("derived_investment_objective"):
                    etf_info.append(f"投资目标: {etf['derived_investment_objective']}")
                if etf.get("derived_pe_ratio"):
                    etf_info.append(f"估算PE: {etf['derived_pe_ratio']} (估算值)")
                if etf.get("derived_pb_ratio"):
                    etf_info.append(f"估算PB: {etf['derived_pb_ratio']} (估算值)")
            
            output_lines.append(f"\n{etf.get('etf_name', 'N/A')}:")
            output_lines.extend([f"  - {info}" for info in etf_info])
        
        if data.get("data_enriched"):
            output_lines.append(f"\n注：标记为'估算值'的数据基于算法推导，仅供参考。")
        
        return "\n".join(output_lines)
    
    async def _arun(self, asset_class: Optional[str] = None,
                   sector: Optional[str] = None,
                   etf_codes: Optional[List[str]] = None,
                   limit: int = 20,
                   include_enrichment: bool = True) -> str:
        """异步执行ETF数据获取"""
        return self._run(asset_class, sector, etf_codes, limit, include_enrichment)
