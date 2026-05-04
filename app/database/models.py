from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.db import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    telegram_user_id = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    visits = relationship("Visit", back_populates="agent")


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    shop_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="visits")
    photos = relationship("VisitPhoto", back_populates="visit", cascade="all, delete-orphan")


class VisitPhoto(Base):
    __tablename__ = "visit_photos"

    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    telegram_file_id = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)

    visit = relationship("Visit", back_populates="photos")
