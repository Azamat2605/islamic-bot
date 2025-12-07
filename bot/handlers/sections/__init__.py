from .islamic_handlers import router as islamic_router
from .profile_handlers import router as profile_router
from .knowledge_handlers import router as knowledge_router
from .education_handlers import router as education_router
from .prayer_schedule_handlers import router as prayer_schedule_router
from .halal_places_handlers import router as halal_places_router
from .events_calendar_handlers import router as events_calendar_router

__all__ = [
    "islamic_router",
    "profile_router",
    "knowledge_router",
    "education_router",
    "prayer_schedule_router",
    "halal_places_router",
    "events_calendar_router",
]
