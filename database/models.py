from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    settings: Mapped["Settings"] = relationship("Settings", back_populates="user", uselist=False)


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True)
    language: Mapped[str] = mapped_column(String, default="ru")
    notification_on: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Новые поля для масштабируемости
    timezone: Mapped[str] = mapped_column(String, default="Europe/Moscow")  # IANA timezone
    date_format: Mapped[str] = mapped_column(String, default="DD.MM.YYYY")  # 'DD.MM.YYYY' или 'MM/DD/YYYY'
    time_format: Mapped[bool] = mapped_column(Boolean, default=True)  # True=24h, False=12h
    prayer_notifications_on: Mapped[bool] = mapped_column(Boolean, default=True)
    event_notifications_on: Mapped[bool] = mapped_column(Boolean, default=True)
    data_export_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    account_deletion_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="settings")
