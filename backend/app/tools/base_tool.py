"""LangChain工具基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
import logging

logger = logging.getLogger(__name__)


class ETFBaseTool(BaseTool, ABC):
    """ETF系统工具基类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """统一错误处理"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(error).__name__
        }
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return True
    
    def log_execution(self, action: str, details: Dict[str, Any] = None):
        """记录执行日志"""
        log_msg = f"{self.name} - {action}"
        if details:
            log_msg += f": {details}"
        self.logger.info(log_msg)
    
    @abstractmethod
    def _execute_tool_logic(self, **kwargs) -> Dict[str, Any]:
        """执行工具核心逻辑"""
        pass
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """执行工具（同步）"""
        try:
            # 验证输入
            if not self.validate_input(**kwargs):
                return self.handle_error(ValueError("输入参数验证失败"))
            
            # 记录开始执行
            self.log_execution("开始执行", kwargs)
            
            # 执行核心逻辑
            result = self._execute_tool_logic(**kwargs)
            
            # 记录执行完成
            self.log_execution("执行完成", {"success": result.get("success", False)})
            
            return result
            
        except Exception as e:
            return self.handle_error(e, "工具执行失败")
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """执行工具（异步）"""
        return self._run(**kwargs)
