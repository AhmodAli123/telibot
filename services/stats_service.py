import time
import psutil
from database.manager import Database


class StatsService:
    def __init__(self, db: Database):
        self.db = db
        self.started = time.time()

    async def get_system_stats(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu": cpu,
            "ram_used": mem.used // (1024 * 1024),
            "ram_total": mem.total // (1024 * 1024),
            "disk_used": disk.used // (1024 * 1024),
            "disk_total": disk.total // (1024 * 1024),
            "uptime": int(time.time() - self.started),
        }

    async def get_global_stats(self):
        u = await self.db.fetchone("SELECT COUNT(*) as c FROM users")
        p = await self.db.fetchone("SELECT COUNT(*) as c FROM processes WHERE status = 'running'")
        return {"total_users": u["c"] if u else 0, "running_processes": p["c"] if p else 0}

    async def get_user_stats(self, user_id: int):
        row = await self.db.fetchone(
            "SELECT total_files, running_processes, plan FROM users WHERE user_id = ?", (user_id,)
        )
        return dict(row) if row else {"total_files": 0, "running_processes": 0, "plan": "free"}