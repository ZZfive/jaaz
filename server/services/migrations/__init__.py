from typing import Protocol
import sqlite3


class Migration(Protocol):  # 迁移协议
    """Migration protocol"""

    version: int
    description: str

    def up(self, conn: sqlite3.Connection) -> None:
        """Apply the migration"""
        ...

    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback the migration"""
        ...
