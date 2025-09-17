"""Celery Worker启动脚本"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start()
