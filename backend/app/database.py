import aiosqlite
from app.config import settings


def get_db():
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return aiosqlite.connect(str(settings.db_path))


async def init_db():
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                summary TEXT,
                file_path TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                start REAL NOT NULL,
                end_time REAL NOT NULL,
                text TEXT NOT NULL
            );
        """)
        await db.commit()
