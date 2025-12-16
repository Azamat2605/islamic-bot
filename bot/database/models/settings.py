from __future__ import annotations

from sqlalchemy import ForeignKey, String, Boolean, DateTime, Integer, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
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
    
    # Поля для уведомлений о намазах
    notify_fajr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_dhuhr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_asr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_maghrib: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_isha: Mapped[bool] = mapped_column(Boolean, default=True)
    madhab: Mapped[str] = mapped_column(String, default="Hanafi")  # Hanafi, Shafi, Maliki, Hanbali
    
    # Новые поля для уведомлений о религиозных событиях
    notify_1day_before: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_day: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_juma: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Поля для уведомлений о мероприятиях
    notify_event_reminder: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_event_changes: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Новые поля для уведомлений об обучении
    notify_course_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_test_results: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_courses: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Настройки обучения
    daily_learning_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_learning_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auto_continue_courses: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="settings")
