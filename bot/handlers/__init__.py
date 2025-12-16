from aiogram import Router

from . import export_users, info, start, support, main_menu, common_nav
from .admins import admin_panel, test_prayer
from .sections import (
    islamic_router,
    profile_router,
    knowledge_router,
    education_router,
    prayer_schedule_router,
    halal_places_router,
    events_calendar_router,
    stubs_router,
    settings_router,
    test_taking_router,
    ai_assistant_router,
)


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(info.router)
    router.include_router(support.router)
    router.include_router(main_menu.router)
    router.include_router(common_nav.router)  # Высокий приоритет для навигации
    router.include_router(export_users.router)
    router.include_router(admin_panel)
    router.include_router(test_prayer)

    # Подключаем роутеры разделов
    router.include_router(islamic_router)
    router.include_router(profile_router)
    router.include_router(knowledge_router)
    router.include_router(education_router)
    router.include_router(prayer_schedule_router)
    router.include_router(halal_places_router)
    router.include_router(events_calendar_router)
    router.include_router(stubs_router)
    router.include_router(settings_router)
    router.include_router(test_taking_router)
    router.include_router(ai_assistant_router)

    return router
