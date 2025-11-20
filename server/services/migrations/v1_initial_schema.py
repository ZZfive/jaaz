from . import Migration  # 导入迁移协议
import sqlite3


class V1InitialSchema(Migration):  # 初始化数据库结构
    version = 1
    description = "Initial schema"

    def up(self, conn: sqlite3.Connection) -> None:
        # Create chat_sessions table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                canvas_id TEXT,
                created_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                title TEXT,
                model TEXT,
                provider TEXT,
                FOREIGN KEY (canvas_id) REFERENCES canvases(id)
            )
        """
        )  # 创建聊天会话表

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC, id DESC)
        """
        )  # 创建聊天会话表索引

        # Create chat_messages table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                message TEXT,
                created_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
            )
        """
        )  # 创建聊天消息表

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id_id ON chat_messages(session_id, id);
        """
        )  # 创建聊天消息表索引

    def down(self, conn: sqlite3.Connection) -> None:  # 回滚数据库结构
        conn.execute("DROP TABLE IF EXISTS chat_messages")  # 删除聊天消息表
        conn.execute("DROP TABLE IF EXISTS chat_sessions")  # 删除聊天会话表
