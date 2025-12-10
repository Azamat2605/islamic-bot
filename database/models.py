from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Boolean, func, Text, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

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
    event_proposals: Mapped[list["EventProposal"]] = relationship("EventProposal", back_populates="user", foreign_keys="[EventProposal.user_id]")
    event_registrations: Mapped[list["EventRegistration"]] = relationship("EventRegistration", back_populates="user")
    created_events: Mapped[list["CommunityEvent"]] = relationship("CommunityEvent", back_populates="creator", foreign_keys="[CommunityEvent.created_by]")


class EventType(enum.Enum):
    LECTURE = "lecture"
    MEETING = "meeting"
    COURSE = "course"
    OTHER = "other"


class EventStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FINISHED = "finished"


class CommunityEvent(Base):
    __tablename__ = "community_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType, native_enum=False), default=EventType.LECTURE)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, native_enum=False), default=EventStatus.ACTIVE)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="event", cascade="all, delete-orphan"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])


class RegistrationStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_events.id"), nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus, native_enum=False), default=RegistrationStatus.CONFIRMED)
    registered_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="event_registrations")
    event: Mapped["CommunityEvent"] = relationship("CommunityEvent", back_populates="registrations")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='uq_user_event'),)


class ProposalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EventProposal(Base):
    __tablename__ = "event_proposals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus, native_enum=False), default=ProposalStatus.PENDING)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="event_proposals", foreign_keys=[user_id])
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewed_by])


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
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="settings")
