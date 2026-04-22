import psutil
from database.manager import Database


class ProcessManager:
    def __init__(self, db: Database):
        self.db = db

    async def register(self, pid: int, user_id: int, script_name: str, log_file: str, port: int | None):
        await self.db.execute(
            "INSERT INTO processes (pid, user_id, script_name, log_file, port) VALUES (?, ?, ?, ?, ?)",
            (pid, user_id, script_name, log_file, port)
        )
        await self.db.execute(
            "UPDATE users SET running_processes = running_processes + 1 WHERE user_id = ?", (user_id,)
        )

    async def mark_stopped(self, pid: int):
        await self.db.execute("UPDATE processes SET status = 'stopped' WHERE pid = ?", (pid,))

    async def get_user_process_count(self, user_id: int) -> int:
        row = await self.db.fetchone(
            "SELECT COUNT(*) as c FROM processes WHERE user_id = ? AND status = 'running'", (user_id,)
        )
        return row["c"] if row else 0

    async def get_user_processes(self, user_id: int):
        rows = await self.db.fetchall(
            "SELECT pid, script_name, started_at, port FROM processes WHERE user_id = ? AND status = 'running'",
            (user_id,)
        )
        return [dict(r) for r in rows]

    async def kill(self, pid: int, force: bool = False):
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)
            for child in children:
                child.terminate() if not force else child.kill()
            proc.terminate() if not force else proc.kill()
            gone, alive = psutil.wait_procs(children + [proc], timeout=3)
            for p in alive:
                p.kill()
        except psutil.NoSuchProcess:
            pass
        await self.db.execute("UPDATE processes SET status = 'stopped' WHERE pid = ?", (pid,))
        row = await self.db.fetchone("SELECT user_id FROM processes WHERE pid = ?", (pid,))
        if row:
            await self.db.execute(
                "UPDATE users SET running_processes = max(0, running_processes - 1) WHERE user_id = ?",
                (row["user_id"],)
            )
        return True, "🛑 প্রসেস বন্ধ করা হয়েছে।"

    async def cleanup_zombies(self):
        rows = await self.db.fetchall("SELECT pid, user_id FROM processes WHERE status = 'running'")
        for row in rows:
            if not psutil.pid_exists(row["pid"]):
                await self.db.execute("UPDATE processes SET status = 'zombie' WHERE pid = ?", (row["pid"],))
                await self.db.execute(
                    "UPDATE users SET running_processes = max(0, running_processes - 1) WHERE user_id = ?",
                    (row["user_id"],)
                )