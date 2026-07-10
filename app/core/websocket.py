"""
WebSocket 实时通知服务

提供实时推送功能：
- 审核任务通知
- 系统消息推送
- 在线用户状态
- 数据实时更新
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储活动连接 {user_id: {websocket, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 房间订阅 {room_name: {user_id, ...}}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        建立WebSocket连接

        Args:
            websocket: WebSocket连接
            user_id: 用户ID
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        print(f"✓ WebSocket connected: {user_id}")

        # 发送欢迎消息
        await self.send_personal_message({
            'type': 'connection',
            'message': 'Connected to PayGuard notification service',
            'timestamp': datetime.now().isoformat()
        }, user_id)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # 从所有房间移除
                for room_users in self.rooms.values():
                    room_users.discard(user_id)

        print(f"✓ WebSocket disconnected: {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        """
        发送个人消息

        Args:
            message: 消息内容
            user_id: 用户ID
        """
        if user_id not in self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                print(f"✗ Send error: {e}")
                disconnected.append(websocket)

        # 清理断开的连接
        for ws in disconnected:
            self.active_connections[user_id].discard(ws)

    async def broadcast(self, message: dict, room: Optional[str] = None):
        """
        广播消息

        Args:
            message: 消息内容
            room: 房间名（None表示全局广播）
        """
        message_json = json.dumps(message)

        if room and room in self.rooms:
            # 房间广播
            user_ids = self.rooms[room]
        else:
            # 全局广播
            user_ids = self.active_connections.keys()

        for user_id in user_ids:
            if user_id in self.active_connections:
                for websocket in self.active_connections[user_id]:
                    try:
                        await websocket.send_text(message_json)
                    except Exception:
                        pass

    def join_room(self, user_id: str, room: str):
        """加入房间"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)
        print(f"✓ {user_id} joined room: {room}")

    def leave_room(self, user_id: str, room: str):
        """离开房间"""
        if room in self.rooms:
            self.rooms[room].discard(user_id)
            if not self.rooms[room]:
                del self.rooms[room]

    def get_online_users(self) -> list:
        """获取在线用户列表"""
        return list(self.active_connections.keys())

    def get_user_count(self) -> int:
        """获取在线用户数"""
        return len(self.active_connections)


# 全局连接管理器
manager = ConnectionManager()


# 通知类型定义

class NotificationType:
    """通知类型"""
    REVIEW_ASSIGNED = "review_assigned"        # 审核任务分配
    REVIEW_COMPLETED = "review_completed"      # 审核完成
    REVIEW_ESCALATED = "review_escalated"      # 审核升级
    REVIEW_COMMENTED = "review_commented"      # 新评论
    AUDIT_COMPLETED = "audit_completed"        # 审计完成
    SYSTEM_ALERT = "system_alert"              # 系统警告
    DATA_UPDATED = "data_updated"              # 数据更新


# 通知发送函数

async def notify_review_assigned(user_id: str, review_data: dict):
    """通知审核任务分配"""
    message = {
        'type': NotificationType.REVIEW_ASSIGNED,
        'title': '新的审核任务',
        'data': review_data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.send_personal_message(message, user_id)


async def notify_review_completed(user_id: str, review_data: dict):
    """通知审核完成"""
    message = {
        'type': NotificationType.REVIEW_COMPLETED,
        'title': '审核已完成',
        'data': review_data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.send_personal_message(message, user_id)


async def notify_audit_completed(user_id: str, audit_data: dict):
    """通知审计完成"""
    message = {
        'type': NotificationType.AUDIT_COMPLETED,
        'title': '审计已完成',
        'data': audit_data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.send_personal_message(message, user_id)


async def broadcast_data_update(data_type: str, data: dict):
    """广播数据更新"""
    message = {
        'type': NotificationType.DATA_UPDATED,
        'data_type': data_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.broadcast(message)


async def broadcast_system_alert(alert_message: str, severity: str = "info"):
    """广播系统警告"""
    message = {
        'type': NotificationType.SYSTEM_ALERT,
        'severity': severity,  # info, warning, error
        'message': alert_message,
        'timestamp': datetime.now().isoformat()
    }
    await manager.broadcast(message)


# 心跳检测

async def send_heartbeat():
    """发送心跳包（保持连接活跃）"""
    while True:
        await asyncio.sleep(30)  # 每30秒一次
        message = {
            'type': 'heartbeat',
            'timestamp': datetime.now().isoformat()
        }
        await manager.broadcast(message)
