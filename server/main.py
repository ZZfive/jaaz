import os
import sys
import io

# Ensure stdout and stderr use utf-8 encoding to prevent emoji logs from crashing python server
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
print('Importing websocket_router')
from routers.websocket_router import *  # DO NOT DELETE THIS LINE, OTHERWISE, WEBSOCKET WILL NOT WORK

print('Importing routers')
from routers import (
    config_router,  # 配置路由
    image_router,  # 图片路由
    root_router,
    workspace,  # 工作空间路由
    canvas,  # 画布路由
    ssl_test,
    chat_router,  # 聊天路由
    settings,  # 设置路由
    tool_confirmation,  # 工具确认路由
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import argparse
from contextlib import asynccontextmanager
from starlette.types import Scope
from starlette.responses import Response
import socketio  # type: ignore

print('Importing websocket_state')
from services.websocket_state import sio

print('Importing websocket_service')
from services.websocket_service import broadcast_init_done

print('Importing config_service')
from services.config_service import config_service

print('Importing tool_service')
from services.tool_service import tool_service  # 工具服务


async def initialize():
    print('Initializing config_service')
    await config_service.initialize()
    print('Initializing broadcast_init_done')
    await broadcast_init_done()


root_dir = os.path.dirname(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # 生命周期管理器
    # onstartup
    # TODO: Check if there will be racing conditions when user send chat request but tools and models are not initialized yet.
    await initialize()  # 初始化配置服务
    await tool_service.initialize()  # 初始化工具服务
    yield
    # onshutdown


print('Creating FastAPI app')
app = FastAPI(lifespan=lifespan)  # 创建FastAPI应用

# Include routers
print('Including routers')
app.include_router(config_router.router)
app.include_router(settings.router)
app.include_router(root_router.router)
app.include_router(canvas.router)
app.include_router(workspace.router)
app.include_router(image_router.router)
app.include_router(ssl_test.router)
app.include_router(chat_router.router)
app.include_router(tool_confirmation.router)

# Mount the React build directory
react_build_dir = os.environ.get(
    'UI_DIST_DIR', os.path.join(os.path.dirname(root_dir), "react", "dist")
)  # 获取React构建目录


# 无缓存静态文件类
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"  # 不存储、不缓存
            )
            response.headers["Pragma"] = "no-cache"  # HTTP/1.0 兼容
            response.headers["Expires"] = "0"  # 立即过期
        return response


static_site = os.path.join(react_build_dir, "assets")
if os.path.exists(static_site):  # 开发环境中实时更新前端资源，避免缓存导致的更新延迟
    app.mount(
        "/assets", NoCacheStaticFiles(directory=static_site), name="assets"
    )  # 挂载静态文件


@app.get("/")
async def serve_react_app():
    response = FileResponse(
        os.path.join(react_build_dir, "index.html")
    )  # 根路径/返回index.html文件
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


print('Creating socketio app')
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path='/socket.io',  # 请求路径为/socket.io时由SocketIO处理，其他路径由FastAPI处理
)  # 创建SocketIO应用，可通过一个进程和端口同时部署websocket和fastapi两个服务，并且两者可以进行通讯


if __name__ == "__main__":
    # bypass localhost request for proxy, fix ollama proxy issue
    _bypass = {"127.0.0.1", "localhost", "::1"}
    current = set(os.environ.get("no_proxy", "").split(",")) | set(
        os.environ.get("NO_PROXY", "").split(",")
    )
    os.environ["no_proxy"] = os.environ["NO_PROXY"] = ",".join(
        sorted(_bypass | current - {""})
    )  # 设置no_proxy环境变量，用于绕过本地代理，即请求本地不走代理

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', type=int, default=57988, help='Port to run the server on'
    )  # 设置端口
    args = parser.parse_args()
    import uvicorn

    print("🌟Starting server, UI_DIST_DIR:", os.environ.get('UI_DIST_DIR'))

    uvicorn.run(socket_app, host="127.0.0.1", port=args.port)
