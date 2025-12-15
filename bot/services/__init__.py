"""
Сервисный слой приложения.
"""

from bot.services.analytics import AnalyticsService, analytics
from bot.services.calendar_service import HijriCalendarService
from bot.services.education_service import EducationService
from bot.services.event_service import EventService
from bot.services.halal_service import HalalService, haversine_distance
from bot.services.prayer_service import PrayerService
from bot.services.scheduler import scheduler, setup_scheduler, start_scheduler, stop_scheduler, set_bot_instance
from bot.services.stats_service import StatsService

__all__ = [
    "AnalyticsService",
    "analytics",
    "HijriCalendarService",
    "EducationService",
    "EventService",
    "HalalService",
    "haversine_distance",
    "PrayerService",
    "scheduler",
    "setup_scheduler",
    "start_scheduler",
    "stop_scheduler",
    "set_bot_instance",
    "StatsService",
]
