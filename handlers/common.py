from aiogram import Router, F
from aiogram.types import Message
from config import Config
from utils.keyboards import main_menu

router = Router()


@router.message(F.text == "◀️ পেছনে")
@router.message(F.text == "◀️ মেইন মেনু")
async def go_back(message: Message):
    is_admin = message.from_user.id in Config.ADMIN_IDS
    await message.answer("🏠 মেইন মেনু", reply_markup=main_menu(is_admin))