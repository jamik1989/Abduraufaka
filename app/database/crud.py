from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, func

from app.config import settings
from app.database.db import SessionLocal
from app.database.models import Agent, Visit, VisitPhoto


def create_agent(full_name: str, phone: str, password: str):
    with SessionLocal() as db:
        existing = db.execute(
            select(Agent).where(Agent.phone == phone)
        ).scalar_one_or_none()

        if existing:
            return None

        agent = Agent(
            full_name=full_name,
            phone=phone,
            password=password,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent


def get_agent_by_phone(phone: str):
    with SessionLocal() as db:
        return db.execute(
            select(Agent).where(
                Agent.phone == phone,
                Agent.is_active == 1
            )
        ).scalar_one_or_none()


def get_agent_by_tg_id(tg_user_id: int):
    with SessionLocal() as db:
        return db.execute(
            select(Agent).where(
                Agent.telegram_user_id == str(tg_user_id),
                Agent.is_active == 1
            )
        ).scalar_one_or_none()


def bind_agent_telegram(agent_id: int, tg_user_id: int):
    with SessionLocal() as db:
        agent = db.get(Agent, agent_id)
        if not agent:
            return None
        agent.telegram_user_id = str(tg_user_id)
        db.commit()
        db.refresh(agent)
        return agent


def unbind_agent_telegram(tg_user_id: int):
    with SessionLocal() as db:
        agent = db.execute(
            select(Agent).where(Agent.telegram_user_id == str(tg_user_id))
        ).scalar_one_or_none()

        if not agent:
            return False

        agent.telegram_user_id = None
        db.commit()
        return True


def list_agents():
    with SessionLocal() as db:
        return db.execute(
            select(Agent).order_by(Agent.id.desc())
        ).scalars().all()


def create_visit(agent_id: int, shop_name: str, photos: list[dict]):
    with SessionLocal() as db:
        visit = Visit(
            agent_id=agent_id,
            shop_name=shop_name,
        )
        db.add(visit)
        db.flush()

        for item in photos:
            db.add(
                VisitPhoto(
                    visit_id=visit.id,
                    telegram_file_id=item["telegram_file_id"],
                    comment=item["comment"],
                )
            )

        db.commit()
        db.refresh(visit)
        return visit


def get_visit_with_photos(visit_id: int):
    with SessionLocal() as db:
        visit = db.get(Visit, visit_id)
        if visit:
            _ = visit.agent
            _ = visit.photos
        return visit


def count_today_visits_for_agent(agent_id: int):
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)

    start_naive = start_local.replace(tzinfo=None)
    end_naive = end_local.replace(tzinfo=None)

    with SessionLocal() as db:
        q = select(func.count(Visit.id)).where(
            Visit.agent_id == agent_id,
            Visit.created_at >= start_naive,
            Visit.created_at < end_naive,
        )
        return db.execute(q).scalar_one()


def get_today_shop_names_for_agent(agent_id: int):
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)

    start_naive = start_local.replace(tzinfo=None)
    end_naive = end_local.replace(tzinfo=None)

    with SessionLocal() as db:
        q = select(Visit.shop_name).where(
            Visit.agent_id == agent_id,
            Visit.created_at >= start_naive,
            Visit.created_at < end_naive,
        ).order_by(Visit.id.desc())
        return [x[0] for x in db.execute(q).all()]