"""数据模型基类"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class BaseModel:
    """模型基类，包含通用字段"""
    
    @declared_attr
    def __tablename__(cls):
        """自动生成表名"""
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        comment="更新时间"
    )


# 创建基类
Base = declarative_base(cls=BaseModel)
