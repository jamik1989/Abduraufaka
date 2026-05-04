from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.database.crud import create_agent, list_agents
from app.keyboards.reply import admin_menu
from app.states import AdminStates
from app.utils.helpers import normalize_phone

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list


@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Siz admin emassiz.")
        return
    await message.answer(
        "Admin panel\n\n"
        "Agent qo'shish uchun:\n"
        "/add_agent",
        reply_markup=admin_menu()
    )


@router.message(
    F.text.in_([
        "➕ Agent qo'shish",
        "Agent qo'shish",
        "Agent qoshish",
        "agent qo'shish",
        "agent qoshish",
        "/add_agent",
    ])
)
async def add_agent_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Siz admin emassiz.")
        return

    await state.clear()
    await message.answer("Agent ismini kiriting:")
    await state.set_state(AdminStates.waiting_agent_name)


@router.message(AdminStates.waiting_agent_name)
async def add_agent_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(full_name=message.text.strip())
    await message.answer("Agent telefon raqamini kiriting. Misol: +998901234567")
    await state.set_state(AdminStates.waiting_agent_phone)


@router.message(AdminStates.waiting_agent_phone)
async def add_agent_phone(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    phone = normalize_phone(message.text.strip())
    await state.update_data(phone=phone)
    await message.answer("Agent parolini kiriting:")
    await state.set_state(AdminStates.waiting_agent_password)


@router.message(AdminStates.waiting_agent_password)
async def add_agent_password(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    full_name = data["full_name"]
    phone = data["phone"]
    password = message.text.strip()

    agent = create_agent(full_name, phone, password)
    if not agent:
        await message.answer("Bu telefon raqam bilan agent allaqachon mavjud.")
        await state.clear()
        return

    await message.answer(
        f"Agent saqlandi.\n\n"
        f"👤 {agent.full_name}\n"
        f"📞 {agent.phone}\n"
        f"🔑 {agent.password}",
        reply_markup=admin_menu()
    )
    await state.clear()


@router.message(
    F.text.in_([
        "📋 Agentlar ro'yxati",
        "Agentlar ro'yxati",
        "agentlar ro'yxati",
        "/agents",
    ])
)
async def agents_list(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Siz admin emassiz.")
        return

    agents = list_agents()
    if not agents:
        await message.answer("Agentlar hozircha yo'q.")
        return

    lines = ["<b>Agentlar ro'yxati</b>\n"]
    for idx, agent in enumerate(agents, start=1):
        linked = "✅" if agent.telegram_user_id else "❌"
        lines.append(f"{idx}. {agent.full_name} | {agent.phone} | Bog'langan: {linked}")

    await message.answer("\n".join(lines), reply_markup=admin_menu())
