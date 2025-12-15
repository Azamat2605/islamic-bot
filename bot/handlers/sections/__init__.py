from .islamic_handlers import router as islamic_router
from .profile_handlers import router as profile_router
from .knowledge_handlers import router as knowledge_router
from .education_handlers import router as education_router
from .prayer_schedule_handlers import router as prayer_schedule_router
from .halal_places_handlers import router as halal_places_router
from .events_calendar_handlers import router as events_calendar_router
from .stubs import router as stubs_router
from .settings_handlers import router as settings_router
from .test_handlers import router as test_taking_router
from .ai_assistant import router as ai_assistant_router

__all__ = [
    "islamic_router",
    "profile_router",
    "knowledge_router",
    "education_router",
    "prayer_schedule_router",
    "halal_places_router",
    "events_calendar_router",
    "stubs_router",
    "settings_router",
    "test_taking_router",
    "ai_assistant_router",
]
