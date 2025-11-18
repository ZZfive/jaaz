# services/websocket_state.py
import socketio
from typing import Dict

sio = socketio.AsyncServer(
    cors_allowed_origins="*", async_mode='asgi'  # 允许所有跨域请求  # 使用ASGI模式
)  # 创建一个异步的Socket.IO服务器

active_connections: Dict[str, dict] = {}  # 存储所有连接的socket_id和用户信息


def add_connection(socket_id: str, user_info: dict = None):  # 添加连接
    active_connections[socket_id] = user_info or {}
    print(
        f"New connection added: {socket_id}, total connections: {len(active_connections)}"
    )


def remove_connection(socket_id: str):  # 删除连接
    if socket_id in active_connections:
        del active_connections[socket_id]
        print(
            f"Connection removed: {socket_id}, total connections: {len(active_connections)}"
        )


def get_all_socket_ids():  # 获取所有连接的socket_id
    return list(active_connections.keys())


def get_connection_count():  # 获取所有连接的数量
    return len(active_connections)
