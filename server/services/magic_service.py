# services/magic_service.py

# Import necessary modules
import asyncio
import json
from typing import Dict, Any, List

# Import service modules
from services.db_service import db_service
from services.OpenAIAgents_service import (
    create_jaaz_response,
)  # jaaz自行维护的云端magic生图能力
from services.websocket_service import send_to_websocket  # type: ignore
from services.stream_service import add_stream_task, remove_stream_task


async def handle_magic(data: Dict[str, Any]) -> None:
    """
    Handle an incoming magic generation request.

    Workflow:
    - Parse incoming magic generation data.
    - Run Agents.
    - Save magic session and messages to the database.
    - Notify frontend via WebSocket.

    Args:
        data (dict): Magic generation request data containing:
            - messages: list of message dicts
            - session_id: unique session identifier
            - canvas_id: canvas identifier (contextual use)
            - text_model: text model configuration
            - tool_list: list of tool model configurations (images/videos)
    """
    # Extract fields from incoming data
    messages: List[Dict[str, Any]] = data.get('messages', [])
    session_id: str = data.get('session_id', '')
    canvas_id: str = data.get('canvas_id', '')

    # print('✨ magic_service 接收到数据:', {
    #     'session_id': session_id,
    #     'canvas_id': canvas_id,
    #     'messages_count': len(messages),
    # })

    # If there is only one message, create a new magic session
    if len(messages) == 1:
        # create new session
        prompt = messages[0].get('content', '')
        await db_service.create_chat_session(
            session_id,
            'gpt',
            'jaaz',
            canvas_id,
            (prompt[:200] if isinstance(prompt, str) else ''),
        )

    # Save user message to database
    if len(messages) > 0:
        await db_service.create_message(
            session_id, messages[-1].get('role', 'user'), json.dumps(messages[-1])
        )

    # Create and start magic generation task
    task = asyncio.create_task(
        _process_magic_generation(messages, session_id, canvas_id)
    )  # 创建magic generation任务

    # Register the task in stream_tasks (for possible cancellation)
    add_stream_task(session_id, task)  # 注册任务到stream_tasks，用于可能的取消
    try:
        # Await completion of the magic generation task
        await task  # 等待任务完成
    except asyncio.exceptions.CancelledError:
        print(f"🛑Magic generation session {session_id} cancelled")
    finally:
        # Always remove the task from stream_tasks after completion/cancellation
        remove_stream_task(session_id)  # 从stream_tasks中移除任务
        # Notify frontend WebSocket that magic generation is done
        await send_to_websocket(session_id, {'type': 'done'})  # 通知前端任务完成

    print('✨ magic_service 处理完成')


async def _process_magic_generation(
    messages: List[Dict[str, Any]],
    session_id: str,
    canvas_id: str,
) -> None:
    """
    Process magic generation in a separate async task.

    Args:
        messages: List of messages
        session_id: Session ID
        canvas_id: Canvas ID
    """

    ai_response = await create_jaaz_response(messages, session_id, canvas_id)

    # Save AI response to database
    await db_service.create_message(session_id, 'assistant', json.dumps(ai_response))

    # Send messages to frontend immediately
    all_messages = messages + [ai_response]
    await send_to_websocket(
        session_id, {'type': 'all_messages', 'messages': all_messages}
    )
