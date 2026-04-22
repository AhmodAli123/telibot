import os
import sys
import asyncio
import aiofiles
from datetime import datetime
from config import Config
from database.manager import Database
from utils.sandbox import Sandbox


class ExecutionService:
    def __init__(self, db: Database, file_service, process_manager, log_service, dependency_service):
        self.db = db
        self.file_service = file_service
        self.pm = process_manager
        self.log_service = log_service
        self.dep_service = dependency_service

    async def run_script(self, user_id: int, script_name: str, env_port: int | None = None):
        user_dir = self.file_service._user_dir(user_id)
        script_path = os.path.join(user_dir, script_name)
        if not os.path.exists(script_path):
            return False, "❌ স্ক্রিপ্ট পাওয়া যায়নি।"

        # Process limit check
        from services.subscription_service import SubscriptionService
        ok, msg = await SubscriptionService(self.db).check_limits(user_id, procs=1)
        if not ok:
            return False, msg

        # Detect language
        if script_name.endswith(".py"):
            cmd = [sys.executable, script_path]
            lang = "python"
        elif script_name.endswith(".js"):
            cmd = ["node", script_path]
            lang = "node"
        else:
            return False, "❌ অসমর্থিত ফরম্যাট।"

        # Dependency auto-fix
        await self.dep_service.resolve(user_dir, lang)

        # Log file
        log_path = await self.log_service.create_log(user_id, script_name)

        # Environment
        env = os.environ.copy()
        env["USER_ID"] = str(user_id)
        env["WORK_DIR"] = user_dir
        env["PYTHONPATH"] = user_dir
        if env_port:
            env["PORT"] = str(env_port)
            env["PLATFORM_PORT"] = str(env_port)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=user_dir,
                env=env,
                preexec_fn=Sandbox.preexec_fn if hasattr(os, "setsid") else None
            )
        except Exception as e:
            return False, f"❌ এক্সিকিউশন ত্রুটি: {e}"

        await self.pm.register(proc.pid, user_id, script_name, log_path, env_port)
        asyncio.create_task(self._pipe_logs(proc, log_path))
        return True, f"▶️ স্ক্রিপ্ট চালু। PID: <code>{proc.pid}</code>"

    async def _pipe_logs(self, proc, log_path: str):
        async with aiofiles.open(log_path, "a") as logf:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                await logf.write(f"[{datetime.now().isoformat()}] {line.decode()}")
                await logf.flush()
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                await logf.write(f"[{datetime.now().isoformat()}] [ERR] {line.decode()}")
                await logf.flush()
        await proc.wait()
        await self.pm.mark_stopped(proc.pid)