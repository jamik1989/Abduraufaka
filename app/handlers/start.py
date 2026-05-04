from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.database.crud import get_agent_by_tg_id
from app.keyboards.reply import main_menu, admin_menu
from app.states import LoginStates

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()

    if message.from_user.id in settings.admin_id_list:
        await message.answer(
            "Admin paneliga xush kelibsiz.",
            reply_markup=admin_menu()
        )
        return

    agent = get_agent_by_tg_id(message.from_user.id)
    if agent:
        await message.answer(
            f"Xush kelibsiz, {agent.full_name}.",
            reply_markup=main_menu()
        )
        return

    await message.answer("Telefon raqamingizni kiriting. Misol: +998901234567")
    await state.set_state(LoginStates.waiting_phone)
