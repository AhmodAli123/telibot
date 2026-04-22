import os
import aiosqlite
from config import Config


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    role TEXT DEFAULT 'user',
                    plan TEXT DEFAULT 'free',
                    plan_expiry TIMESTAMP,
                    total_files INTEGER DEFAULT 0,
                    running_processes INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    filename TEXT,
                    size INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS processes (
                    pid INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    script_name TEXT,
                    log_file TEXT,
                    status TEXT DEFAULT 'running',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    port INTEGER
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bans (
                    user_id INTEGER PRIMARY KEY,
                    reason TEXT,
                    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cron_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    script_name TEXT,
                    schedule_type TEXT,
                    interval_seconds INTEGER,
                    next_run TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS marketplace (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author_id INTEGER,
                    title TEXT,
                    description TEXT,
                    code TEXT,
                    price INTEGER DEFAULT 0,
                    downloads INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()

    async def fetchone(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()