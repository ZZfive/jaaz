# routers/websocket_router.py
from services.websocket_state import sio, add_connection, remove_connection


@sio.event
async def connect(sid, environ, auth):  # 客户连接时触发
    print(f"Client {sid} connected")

    user_info = auth or {}  # 获取用户信息
    add_connection(sid, user_info)  # 添加连接

    await sio.emit('connected', {'status': 'connected'}, room=sid)  # 发送连接成功消息


@sio.event
async def disconnect(sid):  # 客户断开连接时触发
    print(f"Client {sid} disconnected")
    remove_connection(sid)  # 删除连接


@sio.event
async def ping(sid, data):  # 心跳检测
    await sio.emit('pong', data, room=sid)  # 发送心跳响应消息
