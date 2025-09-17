"""Wind数据库服务"""
import pyodbc
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class WindService:
    """Wind数据库服务类"""
    
    def __init__(self):
        self.connection_string = settings.wind_connection_string
        self.connection = None
    
    def connect(self):
        """连接Wind数据库"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            logger.info("Wind数据库连接成功")
        except Exception as e:
            logger.error(f"Wind数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Wind数据库连接已断开")
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """执行SQL查询"""
        try:
            if not self.connection:
                self.connect()
            
            df = pd.read_sql(query, self.connection, params=params)
            return df
            
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            logger.error(f"查询语句: {query}")
            raise
    
    def get_etf_list(self, asset_class: Optional[str] = None, 
                    sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取ETF产品列表"""
        query = """
        SELECT 
            S_INFO_WINDCODE as code,
            S_INFO_NAME as name,
            S_INFO_FULLNAME as full_name,
            S_INFO_LISTDATE as listing_date,
            S_INFO_DELISTDATE as delisting_date,
            S_INFO_SECTOR as sector,
            S_INFO_INDUSTRYNAME as industry
        FROM ASHAREEODPRICES 
        WHERE S_INFO_WINDCODE LIKE '%.SH' OR S_INFO_WINDCODE LIKE '%.SZ'
        AND S_INFO_NAME LIKE '%ETF%'
        """
        
        params = []
        if asset_class:
            query += " AND S_INFO_INDUSTRYNAME LIKE ?"
            params.append(f"%{asset_class}%")
        
        if sector:
            query += " AND S_INFO_SECTOR LIKE ?"
            params.append(f"%{sector}%")
        
        query += " ORDER BY S_INFO_LISTDATE DESC"
        
        df = self.execute_query(query, tuple(params) if params else None)
        return df.to_dict('records')
    
    def get_etf_basic_info(self, etf_code: str) -> Optional[Dict[str, Any]]:
        """获取ETF基本信息"""
        query = """
        SELECT 
            S_INFO_WINDCODE as code,
            S_INFO_NAME as name,
            S_INFO_FULLNAME as full_name,
            S_INFO_LISTDATE as listing_date,
            S_INFO_SECTOR as sector,
            S_INFO_INDUSTRYNAME as industry,
            S_INFO_COMPNAME as company_name
        FROM ASHAREEODPRICES 
        WHERE S_INFO_WINDCODE = ?
        """
        
        df = self.execute_query(query, (etf_code,))
        if df.empty:
            return None
        
        return df.iloc[0].to_dict()
    
    def get_etf_price_data(self, etf_code: str, start_date: str, 
                          end_date: str) -> List[Dict[str, Any]]:
        """获取ETF价格数据"""
        query = """
        SELECT 
            TRADE_DT as trade_date,
            S_DQ_CLOSE as close_price,
            S_DQ_OPEN as open_price,
            S_DQ_HIGH as high_price,
            S_DQ_LOW as low_price,
            S_DQ_VOLUME as volume,
            S_DQ_AMOUNT as amount,
            S_DQ_PCTCHANGE as pct_change
        FROM ASHAREEODPRICES 
        WHERE S_INFO_WINDCODE = ?
        AND TRADE_DT >= ?
        AND TRADE_DT <= ?
        ORDER BY TRADE_DT
        """
        
        df = self.execute_query(query, (etf_code, start_date, end_date))
        return df.to_dict('records')
    
    def get_etf_nav_data(self, etf_code: str, start_date: str, 
                        end_date: str) -> List[Dict[str, Any]]:
        """获取ETF净值数据"""
        query = """
        SELECT 
            PRICE_DATE as price_date,
            F_NAV_UNIT as unit_nav,
            F_NAV_ACCUMULATED as accumulated_nav,
            F_NAV_ADJUSTED as adjusted_nav
        FROM CHINAMUTUALFUNDNAV 
        WHERE F_INFO_WINDCODE = ?
        AND PRICE_DATE >= ?
        AND PRICE_DATE <= ?
        ORDER BY PRICE_DATE
        """
        
        df = self.execute_query(query, (etf_code, start_date, end_date))
        return df.to_dict('records')
    
    def get_etf_holdings(self, etf_code: str, report_date: str) -> List[Dict[str, Any]]:
        """获取ETF持仓数据"""
        query = """
        SELECT 
            S_INFO_STOCKNAME as stock_name,
            S_INFO_WINDCODE as stock_code,
            F_PRT_ENDDATE as report_date,
            F_PRT_STKVALUE as holding_value,
            F_PRT_STKQUANTITY as holding_quantity,
            F_PRT_STKVALUETONAV as weight_to_nav
        FROM CHINAMUTUALFUNDASSETPORTFOLIO 
        WHERE F_INFO_WINDCODE = ?
        AND F_PRT_ENDDATE = ?
        ORDER BY F_PRT_STKVALUETONAV DESC
        """
        
        df = self.execute_query(query, (etf_code, report_date))
        return df.to_dict('records')
    
    def get_market_index_data(self, index_code: str, start_date: str, 
                             end_date: str) -> List[Dict[str, Any]]:
        """获取市场指数数据"""
        query = """
        SELECT 
            TRADE_DT as trade_date,
            S_DQ_CLOSE as close_price,
            S_DQ_OPEN as open_price,
            S_DQ_HIGH as high_price,
            S_DQ_LOW as low_price,
            S_DQ_PCTCHANGE as pct_change,
            S_DQ_VOLUME as volume
        FROM AINDEXEODPRICES 
        WHERE S_INFO_WINDCODE = ?
        AND TRADE_DT >= ?
        AND TRADE_DT <= ?
        ORDER BY TRADE_DT
        """
        
        df = self.execute_query(query, (index_code, start_date, end_date))
        return df.to_dict('records')
    
    def get_etf_performance_metrics(self, etf_code: str, 
                                   period_days: int = 365) -> Dict[str, Any]:
        """获取ETF绩效指标"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y%m%d')
        
        # 获取价格数据
        price_data = self.get_etf_price_data(etf_code, start_date, end_date)
        if not price_data:
            return {}
        
        df = pd.DataFrame(price_data)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date')
        
        # 计算收益率
        df['daily_return'] = df['close_price'].pct_change()
        
        # 计算绩效指标
        total_return = (df['close_price'].iloc[-1] / df['close_price'].iloc[0] - 1) * 100
        annual_return = ((1 + total_return/100) ** (365/period_days) - 1) * 100
        volatility = df['daily_return'].std() * (252 ** 0.5) * 100
        
        # 计算最大回撤
        cumulative_returns = (1 + df['daily_return']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # 计算夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03
        excess_return = annual_return/100 - risk_free_rate
        sharpe_ratio = excess_return / (volatility/100) if volatility > 0 else 0
        
        return {
            'total_return': round(total_return, 2),
            'annual_return': round(annual_return, 2),
            'volatility': round(volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'period_days': period_days
        }
    
    def search_etf_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """根据关键词搜索ETF"""
        query = """
        SELECT TOP (?)
            S_INFO_WINDCODE as code,
            S_INFO_NAME as name,
            S_INFO_FULLNAME as full_name,
            S_INFO_LISTDATE as listing_date,
            S_INFO_SECTOR as sector,
            S_INFO_INDUSTRYNAME as industry
        FROM ASHAREEODPRICES 
        WHERE (S_INFO_NAME LIKE ? OR S_INFO_FULLNAME LIKE ?)
        AND S_INFO_NAME LIKE '%ETF%'
        ORDER BY S_INFO_LISTDATE DESC
        """
        
        search_pattern = f"%{keyword}%"
        df = self.execute_query(query, (limit, search_pattern, search_pattern))
        return df.to_dict('records')
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


# 创建全局Wind服务实例
wind_service = WindService()
