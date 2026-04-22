import os
import aiofiles


class LogService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    async def create_log(self, user_id: int, script_name: str) -> str:
        import datetime
        d = os.path.join(self.base_dir, str(user_id))
        os.makedirs(d, exist_ok=True)
        fname = f"{script_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        path = os.path.join(d, fname)
        async with aiofiles.open(path, "w") as f:
            await f.write(f"# Log started {datetime.datetime.now().isoformat()}\n")
        return path

    async def read_tail(self, path: str, lines: int = 50) -> str:
        if not os.path.exists(path):
            return "❌ লগ পাওয়া যায়নি।"
        async with aiofiles.open(path, "r") as f:
            content = await f.read()
        all_lines = content.splitlines()
        return "\n".join(all_lines[-lines:])