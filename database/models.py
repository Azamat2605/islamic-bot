from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Boolean, func, Text, Enum, UniqueConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
import json

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
    # Новые поля для обучения
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_courses_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    learning_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_learning_activity: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    settings: Mapped["Settings"] = relationship("Settings", back_populates="user", uselist=False)
    event_proposals: Mapped[list["EventProposal"]] = relationship("EventProposal", back_populates="user", foreign_keys="[EventProposal.user_id]")
    event_registrations: Mapped[list["EventRegistration"]] = relationship("EventRegistration", back_populates="user")
    created_events: Mapped[list["CommunityEvent"]] = relationship("CommunityEvent", back_populates="creator", foreign_keys="[CommunityEvent.created_by]")
    # Relationships для обучения
    course_progress: Mapped[list["UserCourseProgress"]] = relationship("UserCourseProgress", back_populates="user")
    module_progress: Mapped[list["UserModuleProgress"]] = relationship("UserModuleProgress", back_populates="user")
    test_results: Mapped[list["UserTestResult"]] = relationship("UserTestResult", back_populates="user")
    # Новые relationships
    stream_reminders: Mapped[list["StreamReminder"]] = relationship("StreamReminder", back_populates="user")
    certificates: Mapped[list["Certificate"]] = relationship("Certificate", back_populates="user")

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
    
    # Новые поля для уведомлений об обучении
    notify_course_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_test_results: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_courses: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Настройки обучения
    daily_learning_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_learning_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auto_continue_courses: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    user: Mapped["User"] = relationship("User", back_populates="settings")


# ==================== EDUCATION MODULE MODELS ====================

class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel, native_enum=False), default=CourseLevel.BEGINNER)
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus, native_enum=False), default=CourseStatus.PUBLISHED)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=10)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    modules: Mapped[list["CourseModule"]] = relationship(
        "CourseModule", back_populates="course", cascade="all, delete-orphan", order_by="CourseModule.order_index"
    )
    user_progress: Mapped[list["UserCourseProgress"]] = relationship(
        "UserCourseProgress", back_populates="course", cascade="all, delete-orphan"
    )
    tests: Mapped[list["Test"]] = relationship("Test", back_populates="course")
    certificates: Mapped[list["Certificate"]] = relationship("Certificate", back_populates="course")


class CourseModule(Base):
    __tablename__ = "course_modules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), default="text")
    content_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=15)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    # Новые поля для связи с тестами
    has_test: Mapped[bool] = mapped_column(Boolean, default=False)
    test_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tests.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="modules")
    user_progress: Mapped[list["UserModuleProgress"]] = relationship(
        "UserModuleProgress", back_populates="module", cascade="all, delete-orphan"
    )
    test: Mapped["Test"] = relationship("Test", foreign_keys=[test_id])


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    completed_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    total_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)  # Новое поле
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course", back_populates="user_progress")
    module_progress: Mapped[list["UserModuleProgress"]] = relationship(
        "UserModuleProgress", back_populates="course_progress", cascade="all, delete-orphan"
    )
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course'),)


class UserModuleProgress(Base):
    __tablename__ = "user_module_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("course_modules.id"), nullable=False)
    course_progress_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_course_progress.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="not_started")
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    module: Mapped["CourseModule"] = relationship("CourseModule", back_populates="user_progress")
    course_progress: Mapped["UserCourseProgress"] = relationship(
        "UserCourseProgress", back_populates="module_progress", foreign_keys=[course_progress_id]
    )
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'module_id', name='uq_user_module'),)


class Test(Base):
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id"), nullable=True)
    module_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("course_modules.id"), nullable=True)  # Новое поле
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_score: Mapped[int] = mapped_column(Integer, default=70)
    max_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="tests")
    module: Mapped["CourseModule"] = relationship("CourseModule", foreign_keys=[module_id])
    questions: Mapped[list["TestQuestion"]] = relationship(
        "TestQuestion", back_populates="test", cascade="all, delete-orphan", order_by="TestQuestion.order_index"
    )
    user_results: Mapped[list["UserTestResult"]] = relationship(
        "UserTestResult", back_populates="test", cascade="all, delete-orphan"
    )


class TestQuestion(Base):
    __tablename__ = "test_questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="single_choice")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="questions")
    options: Mapped[list["TestOption"]] = relationship(
        "TestOption", back_populates="question", cascade="all, delete-orphan", order_by="TestOption.order_index"
    )


class TestOption(Base):
    __tablename__ = "test_options"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    question: Mapped["TestQuestion"] = relationship("TestQuestion", back_populates="options")


class UserTestResult(Base):
    __tablename__ = "user_test_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    test: Mapped["Test"] = relationship("Test", back_populates="user_results")
    answers: Mapped[list["UserTestAnswer"]] = relationship(
        "UserTestAnswer", back_populates="test_result", cascade="all, delete-orphan"
    )
    
    # Unique constraint для попытки
    __table_args__ = (UniqueConstraint('user_id', 'test_id', 'attempt_number', name='uq_user_test_attempt'),)


class UserTestAnswer(Base):
    __tablename__ = "user_test_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_result_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_test_results.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_questions.id"), nullable=False)
    selected_option_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    points_earned: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    test_result: Mapped["UserTestResult"] = relationship("UserTestResult", back_populates="answers")
    question: Mapped["TestQuestion"] = relationship("TestQuestion")


# ==================== STREAM MODELS ====================

class Stream(Base):
    __tablename__ = "streams"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    speaker: Mapped[str] = mapped_column(String(100), nullable=True)
    scheduled_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    stream_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_upcoming: Mapped[bool] = mapped_column(Boolean, default=True)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    reminders: Mapped[list["StreamReminder"]] = relationship(
        "StreamReminder", back_populates="stream", cascade="all, delete-orphan"
    )


class StreamReminder(Base):
    __tablename__ = "stream_reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    stream_id: Mapped[int] = mapped_column(Integer, ForeignKey("streams.id"), nullable=False)
    reminded_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="stream_reminders")
    stream: Mapped["Stream"] = relationship("Stream", back_populates="reminders")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'stream_id', name='uq_user_stream_reminder'),)


# ==================== CERTIFICATE MODEL ====================

class Certificate(Base):
    __tablename__ = "certificates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    certificate_url: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="certificates")
    course: Mapped["Course"] = relationship("Course", back_populates="certificates")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course_certificate'),)
