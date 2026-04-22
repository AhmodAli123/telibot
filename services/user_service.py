from datetime import datetime
from database.manager import Database


class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def register(self, user_id: int, username: str | None):
        exists = await self.db.fetchone("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if not exists:
            await self.db.execute(
                "INSERT INTO users (user_id, username, plan) VALUES (?, ?, ?)",
                (user_id, username, "free")
            )

    async def get(self, user_id: int):
        row = await self.db.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return dict(row) if row else None

    async def update_activity(self, user_id: int):
        await self.db.execute(
            "UPDATE users SET last_activity = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id)
        )

    async def increment_files(self, user_id: int, delta: int = 1):
        await self.db.execute(
            "UPDATE users SET total_files = total_files + ? WHERE user_id = ?",
            (delta, user_id)
        )