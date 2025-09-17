"""ETF分类推导模块

基于ETF名称和代码推导分类信息，补全Wind数据库中缺失的分类字段。
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ETFClassifier:
    """ETF分类器"""
    
    def __init__(self):
        self.industry_keywords = {
            "科技": ["科技", "芯片", "半导体", "人工智能", "AI", "5G", "互联网", "计算机", "电子", "通信"],
            "医药": ["医药", "生物", "医疗", "健康", "制药", "医疗器械", "生物医药", "CXO"],
            "金融": ["银行", "保险", "证券", "金融", "券商", "信托", "期货"],
            "消费": ["消费", "食品", "饮料", "零售", "白酒", "家电", "纺织", "轻工"],
            "能源": ["能源", "石油", "煤炭", "电力", "新能源", "光伏", "风电", "储能"],
            "军工": ["军工", "国防", "航天", "航空", "兵器", "船舶"],
            "地产": ["地产", "房地产", "建筑", "基建", "建材", "装饰"],
            "材料": ["材料", "化工", "钢铁", "有色", "采掘", "化学"],
            "交通": ["交通", "运输", "物流", "航运", "港口", "机场"],
            "公用": ["公用", "水务", "燃气", "环保", "公共服务"]
        }
        
        self.theme_keywords = {
            "ESG": ["ESG", "可持续", "绿色", "环保", "碳中和"],
            "红利": ["红利", "股息", "分红", "高股息"],
            "成长": ["成长", "创新", "新兴", "小盘", "创业板"],
            "价值": ["价值", "蓝筹", "大盘", "低估值"],
            "质量": ["质量", "优质", "龙头", "白马"],
            "动量": ["动量", "趋势", "强势"]
        }
        
        self.region_keywords = {
            "A股": ["沪深", "上证", "深证", "创业板", "科创板", "中证", "国证"],
            "港股": ["港股", "恒生", "香港", "H股"],
            "美股": ["纳斯达克", "标普", "美股", "道琼斯"],
            "全球": ["全球", "海外", "MSCI", "发达", "新兴"]
        }
    
    def classify_etf(self, etf_name: str, etf_code: str) -> Dict[str, str]:
        """对ETF进行分类"""
        
        classification = {
            "derived_category": "综合指数ETF",
            "derived_sub_category": "综合",
            "derived_industry": None,
            "derived_theme": None,
            "derived_region": "A股",
            "derived_investment_objective": "",
            "derived_risk_level": "medium"
        }
        
        # 1. 行业分类
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in etf_name for keyword in keywords):
                classification["derived_industry"] = industry
                classification["derived_category"] = f"{industry}行业ETF"
                classification["derived_sub_category"] = industry
                break
        
        # 2. 主题分类
        for theme, keywords in self.theme_keywords.items():
            if any(keyword in etf_name for keyword in keywords):
                classification["derived_theme"] = theme
                if not classification["derived_industry"]:
                    classification["derived_category"] = f"{theme}主题ETF"
                    classification["derived_sub_category"] = theme
                break
        
        # 3. 地域分类
        for region, keywords in self.region_keywords.items():
            if any(keyword in etf_name for keyword in keywords):
                classification["derived_region"] = region
                break
        
        # 4. 生成投资目标
        classification["derived_investment_objective"] = self._generate_investment_objective(
            classification, etf_name
        )
        
        # 5. 推导风险等级
        classification["derived_risk_level"] = self._derive_risk_level(
            classification, etf_name
        )
        
        return classification
    
    def _generate_investment_objective(self, classification: Dict[str, str], etf_name: str) -> str:
        """生成投资目标描述"""
        
        templates = {
            "行业": "本基金主要投资于{industry}行业相关的优质上市公司，通过跟踪相关指数，为投资者提供投资{industry}行业的便利工具。",
            "主题": "本基金围绕{theme}投资主题，精选相关概念股票，把握{theme}投资机遇，实现主题投资价值。",
            "指数": "本基金采用被动投资策略，通过严格跟踪标的指数，为投资者提供指数化投资工具。",
            "综合": "本基金通过投资一篮子股票，实现对相关市场的广泛覆盖，为投资者提供分散化投资选择。"
        }
        
        if classification.get("derived_industry"):
            return templates["行业"].format(industry=classification["derived_industry"])
        elif classification.get("derived_theme"):
            return templates["主题"].format(theme=classification["derived_theme"])
        elif "指数" in etf_name:
            return templates["指数"]
        else:
            return templates["综合"]
    
    def _derive_risk_level(self, classification: Dict[str, str], etf_name: str) -> str:
        """推导风险等级"""
        
        high_risk_keywords = ["小盘", "创业板", "科创板", "新兴", "成长", "主题"]
        low_risk_keywords = ["大盘", "蓝筹", "红利", "价值", "国债", "货币"]
        
        # 检查高风险关键词
        if any(keyword in etf_name for keyword in high_risk_keywords):
            return "high"
        
        # 检查低风险关键词
        if any(keyword in etf_name for keyword in low_risk_keywords):
            return "low"
        
        # 基于行业判断
        if classification.get("derived_industry") in ["科技", "军工", "新能源"]:
            return "high"
        elif classification.get("derived_industry") in ["消费", "金融", "公用"]:
            return "medium"
        
        return "medium"  # 默认中等风险


def derive_etf_classification(etf_name: str, etf_code: str) -> Dict[str, str]:
    """便捷函数：推导ETF分类信息"""
    classifier = ETFClassifier()
    return classifier.classify_etf(etf_name, etf_code)


def batch_classify_etfs(etf_list: List[Dict]) -> List[Dict]:
    """批量分类ETF"""
    classifier = ETFClassifier()
    
    for etf in etf_list:
        if etf.get("etf_name") and etf.get("etf_code"):
            classification = classifier.classify_etf(
                etf["etf_name"], 
                etf["etf_code"]
            )
            etf.update(classification)
    
    return etf_list


if __name__ == "__main__":
    # 测试代码
    test_etfs = [
        {"etf_name": "沪深300ETF", "etf_code": "510300.SH"},
        {"etf_name": "科技ETF", "etf_code": "515000.SH"},
        {"etf_name": "医药生物ETF", "etf_code": "512010.SH"}
    ]
    
    results = batch_classify_etfs(test_etfs)
    for result in results:
        print(f"{result['etf_name']}: {result['derived_category']}")
