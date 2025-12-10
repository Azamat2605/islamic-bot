from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from database.crud import get_user_by_telegram_id, get_user_settings
from aiogram.utils.i18n import gettext as _

router = Router(name="test_prayer")


@router.message(Command("test_notify"), AdminFilter())
async def cmd_test_notify(
    message: types.Message,
    session: AsyncSession,
    command: CommandObject | None = None,
) -> None:
    """Тестовая команда для проверки уведомлений о намазах"""
    try:
        # Получаем пользователя и его настройки
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer(_("❌ Пользователь не найден в базе данных"))
            return
        
        settings = await get_user_settings(session, user.id)
        if not settings:
            await message.answer(_("❌ Настройки пользователя не найдены"))
            return
        
        # Определяем город для теста
        city = user.city or "Уфа"
        
        # Формируем тестовое сообщение (точно так же, как в планировщике)
        prayer_display = _("Магриб (Тест)")
        test_message = _("🕌 Время намаза {prayer} в г. {city}!").format(
            prayer=prayer_display,
            city=city
        )
        
        # Отправляем тестовое уведомление
        await message.answer(test_message)
        
        # Дополнительная информация для отладки
        debug_info = (
            f"✅ Тестовое уведомление отправлено\n"
            f"👤 Пользователь: {user.full_name} (ID: {user.telegram_id})\n"
            f"📍 Город: {city}\n"
            f"🌍 Язык: {settings.language}\n"
            f"🔔 Уведомления о намазах: {'ВКЛ' if settings.prayer_notifications_on else 'ВЫКЛ'}"
        )
        
        await message.answer(debug_info)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при выполнении команды: {str(e)}")


@router.message(Command("test_scheduler"), AdminFilter())
async def cmd_test_scheduler(
    message: types.Message,
    session: AsyncSession,
) -> None:
    """Тестовая команда для проверки работы планировщика"""
    try:
        from bot.services.scheduler import check_prayer_times
        
        await message.answer(_("🔄 Запуск тестовой проверки планировщика..."))
        
        # Запускаем проверку вручную
        await check_prayer_times()
        
        await message.answer(_("✅ Тестовая проверка планировщика завершена"))
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при тесте планировщика: {str(e)}")
