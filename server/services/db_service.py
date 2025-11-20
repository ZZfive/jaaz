import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
import aiosqlite
from .config_service import USER_DATA_DIR
from .migrations.manager import MigrationManager, CURRENT_VERSION

DB_PATH = os.path.join(USER_DATA_DIR, "localmanus.db")  # 用户数据库路径


class DatabaseService:
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_db_directory()
        self._migration_manager = MigrationManager()
        self._init_db()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        """Initialize the database with the current schema"""  # 初始化数据库
        with sqlite3.connect(self.db_path) as conn:
            # Create version table if it doesn't exist
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS db_version (
                    version INTEGER PRIMARY KEY
                )
            """
            )  # 创建数据库版本表

            # Get current version
            cursor = conn.execute("SELECT version FROM db_version")
            current_version = cursor.fetchone()  # 获取当前数据库版本
            print(
                'local db version', current_version, 'latest version', CURRENT_VERSION
            )

            if current_version is None:
                # First time setup - start from version 0 第一次设置 - 从版本0开始
                conn.execute("INSERT INTO db_version (version) VALUES (0)")
                self._migration_manager.migrate(conn, 0, CURRENT_VERSION)
            elif (
                current_version[0] < CURRENT_VERSION
            ):  # 如果当前数据库版本小于目标版本，则进行迁移
                print(
                    'Migrating database from version',
                    current_version[0],
                    'to',
                    CURRENT_VERSION,
                )
                # Need to migrate
                self._migration_manager.migrate(
                    conn, current_version[0], CURRENT_VERSION
                )  # 进行迁移

    async def create_canvas(self, id: str, name: str):
        """Create a new canvas"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO canvases (id, name)
                VALUES (?, ?)
            """,
                (id, name),
            )  # 向画布表中插入数据
            await db.commit()  # 提交事务

    async def list_canvases(self) -> List[Dict[str, Any]]:
        """Get all canvases"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                """
                SELECT id, name, description, thumbnail, created_at, updated_at
                FROM canvases
                ORDER BY updated_at DESC
            """
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def create_chat_session(
        self,
        id: str,
        model: str,
        provider: str,
        canvas_id: str,
        title: Optional[str] = None,
    ):
        """Save a new chat session"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO chat_sessions (id, model, provider, canvas_id, title)
                VALUES (?, ?, ?, ?, ?)
            """,
                (id, model, provider, canvas_id, title),
            )  # 向聊天会话表中插入数据
            await db.commit()  # 提交事务

    async def create_message(self, session_id: str, role: str, message: str):
        """Save a chat message"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO chat_messages (session_id, role, message)
                VALUES (?, ?, ?)
            """,
                (session_id, role, message),
            )  # 向聊天消息表中插入数据
            await db.commit()  # 提交事务

    async def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                """
                SELECT role, message, id
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY id ASC
            """,
                (session_id,),
            )  # 获取聊天消息
            rows = await cursor.fetchall()

            messages = []
            for row in rows:
                row_dict = dict(row)
                if row_dict['message']:
                    try:
                        msg = json.loads(row_dict['message'])
                        messages.append(msg)
                    except:
                        pass

            return messages

    async def list_sessions(self, canvas_id: str) -> List[Dict[str, Any]]:
        """List all chat sessions"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            if canvas_id:
                cursor = await db.execute(
                    """
                    SELECT id, title, model, provider, created_at, updated_at
                    FROM chat_sessions
                    WHERE canvas_id = ?
                    ORDER BY updated_at DESC
                """,
                    (canvas_id,),
                )  # 获取canvas_id对应的聊天会话
            else:
                cursor = await db.execute(
                    """
                    SELECT id, title, model, provider, created_at, updated_at
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                """
                )  # 获取所有聊天会话
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_canvas_data(self, id: str, data: str, thumbnail: str = None):
        """Save canvas data"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE canvases 
                SET data = ?, thumbnail = ?, updated_at = STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')
                WHERE id = ?
            """,
                (data, thumbnail, id),
            )  # 更新画布数据
            await db.commit()  # 提交事务

    async def get_canvas_data(self, id: str) -> Optional[Dict[str, Any]]:
        """Get canvas data"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                """
                SELECT data, name
                FROM canvases
                WHERE id = ?
            """,
                (id,),
            )  # 获取画布数据
            row = await cursor.fetchone()

            sessions = await self.list_sessions(id)  # 获取canvas_id对应的聊天会话

            if row:
                return {
                    'data': json.loads(row['data']) if row['data'] else {},
                    'name': row['name'],
                    'sessions': sessions,
                }
            return None

    async def delete_canvas(self, id: str):
        """Delete canvas and related data"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM canvases WHERE id = ?", (id,))
            await db.commit()

    async def rename_canvas(self, id: str, name: str):
        """Rename canvas"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE canvases SET name = ? WHERE id = ?", (name, id))
            await db.commit()

    async def create_comfy_workflow(
        self,
        name: str,
        api_json: str,
        description: str,
        inputs: str,
        outputs: str = None,
    ):
        """Create a new comfy workflow"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO comfy_workflows (name, api_json, description, inputs, outputs)
                VALUES (?, ?, ?, ?, ?)
            """,
                (name, api_json, description, inputs, outputs),
            )  # 向ComfyUI工作流表中插入数据
            await db.commit()  # 提交事务

    async def list_comfy_workflows(self) -> List[Dict[str, Any]]:
        """List all comfy workflows"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                "SELECT id, name, description, api_json, inputs, outputs FROM comfy_workflows ORDER BY id DESC"
            )  # 获取所有ComfyUI工作流
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_comfy_workflow(self, id: int):
        """Delete a comfy workflow"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM comfy_workflows WHERE id = ?", (id,))
            await db.commit()

    async def get_comfy_workflow(self, id: int):
        """Get comfy workflow dict"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(
                "SELECT api_json FROM comfy_workflows WHERE id = ?", (id,)
            )  # 获取id对应的ComfyUI工作流
            row = await cursor.fetchone()
        try:
            workflow_json = (
                row["api_json"]
                if isinstance(row["api_json"], dict)
                else json.loads(row["api_json"])
            )  # 将api_json转换为字典
            return workflow_json
        except json.JSONDecodeError as exc:
            raise ValueError(f"Stored workflow api_json is not valid JSON: {exc}")


# Create a singleton instance
db_service = DatabaseService()
