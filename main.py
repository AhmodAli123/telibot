import asyncio
import logging
from core.bot import bot, dp
from database.manager import Database
from config import Config
from keep_alive import keep_alive, init_public
from services.public_url_service import PublicURLService
from core.scheduler import start_background_tasks

# Routers
from handlers import user_handlers, file_handlers, execution_handlers
from handlers import subscription_handlers, marketplace_handlers, admin_handlers, common

logging.basicConfig(level=logging.INFO)

db = Database(Config.DB_PATH)


class DBMiddleware:
    """Inject database instance into every handler."""
    async def __call__(self, handler, event, data):
        data["db"] = db
        return await handler(event, data)


async def main():
    # 1. Database init
    await db.init()

    # 2. Load banned users into memory
    rows = await db.fetchall("SELECT user_id FROM bans")
    Config.BANNED_USERS = {r["user_id"] for r in rows}

    # 3. Middleware
    dp.message.middleware(DBMiddleware())
    dp.callback_query.middleware(DBMiddleware())

    # 4. Register handlers
    dp.include_router(user_handlers.router)
    dp.include_router(file_handlers.router)
    dp.include_router(execution_handlers.router)
    dp.include_router(subscription_handlers.router)
    dp.include_router(marketplace_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(common.router)

    # 5. Public URL & Keep-alive (Replit/Render compatible)
    pub = PublicURLService()
    init_public(pub)
    keep_alive(Config.WEB_PORT, Config.HOST)

    # 6. Background workers (Cron, Zombie cleaner, Auto-retry)
    await start_background_tasks(db)

    # 7. Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())