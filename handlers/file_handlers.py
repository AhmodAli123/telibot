from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from io import BytesIO
from database.manager import Database
from services.file_service import FileService
from utils.decorators import banned_check
from utils.keyboards import back_button, file_inline_actions
from config import Config
from core.bot import bot
import html

router = Router()


@router.message(F.text == "📁 ফাইল ম্যানেজার")
@banned_check
async def file_manager(message: Message, db: Database):
    svc = FileService(Config.STORAGE_BASE, db)
    files = await svc.list_files(message.from_user.id)
    if not files:
        await message.answer("📂 কোনো ফাইল নেই। .py / .js / .zip আপলোড করুন।", reply_markup=back_button())
        return
    await message.answer(f"📁 মোট {len(files)}টি ফাইল।", reply_markup=back_button())
    for f in files[:5]:
        await message.answer(
            f"📄 <b>{html.escape(f['filename'])}</b> ({f['size']} bytes)",
            reply_markup=file_inline_actions(f["id"])
        )


@router.message(F.document)
@banned_check
async def upload_file(message: Message, db: Database):
    if not message.document:
        return
    doc = message.document
    fname = doc.file_name or "unnamed"
    if not any(fname.endswith(ext) for ext in [".py", ".js", ".zip", ".txt"]):
        await message.answer("❌ শুধু .py / .js / .zip / .txt")
        return

    file_info = await bot.get_file(doc.file_id)
    bio = await bot.download_file(file_info.file_path, BytesIO())
    data = bio.read()

    svc = FileService(Config.STORAGE_BASE, db)
    ok, msg = await svc.save_file(message.from_user.id, fname, data)
    await message.answer(msg, reply_markup=back_button())


@router.callback_query(F.data.startswith("del:"))
async def cb_delete(callback: CallbackQuery, db: Database):
    fid = int(callback.data.split(":")[1])
    svc = FileService(Config.STORAGE_BASE, db)
    ok = await svc.delete_file(callback.from_user.id, fid)
    await callback.answer("🗑️ ডিলিট হয়েছে" if ok else "❌ ব্যর্থ", show_alert=True)
    if ok and callback.message:
        await callback.message.delete()