from . import Migration
import sqlite3


class V2AddCanvases(Migration):
    version = 2
    description = "Add canvases"

    def up(self, conn: sqlite3.Connection) -> None:
        # Create canvases table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS canvases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT,
                description TEXT DEFAULT '',
                thumbnail TEXT DEFAULT '',
                created_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
        """
        )  # 创建画布表

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_canvases_updated_at ON canvases(updated_at DESC, id DESC)
        """
        )  # 创建画布表索引

        # Check if canvas_id column already exists in chat_sessions
        cursor = conn.execute("PRAGMA table_info(chat_sessions)")
        columns = [column[1] for column in cursor.fetchall()]  # 获取聊天会话表的列

        if 'canvas_id' not in columns:
            # Add canvas_id column to chat_sessions only if it doesn't exist
            conn.execute(
                "ALTER TABLE chat_sessions ADD COLUMN canvas_id TEXT REFERENCES canvases(id)"
            )  # 添加画布ID到聊天会话表

        # Create default canvas
        conn.execute(
            """
            INSERT OR IGNORE INTO canvases (id, name)
            VALUES ('default', 'Default Canvas')
        """
        )  # 创建默认画布

        # Associate all existing sessions with default canvas
        conn.execute(
            """
            UPDATE chat_sessions
            SET canvas_id = 'default'
            WHERE canvas_id IS NULL
        """
        )  # 将所有聊天会话关联到默认画布

    def down(self, conn: sqlite3.Connection) -> None:  # 回滚数据库结构
        # Remove canvas_id column from chat_sessions
        conn.execute(
            """
            CREATE TABLE chat_sessions_new (
                id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at TEXT DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
                title TEXT,
                model TEXT,
                provider TEXT
            )
        """
        )  # 创建新的聊天会话表

        conn.execute(
            """
            INSERT INTO chat_sessions_new (id, created_at, updated_at, title, model, provider)
            SELECT id, created_at, updated_at, title, model, provider FROM chat_sessions
        """
        )  # 将聊天会话表的数据插入到新的聊天会话表

        conn.execute("DROP TABLE chat_sessions")  # 删除聊天会话表
        conn.execute(
            "ALTER TABLE chat_sessions_new RENAME TO chat_sessions"
        )  # 将新的聊天会话表重命名为聊天会话表

        conn.execute("DROP TABLE IF EXISTS canvases")  # 删除画布表
