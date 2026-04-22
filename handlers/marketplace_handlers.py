from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.manager import Database
from services.marketplace_service import MarketplaceService
from utils.decorators import banned_check
import html

router = Router()


@router.message(Command("market"))
@banned_check
async def market_list(message: Message, db: Database):
    mk = MarketplaceService(db)
    items = await mk.list_items()
    if not items:
        await message.answer("🛒 বর্তমানে কোনো টেমপ্লেট নেই।")
        return
    for item in items[:5]:
        price = "🆓 ফ্রি" if item["price"] == 0 else f"💎 {item['price']} coin"
        await message.answer(
            f"📦 <b>{html.escape(item['title'])}</b>\n"
            f"{html.escape(item['description'] or '')}\n"
            f"{price}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 কোড দেখুন", callback_data=f"mkview:{item['id']}")],
                [InlineKeyboardButton(text="📥 ডাউনলোড", callback_data=f"mkdl:{item['id']}")],
            ])
        )


@router.callback_query(F.data.startswith("mkview:"))
async def cb_market_view(callback: CallbackQuery, db: Database):
    item_id = int(callback.data.split(":")[1])
    mk = MarketplaceService(db)
    item = await mk.get_item(item_id)
    if not item:
        return await callback.answer("পাওয়া যায়নি!")
    code = html.escape(item["code"][:3000])
    await callback.message.answer(f"📝 <b>কোড:</b>\n<pre>{code}</pre>")
    await callback.answer()


@router.callback_query(F.data.startswith("mkdl:"))
async def cb_market_dl(callback: CallbackQuery, db: Database):
    item_id = int(callback.data.split(":")[1])
    mk = MarketplaceService(db)
    item = await mk.get_item(item_id)
    if not item:
        return await callback.answer("পাওয়া যায়নি!")
    # Save to user directory
    from services.file_service import FileService
    from config import Config
    fs = FileService(Config.STORAGE_BASE, db)
    fname = f"market_{item['title'].replace(' ', '_')}.py"
    await fs.save_file(callback.from_user.id, fname, item["code"].encode())
    await callback.answer("📥 ডাউনলোড সম্পূর্ণ!")
    await callback.message.answer("✅ ফাইল আপনার স্টোরেজে যোগ হয়েছে।")


@router.message(Command("publish"))
@banned_check
async def publish_item(message: Message, db: Database):
    args = message.text.replace("/publish", "").strip()
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 4:
        return await message.answer(
            "📤 ব্যবহার:\n/publish Title | Description | Price | Code\n"
            "যেমন: /publish HelloBot | A greet bot | 0 | print('Hi')"
        )
    title, desc, price_str, code = parts[0], parts[1], parts[2], parts[3]
    try:
        price = int(price_str)
    except ValueError:
        price = 0
    mk = MarketplaceService(db)
    await mk.publish(message.from_user.id, title, desc, code, price)
    await message.answer("✅ মার্কেটপ্লেসে পাবলিশ হয়েছে!")