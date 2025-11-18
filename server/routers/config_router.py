from fastapi import APIRouter, Request
from services.config_service import config_service

# from tools.video_models_dynamic import register_video_models  # Disabled video models
from services.tool_service import tool_service

router = APIRouter(
    prefix="/api/config"
)  # 创建设置相关的路由器，所有端点都以 /api/config 为前缀


@router.get("/exists")
async def config_exists():
    return {"exists": config_service.exists_config()}  # 检查配置文件是否存在


@router.get("")
async def get_config():
    return config_service.app_config  # 获取所有配置


@router.post("")
async def update_config(request: Request):
    data = await request.json()  # 获取请求数据
    res = await config_service.update_config(data)  # 更新配置

    # 每次更新配置后，重新初始化工具，因为工具依赖于配置
    await tool_service.initialize()  # 重新初始化工具
    return res  # 返回响应
