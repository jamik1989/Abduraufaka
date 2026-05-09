import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.database.crud import (
    get_agent_by_tg_id,
    count_today_visits_for_agent,
    unbind_agent_telegram,
)
from app.keyboards.inline import confirm_visit_kb
from app.keyboards.reply import main_menu
from app.services.panel_sender import send_report_to_panel
from app.services.telegram_sender import send_visit_to_group
from app.states import VisitStates

router = Router()


def now_local():
    return datetime.now(ZoneInfo(settings.timezone))


def is_report_text(text: str) -> bool:
    return "Bugungi hisobot" in text


def is_logout_text(text: str) -> bool:
    return "Chiqish" in text


def is_new_visit_text(text: str) -> bool:
    return "Yangi TT" in text


async def handle_menu_interrupt(message: Message, state: FSMContext) -> bool:
    text = (message.text or "").strip()

    if is_report_text(text):
        agent = get_agent_by_tg_id(message.from_user.id)
        await state.clear()
        if not agent:
            await message.answer("Avval login qiling. /start")
            return True

        count = count_today_visits_for_agent(agent.id)
        await message.answer(
            f"📊 Bugungi hisobotingiz\n\n"
            f"👤 {agent.full_name}\n"
            f"🧾 Kiritilgan so'rovnomalar soni: <b>{count}</b>"
        )
        return True

    if is_logout_text(text):
        await state.clear()
        unbind_agent_telegram(message.from_user.id)
        await message.answer("Siz tizimdan chiqdingiz.\n\nQayta kirish uchun /start bosing.")
        return True

    return False


async def finalize_background(bot, report_data, photos_payload, agent):
    photo_links = ["", "", ""]

    try:
        group_ok, group_msg, photo_links = await send_visit_to_group(
            bot=bot,
            payload={**report_data, **photos_payload},
            agent=agent,
        )
        print("GROUP RESULT:", group_ok, group_msg)
    except Exception as e:
        print("GROUP ERROR:", e)

    try:
        panel_ok, panel_msg = await asyncio.to_thread(
            send_report_to_panel,
            report_data,
            agent,
            photo_links,
        )
        print("PANEL RESULT:", panel_ok, panel_msg)
    except Exception as e:
        print("PANEL ERROR:", e)


@router.message(F.text.contains("Bugungi hisobot"))
async def today_report(message: Message, state: FSMContext):
    await handle_menu_interrupt(message, state)


@router.message(F.text.contains("Chiqish"))
async def logout_info(message: Message, state: FSMContext):
    await handle_menu_interrupt(message, state)


@router.message(F.text.contains("Yangi TT"))
async def new_visit_start(message: Message, state: FSMContext):
    agent = get_agent_by_tg_id(message.from_user.id)
    if not agent:
        await state.clear()
        await message.answer("Avval login qiling. /start")
        return

    current_state = await state.get_state()

    if current_state is not None:
        return

    await state.clear()
    await state.set_state(VisitStates.waiting_address)
    await message.answer("Адрес:")


