import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x]
    DB_PATH: str = os.getenv("DB_PATH", "data/platform.db")
    STORAGE_BASE: str = os.getenv("STORAGE_BASE", "storage/users")
    LOGS_BASE: str = os.getenv("LOGS_BASE", "storage/logs")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    WEB_PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEFAULT_PLAN: str = "free"

    PLANS: dict[str, dict] = {
        "free": {
            "max_files": 10, "max_processes": 1, "max_storage_mb": 100,
            "can_git": False, "can_public_url": False
        },
        "premium": {
            "max_files": 50, "max_processes": 3, "max_storage_mb": 500,
            "can_git": True, "can_public_url": True
        },
        "pro": {
            "max_files": 200, "max_processes": 10, "max_storage_mb": 2000,
            "can_git": True, "can_public_url": True
        },
    }

    MAINTENANCE_MODE: bool = False
    BANNED_USERS: set[int] = set()