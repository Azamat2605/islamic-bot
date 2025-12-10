from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, List, Tuple
from loguru import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.prayer_service import PrayerService
from database.engine import AsyncSessionLocal as async_session_maker
from database.models import User, Settings
from aiogram.utils.i18n import gettext as _

# Глобальный экземпляр бота, будет установлен после инициализации
bot_instance = None


async def check_prayer_times() -> None:
    """Проверяет время намазов и отправляет уведомления пользователям"""
    try:
        # Получаем текущее локальное время в формате HH:MM
        # Предполагаем, что сервер находится в том же часовом поясе, что и пользователи
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        logger.info(f"Проверка времени намазов: {current_time}")
        
        async with async_session_maker() as session:
            # 1. Получаем уникальные города, где есть пользователи с включенными уведомлениями
            cities = await get_cities_with_notifications(session)
            if not cities:
                logger.info("Нет городов с активными уведомлениями")
                return
            
            logger.info(f"Найдено городов для проверки: {len(cities)}")
            
            # 2. Для каждого города получаем время намазов
            notifications_sent = 0
            for city in cities:
                try:
                    city_notifications = await check_city_prayer_times(
                        session, city, current_time
                    )
                    notifications_sent += city_notifications
                except Exception as e:
                    logger.error(f"Ошибка при проверке города {city}: {e}")
            
            if notifications_sent > 0:
                logger.info(f"Отправлено уведомлений: {notifications_sent}")
            else:
                logger.debug("Нет уведомлений для отправки")
                
    except Exception as e:
        logger.error(f"Критическая ошибка в check_prayer_times: {e}")


async def get_cities_with_notifications(session: AsyncSession) -> List[str]:
    """Получает список уникальных городов, где есть пользователи с включенными уведомлениями"""
    try:
        # Находим города, где есть пользователи с включенными уведомлениями о намазах
        # и у которых указан город
        stmt = (
            select(User.city)
            .join(Settings, User.id == Settings.user_id)
            .where(
                and_(
                    User.city.isnot(None),
                    User.city != "",
                    Settings.prayer_notifications_on == True,
                    or_(
                        Settings.notify_fajr == True,
                        Settings.notify_dhuhr == True,
                        Settings.notify_asr == True,
                        Settings.notify_maghrib == True,
                        Settings.notify_isha == True,
                    )
                )
            )
            .distinct()
        )
        
        result = await session.execute(stmt)
        cities = [row[0] for row in result.fetchall() if row[0]]
        return cities
        
    except Exception as e:
        logger.error(f"Ошибка при получении городов: {e}")
        return []


async def check_city_prayer_times(
    session: AsyncSession, 
    city: str, 
    current_time: str
) -> int:
    """Проверяет время намазов для конкретного города и отправляет уведомления"""
    try:
        # Получаем всех пользователей из этого города с их настройками
        stmt = (
            select(User, Settings)
            .join(Settings, User.id == Settings.user_id)
            .where(
                and_(
                    User.city == city,
                    Settings.prayer_notifications_on == True
                )
            )
        )
        
        result = await session.execute(stmt)
        users_data = result.fetchall()
        
        if not users_data:
            return 0
        
        # Получаем время намазов для города (берем мазхаб первого пользователя для простоты)
        # В реальной системе нужно было бы учитывать разные мазхабы, но для MVP используем первый
        first_user_settings = users_data[0][1]
        madhab = first_user_settings.madhab or "Hanafi"
        
        timings_data = await PrayerService.get_today_timings(city, madhab)
        if not timings_data:
            logger.warning(f"Не удалось получить время намазов для города {city}")
            return 0
        
        timings = timings_data.get("timings", {})
        if not timings:
            return 0
        
        # Проверяем совпадение времени для каждого намаза
        notifications_sent = 0
        
        # Маппинг названий намазов на поля в Settings
        prayer_fields = {
            "Fajr": "notify_fajr",
            "Dhuhr": "notify_dhuhr",
            "Asr": "notify_asr",
            "Maghrib": "notify_maghrib",
            "Isha": "notify_isha",
        }
        
        for prayer_name, prayer_time in timings.items():
            if prayer_time == current_time:
                field_name = prayer_fields.get(prayer_name)
                if not field_name:
                    continue
                
                # Отправляем уведомления всем пользователям с включенным уведомлением для этого намаза
                for user, settings in users_data:
                    if getattr(settings, field_name, False):
                        try:
                            await send_prayer_notification(user, prayer_name, city)
                            notifications_sent += 1
                        except Exception as e:
                            logger.error(f"Ошибка отправки уведомления пользователю {user.telegram_id}: {e}")
        
        return notifications_sent
        
    except Exception as e:
        logger.error(f"Ошибка при проверке города {city}: {e}")
        return 0


