import asyncio
from config import Config
from database.manager import Database
from services.cron_service import CronService
from services.execution_service import ExecutionService
from services.file_service import FileService
from services.process_manager import ProcessManager
from services.log_service import LogService
from services.dependency_service import DependencyService


async def start_background_tasks(db: Database):
    """Initialize background workers: cron & zombie cleaner."""
    fs = FileService(Config.STORAGE_BASE, db)
    pm = ProcessManager(db)
    ls = LogService(Config.LOGS_BASE)
    ds = DependencyService(db)
    exec_svc = ExecutionService(db, fs, pm, ls, ds)

    # Cron worker
    cron = CronService(db, exec_svc)
    asyncio.create_task(cron.run_loop())

    # Zombie process cleaner every 5 min
    async def zombie_loop():
        while True:
            await asyncio.sleep(300)
            await pm.cleanup_zombies()

    asyncio.create_task(zombie_loop())