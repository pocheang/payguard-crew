"""
WebSocket API端点
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.websocket import manager
import json

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Query(..., description="用户ID"),
    token: str = Query(None, description="认证Token（可选）")
):
    """
    WebSocket连接端点

    连接URL: ws://localhost:8000/api/ws?user_id=user123&token=xxx

    消息格式：
    {
        "type": "subscribe",
        "room": "reviews"  // 可选：dashboard, reviews, audits
    }
    """
    await manager.connect(websocket, user_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get('type')

                if message_type == 'subscribe':
                    # 订阅房间
                    room = message.get('room')
                    if room:
                        manager.join_room(user_id, room)
                        await websocket.send_json({
                            'type': 'subscribed',
                            'room': room,
                            'message': f'Subscribed to {room}'
                        })

                elif message_type == 'unsubscribe':
                    # 取消订阅
                    room = message.get('room')
                    if room:
                        manager.leave_room(user_id, room)
                        await websocket.send_json({
                            'type': 'unsubscribed',
                            'room': room
                        })

                elif message_type == 'ping':
                    # 心跳响应
                    await websocket.send_json({'type': 'pong'})

                else:
                    # 未知消息类型
                    await websocket.send_json({
                        'type': 'error',
                        'message': f'Unknown message type: {message_type}'
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """获取WebSocket统计信息"""
    return {
        'online_users': manager.get_user_count(),
        'active_rooms': list(manager.rooms.keys()),
        'users': manager.get_online_users()
    }