async def send_prayer_notification(user: User, prayer_name: str, city: str) -> None:
    """Отправляет уведомление о времени намаза пользователю"""
    global bot_instance
    
    if bot_instance is None:
        logger.error("Экземпляр бота не установлен в планировщике")
        return
    
    try:
        # Получаем локализованное название намаза
        prayer_display_names = {
            "Fajr": _("Фаджр"),
            "Dhuhr": _("Зухр"),
            "Asr": _("Аср"),
            "Maghrib": _("Магриб"),
            "Isha": _("Иша"),
        }
        
        prayer_display = prayer_display_names.get(prayer_name, prayer_name)
        
        # Создаем сообщение
        message = _("🕌 Время намаза {prayer} в г. {city}!").format(
            prayer=prayer_display,
            city=city
        )
        
        # Отправляем сообщение
        await bot_instance.send_message(
            chat_id=user.telegram_id,
            text=message
        )
        
        logger.debug(f"Уведомление отправлено пользователю {user.telegram_id}: {prayer_name} в {city}")
        
    except Exception as e:
        # Игнорируем ошибки блокировки бота пользователем и другие
        if "bot was blocked" in str(e).lower() or "user is deactivated" in str(e).lower():
            logger.debug(f"Пользователь {user.telegram_id} заблокировал бота")
        else:
            logger.error(f"Ошибка отправки уведомления пользователю {user.telegram_id}: {e}")


async def check_event_notifications() -> None:
    """Проверяет мероприятия и отправляет уведомления пользователям"""
    try:
        global bot_instance
        if bot_instance is None:
            logger.error("Экземпляр бота не установлен в планировщике")
            return
        
        async with async_session_maker() as session:
            from bot.services.event_service import EventService
            from database.models import Settings
            
            # Получаем мероприятия для уведомлений (за 24 часа до начала)
            events_with_registrations = await EventService.get_events_for_notification(
                session, hours_before=24
            )
            
            notifications_sent = 0
            for event, registrations in events_with_registrations:
                # Отправляем уведомления всем зарегистрированным пользователям
                for registration in registrations:
                    try:
                        # Проверяем настройки уведомлений пользователя
                        stmt = select(Settings).where(Settings.user_id == registration.user_id)
                        result = await session.execute(stmt)
                        settings = result.scalar_one_or_none()
                        
                        if settings and settings.notify_event_reminder:
                            # Форматируем сообщение
                            start_time = event.start_time.strftime("%d.%m.%Y %H:%M")
                            message = _(
                                "🎪 *Напоминание о мероприятии*\n\n"
                                "Название: *{title}*\n"
                                "Дата и время: {start_time}\n"
                                "Место: {location}\n\n"
                                "Мероприятие начнётся через 24 часа!"
                            ).format(
                                title=event.title,
                                start_time=start_time,
                                location=event.location or _("Не указано")
                            )
                            
                            await bot_instance.send_message(
                                chat_id=registration.user_id,
                                text=message,
                                parse_mode="Markdown"
                            )
                            notifications_sent += 1
                            
                    except Exception as e:
                        logger.error(f"Ошибка отправки уведомления о мероприятии: {e}")
            
            if notifications_sent > 0:
                logger.info(f"Отправлено уведомлений о мероприятиях: {notifications_sent}")
                
    except Exception as e:
        logger.error(f"Ошибка в check_event_notifications: {e}")


# Создаем глобальный экземпляр планировщика
scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """Настраивает и запускает планировщик"""
    try:
        # Добавляем задачу проверки времени намазов каждую минуту
        scheduler.add_job(
            check_prayer_times,
            'cron',
            second=0,  # Запускаем в начале каждой минуты
            id='prayer_notifications',
            replace_existing=True
        )
        
        # Добавляем задачу проверки мероприятий каждый час
        scheduler.add_job(
            check_event_notifications,
            'cron',
            hour='*',  # Каждый час
            id='event_notifications',
            replace_existing=True
        )
        
        logger.info("Планировщик уведомлений настроен")
        
    except Exception as e:
        logger.error(f"Ошибка настройки планировщика: {e}")


def start_scheduler() -> None:
    """Запускает планировщик"""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("Планировщик уведомлений запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {e}")


def stop_scheduler() -> None:
    """Останавливает планировщик"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Планировщик уведомлений остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки планировщика: {e}")


def set_bot_instance(bot):
    """Устанавливает экземпляр бота для использования в планировщике"""
    global bot_instance
    bot_instance = bot
    logger.info("Экземпляр бота установлен в планировщике")
