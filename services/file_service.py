import os
import sys
import asyncio
import zipfile
import aiofiles
from config import Config
from database.manager import Database


class FileService:
    def __init__(self, storage_base: str, db: Database):
        self.storage_base = storage_base
        self.db = db

    def _user_dir(self, user_id: int) -> str:
        d = os.path.join(self.storage_base, str(user_id))
        os.makedirs(d, exist_ok=True)
        os.makedirs(os.path.join(d, "logs"), exist_ok=True)
        return d

    async def save_file(self, user_id: int, filename: str, content: bytes):
        user_dir = self._user_dir(user_id)
        filepath = os.path.join(user_dir, filename)

        if len(content) > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, "❌ ফাইল সাইজ সীমা অতিক্রম করেছে।"

        # Storage quota check
        from services.subscription_service import SubscriptionService
        plan = await SubscriptionService(self.db).get_plan(user_id)
        current = await self._calc_storage(user_dir)
        if current + len(content) > plan["max_storage_mb"] * 1024 * 1024:
            return False, "❌ স্টোরেজ লিমিট পূর্ণ।"

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        if filename.lower().endswith(".zip"):
            await self._extract_zip(user_dir, filepath)

        await self._auto_deps(user_dir)

        await self.db.execute(
            "INSERT INTO files (user_id, filename, size) VALUES (?, ?, ?)",
            (user_id, filename, len(content))
        )
        await self.db.execute(
            "UPDATE users SET total_files = total_files + 1 WHERE user_id = ?", (user_id,)
        )
        return True, "✅ আপলোড সফল।"

    async def list_files(self, user_id: int):
        rows = await self.db.fetchall(
            "SELECT id, filename, size, uploaded_at FROM files WHERE user_id = ?", (user_id,)
        )
        return [dict(r) for r in rows]

    async def delete_file(self, user_id: int, file_id: int):
        row = await self.db.fetchone(
            "SELECT filename FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)
        )
        if not row:
            return False
        fpath = os.path.join(self._user_dir(user_id), row["filename"])
        if os.path.exists(fpath):
            os.remove(fpath)
        await self.db.execute("DELETE FROM files WHERE id = ?", (file_id,))
        await self.db.execute(
            "UPDATE users SET total_files = max(0, total_files - 1) WHERE user_id = ?", (user_id,)
        )
        return True

    async def _calc_storage(self, directory: str) -> int:
        total = 0
        for root, _, files in os.walk(directory):
            for f in files:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
        return total

    async def _extract_zip(self, user_dir: str, zip_path: str):
        def _extract():
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(user_dir)
        await asyncio.to_thread(_extract)

    async def _auto_deps(self, user_dir: str):
        req = os.path.join(user_dir, "requirements.txt")
        pkg = os.path.join(user_dir, "package.json")
        if os.path.exists(req):
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", "-r", req, "--user", "-q",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        if os.path.exists(pkg):
            proc = await asyncio.create_subprocess_exec(
                "npm", "install", cwd=user_dir,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()