from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database.crud import list_agents, count_today_visits_for_agent, get_today_shop_names_for_agent


def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    async def send_daily_reports():
        agents = list_agents()
        for agent in agents:
            if not agent.telegram_user_id:
                continue

            count = count_today_visits_for_agent(agent.id)
            shops = get_today_shop_names_for_agent(agent.id)

            text = (
                f"📊 <b>Bugungi hisobotingiz</b>\n\n"
                f"👤 Agent: {agent.full_name}\n"
                f"🏪 Bugun kiritilgan magazinlar soni: <b>{count}</b>\n"
            )

            if shops:
                text += "\n<b>Magazinlar:</b>\n" + "\n".join(f"• {x}" for x in shops[:15])

            try:
                await bot.send_message(chat_id=int(agent.telegram_user_id), text=text)
            except Exception:
                pass

    scheduler.add_job(
        send_daily_reports,
        CronTrigger(hour=20, minute=0, timezone=settings.timezone),
        id="daily_agent_report",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
