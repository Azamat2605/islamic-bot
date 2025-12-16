from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from aiogram import F, Router
from bot.handlers.common.show_main_menu import show_main_menu
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.prayers import (
    get_prayer_main_kb,
    get_prayer_week_kb,
    get_prayer_settings_kb,
    get_notification_settings_kb,
    get_madhab_selection_kb,
    get_city_selection_kb,
)
from bot.services.prayer_service import PrayerService
from database.crud import get_user_by_telegram_id, get_user_settings, update_settings
from database.models import User, Settings

router = Router(name="prayer_schedule")


@router.message(F.text == __("Расписание намазов"))
async def handle_prayer_text(message: Message, session: AsyncSession) -> None:
    """Обработка текстового сообщения 'Расписание намазов' (reply-клавиатура)"""
    try:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer(_("Пользователь не найден"))
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await message.answer(_("Настройки не найдены"))
            return

        # Получаем город из профиля пользователя
        city = user.city or "Moscow"
        madhab = settings.madhab or "Hanafi"

        # Получаем время намазов на сегодня
        timings_data = await PrayerService.get_today_timings(city, madhab)
        
        if not timings_data:
            await message.answer(
                _("❌ Не удалось получить расписание намазов.\nПроверьте настройки города."),
                reply_markup=get_prayer_main_kb()
            )
            return

        # Формируем сообщение с улучшенным форматированием
        today_date = date.today().strftime("%d.%m.%Y")
        message_text = _(
            "📍 {city} | 🗓️ {date}\n"
            "🕌 Мазхаб: {madhab}\n"
            "──────────────────\n"
        ).format(city=city, date=today_date, madhab=madhab)

        # Добавляем время намазов без эмодзи
        prayer_times = [
            ("Fajr", _("Фаджр")),
            ("Dhuhr", _("Зухр")),
            ("Asr", _("Аср")),
            ("Maghrib", _("Магриб")),
            ("Isha", _("Иша")),
        ]

        # Собираем строки для выравнивания
        prayer_lines = []
        for prayer_key, prayer_name in prayer_times:
            time_str = timings_data["timings"].get(prayer_key, "N/A")
            if time_str != "N/A":
                try:
                    dt = datetime.strptime(time_str, "%H:%M")
                    time_display = dt.strftime("%H:%M")
                except ValueError:
                    time_display = time_str
                # Выравнивание с использованием фиксированной ширины названий
                if prayer_name == "Фаджр":
                    line = f"{prayer_name}:   {time_display}"
                elif prayer_name == "Зухр":
                    line = f"{prayer_name}:   {time_display}"
                elif prayer_name == "Аср":
                    line = f"{prayer_name}:    {time_display}"
                elif prayer_name == "Магриб":
                    line = f"{prayer_name}: {time_display}"
                elif prayer_name == "Иша":
                    line = f"{prayer_name}:    {time_display}"
                else:
                    line = f"{prayer_name}: {time_display}"
                prayer_lines.append(line)
        
        message_text += "\n".join(prayer_lines)

        await message.answer(
            message_text,
            reply_markup=get_prayer_main_kb()
        )

    except Exception as e:
        logger.error(f"Error in handle_prayer_text: {e}")
        await message.answer(_("Произошла ошибка"))


