import os
import asyncio


class GitService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    async def clone(self, user_id: int, repo_url: str):
        user_dir = os.path.join(self.base_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", repo_url, user_dir,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return True, "✅ Git clone সফল।"
        return False, f"❌ Git Error:\n{stderr.decode()[:1000]}"