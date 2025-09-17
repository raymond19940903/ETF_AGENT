"""虚拟板块数据工具

基于ETF分类构建虚拟行业板块数据，提供板块轮动分析依据。
"""

from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.data_processing.sector_builder import VirtualSectorBuilder
from app.data_processing.data_enricher import DataEnricher
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VirtualSectorDataInput(BaseModel):
    """虚拟板块数据工具输入"""
    sector_type: Optional[str] = Field(None, description="板块类型（科技/医药/金融等）")
    analysis_date: Optional[str] = Field(None, description="分析日期（YYYY-MM-DD）")
    include_rotation_analysis: bool = Field(True, description="是否包含板块轮动分析")


class VirtualSectorDataTool(BaseTool):
    """虚拟板块数据工具"""
    name = "virtual_sector_data_tool"
    description = "基于ETF分类构建虚拟行业板块数据，提供板块轮动分析依据"
    args_schema = VirtualSectorDataInput
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.sector_builder = VirtualSectorBuilder()
        self.data_enricher = DataEnricher(db)
    
    def _run(self, sector_type: Optional[str] = None,
             analysis_date: Optional[str] = None,
             include_rotation_analysis: bool = True) -> str:
        """执行虚拟板块数据构建"""
        
        try:
            # 1. 设置分析日期
            if not analysis_date:
                analysis_date = datetime.now().strftime("%Y-%m-%d")
            
            # 2. 获取ETF数据
            etf_data = self._get_etf_universe()
            if not etf_data:
                return "无法获取ETF数据，板块分析失败。"
            
            # 3. 补全ETF分类信息
            enriched_etfs = self.data_enricher.enrich_etf_data(etf_data)
            
            # 4. 构建虚拟板块数据
            if sector_type:
                # 构建特定板块数据
                sector_etfs = [etf for etf in enriched_etfs 
                             if etf.get('derived_industry') == sector_type or 
                                etf.get('derived_sub_category') == sector_type]
                
                if not sector_etfs:
                    return f"未找到{sector_type}板块相关的ETF产品。"
                
                sector_data = self.sector_builder.build_sector_data(sector_etfs, analysis_date)
                return self._format_single_sector_output(sector_data, sector_type)
            else:
                # 构建所有板块数据
                all_sectors = self.sector_builder.build_sector_data(enriched_etfs, analysis_date)
                
                if include_rotation_analysis:
                    rotation_analysis = self.sector_builder.build_sector_rotation_analysis(all_sectors)
                    return self._format_all_sectors_output(all_sectors, rotation_analysis)
                else:
                    return self._format_sectors_summary(all_sectors)
            
        except Exception as e:
            logger.error(f"虚拟板块数据构建失败: {e}")
            return f"板块数据分析失败: {str(e)}"
    
    def _get_etf_universe(self) -> List[Dict]:
        """获取ETF全集数据"""
        try:
            # 这里应该从数据库查询所有活跃的ETF
            # 当前返回模拟数据，实际实现时需要查询etf_basic_info表
            
            from app.models.etf import ETFBasicInfo
            
            etfs = self.db.query(ETFBasicInfo).filter(
                ETFBasicInfo.status == "active"
            ).all()
            
            return [
                {
                    "etf_code": etf.etf_code,
                    "etf_name": etf.etf_name,
                    "asset_class": etf.asset_class,
                    "fund_company": etf.fund_company,
                    "fund_scale": etf.fund_scale,
                    "listing_date": str(etf.listing_date) if etf.listing_date else None
                }
                for etf in etfs
            ]
            
        except Exception as e:
            logger.error(f"获取ETF数据失败: {e}")
            return []
    
    def _format_single_sector_output(self, sector_data: List[Dict], sector_type: str) -> str:
        """格式化单个板块输出"""
        
        if not sector_data:
            return f"{sector_type}板块数据构建失败。"
        
        sector = sector_data[0]  # 单个板块
        
        output_lines = [
            f"{sector['sector_name']}板块分析报告:",
            f"分析日期: {sector['trade_date']}",
            f"板块指数: {sector['index_value']:.2f}",
            f"涨跌幅: {sector['change_rate']:.2f}%",
            f"成分ETF数量: {sector['etf_count']}个",
            f"总市值: {sector['total_market_cap']:.0f}万元",
            "",
            "成分ETF列表:"
        ]
        
        # 添加成分ETF信息
        for i, etf_code in enumerate(sector['constituent_etfs'][:10], 1):
            weight = sector['weights'].get(etf_code, 0)
            output_lines.append(f"  {i}. {etf_code} (权重: {weight:.2%})")
        
        if len(sector['constituent_etfs']) > 10:
            output_lines.append(f"  ... 还有{len(sector['constituent_etfs']) - 10}个ETF")
        
        # 添加板块表现总结
        if sector.get('performance_summary'):
            output_lines.append(f"\n板块表现: {sector['performance_summary']}")
        
        return "\n".join(output_lines)
    
    def _format_all_sectors_output(self, all_sectors: List[Dict], 
                                  rotation_analysis: Dict[str, Any]) -> str:
        """格式化所有板块输出"""
        
        if not all_sectors:
            return "无法构建板块数据，可能是ETF数据不足。"
        
        # 按表现排序
        sorted_sectors = sorted(all_sectors, key=lambda x: x['change_rate'], reverse=True)
        
        output_lines = [
            f"板块轮动分析报告 ({sorted_sectors[0]['trade_date']}):",
            "",
            "板块表现排名:"
        ]
        
        # 添加板块排名
        for i, sector in enumerate(sorted_sectors, 1):
            performance_icon = "📈" if sector['change_rate'] > 0 else "📉"
            output_lines.append(
                f"  {i}. {sector['sector_name']} {performance_icon} "
                f"{sector['change_rate']:+.2f}% ({sector['etf_count']}只ETF)"
            )
        
        # 添加轮动分析
        if rotation_analysis.get("rotation_analysis"):
            analysis = rotation_analysis["rotation_analysis"]
            output_lines.extend([
                "",
                "板块轮动建议:",
                f"强势板块: {', '.join(analysis.get('strong_sectors', []))}",
                f"弱势板块: {', '.join(analysis.get('weak_sectors', []))}",
                "",
                f"投资建议: {analysis.get('rotation_suggestion', '')}"
            ])
        
        return "\n".join(output_lines)
    
    def _format_sectors_summary(self, all_sectors: List[Dict]) -> str:
        """格式化板块摘要"""
        
        if not all_sectors:
            return "无板块数据可供分析。"
        
        output_lines = [
            f"板块数据摘要 ({all_sectors[0]['trade_date']}):",
            f"共构建 {len(all_sectors)} 个虚拟板块",
            ""
        ]
        
        # 统计信息
        positive_sectors = [s for s in all_sectors if s['change_rate'] > 0]
        negative_sectors = [s for s in all_sectors if s['change_rate'] < 0]
        
        output_lines.extend([
            f"上涨板块: {len(positive_sectors)}个",
            f"下跌板块: {len(negative_sectors)}个",
            f"平盘板块: {len(all_sectors) - len(positive_sectors) - len(negative_sectors)}个"
        ])
        
        if positive_sectors:
            best_sector = max(positive_sectors, key=lambda x: x['change_rate'])
            output_lines.append(f"表现最佳: {best_sector['sector_name']} (+{best_sector['change_rate']:.2f}%)")
        
        if negative_sectors:
            worst_sector = min(negative_sectors, key=lambda x: x['change_rate'])
            output_lines.append(f"表现最差: {worst_sector['sector_name']} ({worst_sector['change_rate']:.2f}%)")
        
        return "\n".join(output_lines)
    
    async def _arun(self, sector_type: Optional[str] = None,
                   analysis_date: Optional[str] = None,
                   include_rotation_analysis: bool = True) -> str:
        """异步执行虚拟板块数据构建"""
        return self._run(sector_type, analysis_date, include_rotation_analysis)


if __name__ == "__main__":
    # 测试代码
    print("虚拟板块数据工具测试完成")