@router.callback_query(F.data == "prayer_main")
@router.callback_query(F.data == "prayer_schedule")
async def handle_prayer_main(callback: CallbackQuery, session: AsyncSession) -> None:
    """Обработка кнопки 'Расписание намазов' (главное меню)"""
    try:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        # Получаем город из профиля пользователя
        city = user.city or "Moscow"
        madhab = settings.madhab or "Hanafi"

        # Получаем время намазов на сегодня
        timings_data = await PrayerService.get_today_timings(city, madhab)
        
        if not timings_data:
            # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение
            # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст
            try:
                await callback.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete previous message: {e}")
            
            # Отправляем новое сообщение
            await callback.message.answer(
                _("❌ Не удалось получить расписание намазов.\nПроверьте настройки города."),
                reply_markup=get_prayer_main_kb()
            )
            return

        # Формируем сообщение с улучшенным форматированием
        today_date = date.today().strftime("%d.%m.%Y")
        message_text = _(
            "📍 {city} | 🗓️ {date}\n"
            "🕌 Мазхаб: {madhab}\n"
            "──────────────────\n"
        ).format(city=city, date=today_date, madhab=madhab)

        # Добавляем время намазов без эмодзи
        prayer_times = [
            ("Fajr", _("Фаджр")),
            ("Dhuhr", _("Зухр")),
            ("Asr", _("Аср")),
            ("Maghrib", _("Магриб")),
            ("Isha", _("Иша")),
        ]

        # Собираем строки для выравнивания
        prayer_lines = []
        for prayer_key, prayer_name in prayer_times:
            time_str = timings_data["timings"].get(prayer_key, "N/A")
            if time_str != "N/A":
                try:
                    dt = datetime.strptime(time_str, "%H:%M")
                    time_display = dt.strftime("%H:%M")
                except ValueError:
                    time_display = time_str
                # Выравнивание с использованием фиксированной ширины названий
                if prayer_name == "Фаджр":
                    line = f"{prayer_name}:   {time_display}"
                elif prayer_name == "Зухр":
                    line = f"{prayer_name}:   {time_display}"
                elif prayer_name == "Аср":
                    line = f"{prayer_name}:    {time_display}"
                elif prayer_name == "Магриб":
                    line = f"{prayer_name}: {time_display}"
                elif prayer_name == "Иша":
                    line = f"{prayer_name}:    {time_display}"
                else:
                    line = f"{prayer_name}: {time_display}"
                prayer_lines.append(line)
        
        message_text += "\n".join(prayer_lines)

        # Отправляем/редактируем сообщение
        if callback.message.photo:
            # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение
            # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст
            try:
                await callback.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete previous message: {e}")
            
            # Отправляем новое сообщение
            await callback.message.answer(
                message_text,
                reply_markup=get_prayer_main_kb()
            )
        else:
            await callback.message.answer(
                message_text,
                reply_markup=get_prayer_main_kb()
            )
        
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_prayer_main: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data.startswith("prayer_week"))
async def handle_prayer_week(callback: CallbackQuery, session: AsyncSession) -> None:
    """Обработка кнопки '📆 НЕДЕЛЯ'"""
    try:
        # Парсим смещение дней из callback_data
        callback_data = callback.data
        offset_days = 0
        
        if ":" in callback_data:
            try:
                offset_days = int(callback_data.split(":")[1])
            except ValueError:
                offset_days = 0

        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        city = user.city or "Moscow"
        madhab = settings.madhab or "Hanafi"
        start_date = date.today() + timedelta(days=offset_days)

        # Получаем расписание на неделю
        week_data = await PrayerService.get_week_timings(city, madhab, start_date)
        
        if not week_data:
            await callback.message.edit_text(
                _("❌ Не удалось получить расписание на неделю."),
                reply_markup=get_prayer_week_kb(offset_days)
            )
            return

        # Формируем сообщение
        message_text = _("📅 Расписание намазов на неделю\n")
        message_text += _("📍 Город: {city}\n").format(city=city)
        message_text += _("🕌 Мазхаб: {madhab}\n\n").format(madhab=madhab)

        for day_data in week_data:
            day_date = day_data["date"].strftime("%d.%m.%Y")
            message_text += f"<b>{day_date}</b>:\n"
            
            for prayer_key in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                time_str = day_data["timings"].get(prayer_key, "N/A")
                if time_str != "N/A":
                    try:
                        dt = datetime.strptime(time_str, "%H:%M")
                        time_display = dt.strftime("%H:%M")
                    except ValueError:
                        time_display = time_str
                    
                    prayer_name = PrayerService.get_prayer_display_name(prayer_key)
                    message_text += f"  {prayer_name}: {time_display}\n"
            
            message_text += "\n"

        await callback.message.edit_text(
            message_text,
            reply_markup=get_prayer_week_kb(offset_days),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_prayer_week: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data == "prayer_settings")
