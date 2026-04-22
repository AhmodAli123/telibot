import asyncio
from datetime import datetime, timedelta
from database.manager import Database


class CronService:
    def __init__(self, db: Database, execution_service):
        self.db = db
        self.exec = execution_service

    async def add_job(self, user_id: int, script_name: str, interval: int):
        nxt = (datetime.now() + timedelta(seconds=interval)).isoformat()
        await self.db.execute(
            "INSERT INTO cron_jobs (user_id, script_name, schedule_type, interval_seconds, next_run) VALUES (?, ?, 'interval', ?, ?)",
            (user_id, script_name, interval, nxt)
        )

    async def run_loop(self):
        while True:
            await asyncio.sleep(60)
            now = datetime.now().isoformat()
            rows = await self.db.fetchall(
                "SELECT id, user_id, script_name, interval_seconds FROM cron_jobs WHERE next_run <= ? AND is_active = 1",
                (now,)
            )
            for row in rows:
                uid, sid, script, inter = row["user_id"], row["id"], row["script_name"], row["interval_seconds"]
                await self.exec.run_script(uid, script)
                nxt = (datetime.now() + timedelta(seconds=inter)).isoformat()
                await self.db.execute("UPDATE cron_jobs SET next_run = ? WHERE id = ?", (nxt, sid))