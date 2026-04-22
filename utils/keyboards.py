from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(is_admin: bool = False):
    buttons = [
        [KeyboardButton(text="📁 ফাইল ম্যানেজার"), KeyboardButton(text="▶️ স্ক্রিপ্ট রান")],
        [KeyboardButton(text="📊 ড্যাশবোর্ড"), KeyboardButton(text="⏱️ ক্রন জবস")],
        [KeyboardButton(text="🛒 মার্কেটপ্লেস"), KeyboardButton(text="⚙️ সেটিংস")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="🛠️ অ্যাডমিন প্যানেল")])
    buttons.append([KeyboardButton(text="❓ সাহায্য")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def back_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ পেছনে")]],
        resize_keyboard=True
    )


def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ হ্যাঁ"), KeyboardButton(text="❌ না")]],
        resize_keyboard=True
    )


# শুধুমাত্র বিশেষ প্রয়োজনে (ফাইল স্পেসিফিক অ্যাকশন) ইনলাইন ব্যবহার
def file_inline_actions(file_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑️ ডিলিট", callback_data=f"del:{file_id}"),
            InlineKeyboardButton(text="▶️ রান", callback_data=f"run:{file_id}")
        ],
        [
            InlineKeyboardButton(text="📜 লগ", callback_data=f"log:{file_id}")
        ]
    ])