async def handle_prayer_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    """Обработка кнопки '⚙️ НАСТРОЙКИ'"""
    try:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        # Hotfix: проверка и исправление некорректного города
        if user.city is None or "python" in user.city.lower():
            from database.crud import update_user
            await update_user(session, user.id, {"city": "Уфа"})
            # Обновляем объект пользователя
            user = await get_user_by_telegram_id(session, callback.from_user.id)

        city = user.city or _("Не указан")
        
        # Получаем текущее время намазов для отображения
        timings_data = None
        if user.city:
            timings_data = await PrayerService.get_today_timings(
                user.city, 
                settings.madhab or "Hanafi"
            )

        timings = timings_data["timings"] if timings_data else None

        await callback.message.edit_text(
            _("⚙️ Настройки намазов"),
            reply_markup=get_prayer_settings_kb(settings, city, timings)
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_prayer_settings: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data == "open_notification_settings")
async def handle_open_notification_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    """Открытие подменю настроек уведомлений"""
    try:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return
        
        # Получаем время намазов для отображения
        timings_data = None
        if user.city:
            timings_data = await PrayerService.get_today_timings(
                user.city, 
                settings.madhab or "Hanafi"
            )
        
        timings = timings_data["timings"] if timings_data else None

        await callback.message.edit_text(
            _("🔔 Настройка уведомлений"),
            reply_markup=get_notification_settings_kb(settings, timings)
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_open_notification_settings: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data == "open_prayer_settings")
async def handle_open_prayer_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    """Возврат из подменю уведомлений в главное меню настроек"""
    try:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        city = user.city or _("Не указан")
        
        # Получаем текущее время намазов для отображения
        timings_data = None
        if user.city:
            timings_data = await PrayerService.get_today_timings(
                user.city, 
                settings.madhab or "Hanafi"
            )

        timings = timings_data["timings"] if timings_data else None

        await callback.message.edit_text(
            _("⚙️ Настройки намазов"),
            reply_markup=get_prayer_settings_kb(settings, city, timings)
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_open_prayer_settings: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data.startswith("prayer_toggle:"))
async def handle_prayer_toggle(callback: CallbackQuery, session: AsyncSession) -> None:
    """Переключение уведомлений для конкретного намаза (в подменю уведомлений)"""
    try:
        prayer_key = callback.data.split(":")[1].upper()  # fajr -> FAJR
        
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        # Определяем поле для обновления
        field_map = {
            "FAJR": "notify_fajr",
            "DHUHR": "notify_dhuhr",
            "ASR": "notify_asr",
            "MAGHRIB": "notify_maghrib",
            "ISHA": "notify_isha",
        }
        
        field_name = field_map.get(prayer_key)
        if not field_name:
            await callback.answer(_("Неизвестный намаз"), show_alert=True)
            return

        # Инвертируем значение
        current_value = getattr(settings, field_name, True)
        new_value = not current_value
        
        # Обновляем в БД
        update_data = {field_name: new_value}
        await update_settings(session, settings.id, update_data)
        
        # Получаем обновленные настройки
        settings = await get_user_settings(session, user.id)
        
        # Получаем время намазов для отображения
        timings_data = None
        if user.city:
            timings_data = await PrayerService.get_today_timings(
                user.city, 
                settings.madhab or "Hanafi"
            )
        
        timings = timings_data["timings"] if timings_data else None
        
        # Обновляем клавиатуру подменю уведомлений
        await callback.message.edit_reply_markup(
            reply_markup=get_notification_settings_kb(settings, timings)
        )
        
        status_text = _("включены") if new_value else _("выключены")
        prayer_name = PrayerService.get_prayer_display_name(prayer_key.capitalize())
        await callback.answer(_("Уведомления для {prayer} {status}").format(
            prayer=prayer_name, status=status_text
        ))

    except Exception as e:
        logger.error(f"Error in handle_prayer_toggle: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)


@router.callback_query(F.data == "prayer_change_city")
async def handle_change_city(callback: CallbackQuery) -> None:
    """Показ клавиатуры выбора города из списка Башкирии"""
    await callback.message.edit_text(
        _("📍 Выберите город из списка:"),
        reply_markup=get_city_selection_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prayer_select_city:"))
async def handle_city_selection(callback: CallbackQuery, session: AsyncSession) -> None:
    """Обработка выбора города из списка"""
    try:
        city = callback.data.split(":")[1]
        
        # Сохраняем город в профиль пользователя
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return
        
        from database.crud import update_user
        await update_user(session, user.id, {"city": city})
        
        # Получаем обновленные настройки для отображения
        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return
        
        # Получаем время намазов для отображения
        timings_data = None
        if city:
            timings_data = await PrayerService.get_today_timings(
                city, 
                settings.madhab or "Hanafi"
            )
        
        timings = timings_data["timings"] if timings_data else None
        
        await callback.message.edit_text(
            _("✅ Город '{city}' успешно сохранен!").format(city=city),
            reply_markup=get_prayer_settings_kb(settings, city, timings)
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_city_selection: {e}")
        await callback.answer(_("❌ Произошла ошибка при сохранении города."), show_alert=True)


@router.callback_query(F.data == "noop")
async def handle_noop(callback: CallbackQuery) -> None:
    """Обработка noop callback (кнопки без действия)"""
    await callback.answer()


# Дополнительные обработчики для выбора мазхаба (если понадобится расширить функционал)
@router.callback_query(F.data.startswith("prayer_madhab:"))
async def handle_madhab_selection(callback: CallbackQuery, session: AsyncSession) -> None:
    """Обработка выбора мазхаба"""
    try:
        madhab = callback.data.split(":")[1]
        
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(_("Пользователь не найден"), show_alert=True)
            return

        settings = await get_user_settings(session, user.id)
        if not settings:
            await callback.answer(_("Настройки не найдены"), show_alert=True)
            return

        # Обновляем мазхаб
        await update_settings(session, settings.id, {"madhab": madhab})
        
        await callback.message.edit_text(
            _("✅ Мазхаб изменен на {madhab}").format(madhab=madhab),
            reply_markup=get_prayer_main_kb()
        )
        
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in handle_madhab_selection: {e}")
        await callback.answer(_("Произошла ошибка"), show_alert=True)
