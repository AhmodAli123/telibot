from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import Config

bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()