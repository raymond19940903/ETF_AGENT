"""WebSocket连接管理器"""
from typing import Dict, Set, Any, Callable
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接：session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # 用户会话映射：user_id -> Set[session_id]
        self.user_sessions: Dict[int, Set[str]] = {}
        # 状态更新回调
        self.status_callbacks: Dict[str, Callable] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: int):
        """建立WebSocket连接"""
        try:
            await websocket.accept()
            
            # 断开之前的连接（如果存在）
            if session_id in self.active_connections:
                await self.disconnect(session_id)
            
            # 添加新连接
            self.active_connections[session_id] = websocket
            
            # 更新用户会话映射
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
            
            logger.info(f"WebSocket连接建立: session={session_id}, user={user_id}")
            
            # 发送连接确认消息
            await self.send_to_session(session_id, {
                "type": "connection_established",
                "data": {
                    "session_id": session_id,
                    "message": "连接已建立"
                }
            })
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            raise
    
    async def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        try:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                
                try:
                    await websocket.close(code=1000, reason="正常断开")
                except:
                    pass  # 忽略关闭时的错误
                
                del self.active_connections[session_id]
                
                # 更新用户会话映射
                for user_id, sessions in self.user_sessions.items():
                    if session_id in sessions:
                        sessions.remove(session_id)
                        if not sessions:  # 如果用户没有其他会话，删除映射
                            del self.user_sessions[user_id]
                        break
                
                # 清理状态回调
                if session_id in self.status_callbacks:
                    del self.status_callbacks[session_id]
                
                logger.info(f"WebSocket连接断开: {session_id}")
                
        except Exception as e:
            logger.error(f"断开WebSocket连接失败: {e}")
    
    async def send_to_session(self, session_id: str, message: Dict[str, Any]) -> bool:
        """向指定会话发送消息"""
        try:
            if session_id not in self.active_connections:
                logger.warning(f"会话不存在: {session_id}")
                return False
            
            websocket = self.active_connections[session_id]
            message_json = json.dumps(message, ensure_ascii=False, default=str)
            
            await websocket.send_text(message_json)
            return True
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket连接已断开: {session_id}")
            await self.disconnect(session_id)
            return False
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
            return False
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> int:
        """向用户的所有会话发送消息"""
        sent_count = 0
        
        if user_id in self.user_sessions:
            sessions = self.user_sessions[user_id].copy()
            for session_id in sessions:
                if await self.send_to_session(session_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """向所有连接广播消息"""
        sent_count = 0
        
        sessions = list(self.active_connections.keys())
        for session_id in sessions:
            if await self.send_to_session(session_id, message):
                sent_count += 1
        
        return sent_count
    
    def get_connection_count(self) -> int:
        """获取活跃连接数"""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """获取用户连接数"""
        return len(self.user_sessions.get(user_id, set()))
    
    def is_session_connected(self, session_id: str) -> bool:
        """检查会话是否连接"""
        return session_id in self.active_connections
    
    def register_status_callback(self, session_id: str, callback: Callable):
        """注册状态更新回调"""
        self.status_callbacks[session_id] = callback
    
    async def send_status_update(self, session_id: str, status: str, message: str):
        """发送状态更新"""
        status_message = {
            "type": "status_update",
            "data": {
                "status": status,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        await self.send_to_session(session_id, status_message)
    
    async def send_strategy_update(self, session_id: str, strategy_data: Dict[str, Any]):
        """发送策略更新"""
        strategy_message = {
            "type": "strategy_update",
            "data": strategy_data
        }
        
        await self.send_to_session(session_id, strategy_message)
    
    async def handle_ping_pong(self, session_id: str):
        """处理心跳检测"""
        try:
            if session_id in self.active_connections:
                await self.send_to_session(session_id, {
                    "type": "pong",
                    "data": {"timestamp": asyncio.get_event_loop().time()}
                })
        except Exception as e:
            logger.error(f"心跳检测失败: {e}")
            await self.disconnect(session_id)
    
    async def cleanup_inactive_connections(self):
        """清理非活跃连接"""
        inactive_sessions = []
        
        for session_id, websocket in self.active_connections.items():
            try:
                # 发送ping消息测试连接
                await websocket.ping()
            except:
                inactive_sessions.append(session_id)
        
        # 断开非活跃连接
        for session_id in inactive_sessions:
            await self.disconnect(session_id)
        
        if inactive_sessions:
            logger.info(f"清理了 {len(inactive_sessions)} 个非活跃连接")


# 创建全局WebSocket管理器实例
websocket_manager = WebSocketManager()
