from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏪 Yangi TT")],
            [KeyboardButton(text="📊 Bugungi hisobot")],
            [KeyboardButton(text="🚪 Chiqish")],
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Agent qo'shish")],
            [KeyboardButton(text="📋 Agentlar ro'yxati")],
        ],
        resize_keyboard=True
    )
