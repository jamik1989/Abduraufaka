from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_visit_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yuborish", callback_data="visit_send"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="visit_cancel"),
            ]
        ]
    )
