from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings


def now_local():
    return datetime.now(ZoneInfo(settings.timezone))


def format_dt(dt: datetime) -> str:
    local = dt.replace(tzinfo=ZoneInfo(settings.timezone))
    return local.strftime("%d.%m.%Y %H:%M")


def normalize_phone(phone: str) -> str:
    p = "".join(ch for ch in phone if ch.isdigit() or ch == "+")

    digits = "".join(ch for ch in p if ch.isdigit())

    if p.startswith("+998") and len(digits) == 12:
        return "+998" + digits[-9:]

    if digits.startswith("998") and len(digits) == 12:
        return "+" + digits

    if len(digits) == 9:
        return "+998" + digits

    if p.startswith("+") and len(digits) >= 9:
        return p

    return phone.strip()
