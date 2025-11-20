from fastapi import APIRouter, Request

# from routers.agent import chat
from services.chat_service import handle_chat
from services.db_service import db_service
import asyncio
import json

router = APIRouter(prefix="/api/canvas")


@router.get("/list")
async def list_canvases():  # 列出所有画布
    return await db_service.list_canvases()


@router.post("/create")
async def create_canvas(request: Request):  # 创建画布
    data = await request.json()
    id = data.get('canvas_id')
    name = data.get('name')

    asyncio.create_task(handle_chat(data))
    await db_service.create_canvas(id, name)
    return {"id": id}


@router.get("/{id}")
async def get_canvas(id: str):  # 获取画布数据
    return await db_service.get_canvas_data(id)


@router.post("/{id}/save")
async def save_canvas(id: str, request: Request):  # 保存画布数据
    payload = await request.json()
    data_str = json.dumps(payload['data'])
    await db_service.save_canvas_data(id, data_str, payload['thumbnail'])
    return {"id": id}


@router.post("/{id}/rename")
async def rename_canvas(id: str, request: Request):  # 重命名画布
    data = await request.json()
    name = data.get('name')
    await db_service.rename_canvas(id, name)
    return {"id": id}


@router.delete("/{id}/delete")
async def delete_canvas(id: str):  # 删除画布
    await db_service.delete_canvas(id)
    return {"id": id}
