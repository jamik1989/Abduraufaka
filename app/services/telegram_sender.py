from aiogram.types import InputMediaPhoto
from app.config import settings


def build_tme_c_link(chat_id: str, message_id: int) -> str:
    chat_id_str = str(chat_id)
    if chat_id_str.startswith("-100"):
        internal_id = chat_id_str[4:]
        return f"https://t.me/c/{internal_id}/{message_id}"
    return ""


async def send_visit_to_group(bot, payload, agent):
    if not settings.group_chat_id:
        return False, "GROUP_CHAT_ID kiritilmagan", []

    caption_text = (
        f"Bugungi sana : {payload['date_str']}\n"
        f"{payload['time_str']}\n"
        f"1. Адрес: {payload['address']}\n"
        f"2. Код клиента: {payload['client_code']}\n"
        f"3. Ориентир: {payload['landmark']}\n"
        f"4. Последняя прибытья аналитика: {payload['last_visit_date']}\n"
        f"5. Код стенда: {payload['stand_code']}\n"
        f"6. Комментария от клиента: {payload['client_comment']}\n"
        f"7. Заключение: {payload['conclusion']}\n"
        f"8. Аналитик: {agent.full_name}\n"
        f"9. Телефон: {agent.phone}"
    )

    media = [
        InputMediaPhoto(media=payload["stand_photo"]),
        InputMediaPhoto(media=payload["product_photo"]),
        InputMediaPhoto(media=payload["outside_photo"], caption=caption_text),
    ]

    sent_messages = await bot.send_media_group(
        chat_id=settings.group_chat_id,
        media=media
    )

    links = [
        build_tme_c_link(settings.group_chat_id, msg.message_id)
        for msg in sent_messages
    ]

    return True, "ok", links