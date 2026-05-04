from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.crud import get_agent_by_phone, bind_agent_telegram
from app.keyboards.reply import main_menu
from app.states import LoginStates
from app.utils.helpers import normalize_phone

router = Router()


@router.message(LoginStates.waiting_phone)
async def login_phone(message: Message, state: FSMContext):
    phone = normalize_phone(message.text.strip())
    await state.update_data(phone=phone)
    await message.answer("Parolni kiriting:")
    await state.set_state(LoginStates.waiting_password)


@router.message(LoginStates.waiting_password)
async def login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    password = message.text.strip()

    agent = get_agent_by_phone(phone)
    if not agent or agent.password != password:
        await message.answer("Telefon yoki parol noto'g'ri. Qaytadan /start bosing.")
        await state.clear()
        return

    bind_agent_telegram(agent.id, message.from_user.id)
    await message.answer(
        f"Muvaffaqiyatli kirildi.\n\n👤 {agent.full_name}\n📞 {agent.phone}",
        reply_markup=main_menu()
    )
    await state.clear()
