import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.database.db import Base, engine
from app.handlers import start, admin, auth, visit
from app.services.scheduler import setup_scheduler


async def runner():
    Base.metadata.create_all(bind=engine)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(auth.router)
    dp.include_router(visit.router)

    setup_scheduler(bot)

    await dp.start_polling(bot)


def main():
    asyncio.run(runner())