@router.message(VisitStates.waiting_address)
async def get_address(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(address=message.text.strip())
    await state.set_state(VisitStates.waiting_landmark)
    await message.answer("Ориентир:")


@router.message(VisitStates.waiting_landmark)
async def get_landmark(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(landmark=message.text.strip())
    await state.set_state(VisitStates.waiting_client_code)
    await message.answer("Код клиента:")


@router.message(VisitStates.waiting_client_code)
async def get_client_code(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(client_code=message.text.strip())
    await state.set_state(VisitStates.waiting_last_visit_date)
    await message.answer("Последний прибытия торгового агента: (дата)")


@router.message(VisitStates.waiting_last_visit_date)
async def get_last_visit_date(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(last_visit_date=message.text.strip())
    await state.set_state(VisitStates.waiting_stand_code)
    await message.answer("Код стенда:")


@router.message(VisitStates.waiting_stand_code)
async def get_stand_code(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(stand_code=message.text.strip())
    await state.set_state(VisitStates.waiting_client_comment)
    await message.answer("Комментарии от клиента:")


@router.message(VisitStates.waiting_client_comment)
async def get_client_comment(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(client_comment=message.text.strip())
    await state.set_state(VisitStates.waiting_conclusion)
    await message.answer("Заключение:")


@router.message(VisitStates.waiting_conclusion)
async def get_conclusion(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await state.update_data(conclusion=message.text.strip())
    await state.set_state(VisitStates.waiting_stand_photo)
    await message.answer("Фото стенда:")


@router.message(VisitStates.waiting_stand_photo, F.photo)
async def get_stand_photo(message: Message, state: FSMContext):
    await state.update_data(stand_photo=message.photo[-1].file_id)
    await state.set_state(VisitStates.waiting_product_photo)
    await message.answer("Фото махсулот:")


@router.message(VisitStates.waiting_stand_photo)
async def get_stand_photo_invalid(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await message.answer("Iltimos, rasm yuboring.")


@router.message(VisitStates.waiting_product_photo, F.photo)
async def get_product_photo(message: Message, state: FSMContext):
    await state.update_data(product_photo=message.photo[-1].file_id)
    await state.set_state(VisitStates.waiting_outside_photo)
    await message.answer("Фото ташкари:")


@router.message(VisitStates.waiting_product_photo)
async def get_product_photo_invalid(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await message.answer("Iltimos, rasm yuboring.")


@router.message(VisitStates.waiting_outside_photo, F.photo)
async def get_outside_photo(message: Message, state: FSMContext):
    await state.update_data(outside_photo=message.photo[-1].file_id)

    data = await state.get_data()
    preview = (
        "<b>Текширув</b>\n\n"
        f"📍 Адрес: {data['address']}\n"
        f"🧭 Ориентир: {data['landmark']}\n"
        f"🆔 Код клиента: {data['client_code']}\n"
        f"📅 Последний прибытия торгового агента: {data['last_visit_date']}\n"
        f"🏷 Код стенда: {data['stand_code']}\n"
        f"💬 Комментарии от клиента: {data['client_comment']}\n"
        f"📝 Заключение: {data['conclusion']}\n\n"
        "Юборилсинми?"
    )
    await state.set_state(VisitStates.confirm)
    await message.answer(preview, reply_markup=confirm_visit_kb())


@router.message(VisitStates.waiting_outside_photo)
async def get_outside_photo_invalid(message: Message, state: FSMContext):
    if await handle_menu_interrupt(message, state):
        return
    await message.answer("Iltimos, rasm yuboring.")


@router.callback_query(F.data == "visit_cancel")
async def cancel_visit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.message.answer("Asosiy menyu", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "visit_send")
async def send_visit(callback: CallbackQuery, state: FSMContext, bot):
    agent = get_agent_by_tg_id(callback.from_user.id)
    if not agent:
        await callback.answer("Login kerak", show_alert=True)
        return

    data = await state.get_data()
    now = now_local()

    report_data = {
        "address": data["address"],
        "landmark": data["landmark"],
        "client_code": data["client_code"],
        "last_visit_date": data["last_visit_date"],
        "stand_code": data["stand_code"],
        "client_comment": data["client_comment"],
        "conclusion": data["conclusion"],
        "date_str": now.strftime("%d.%m.%Y"),
        "time_str": now.strftime("%H:%M"),
    }

    photos_payload = {
        "stand_photo": data["stand_photo"],
        "product_photo": data["product_photo"],
        "outside_photo": data["outside_photo"],
    }

    today_count = count_today_visits_for_agent(agent.id) + 1

    await callback.message.edit_text(
        "✅ Qabul qilindi.\n\n"
        f"📍 Адрес: {report_data['address']}\n"
        f"📊 Bugungi TT soni: {today_count}\n\n"
        "Guruh va Panelga yuborilmoqda..."
    )
    await callback.message.answer("Asosiy menyu", reply_markup=main_menu())

    await state.clear()
    await callback.answer()

    asyncio.create_task(finalize_background(bot, report_data, photos_payload, agent))