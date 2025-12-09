from aiogram import Router

from . import export_users, info, start, support, main_menu
from .admins import admin_panel
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
)


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(info.router)
    router.include_router(support.router)
    router.include_router(main_menu.router)
    router.include_router(export_users.router)
    router.include_router(admin_panel.router)

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

    return router
