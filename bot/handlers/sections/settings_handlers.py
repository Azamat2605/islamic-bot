from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User, Settings
from database.crud import get_user_with_settings
from bot.keyboards.inline.settings import (
    settings_root_keyboard,
    settings_general_keyboard,
    settings_notifications_keyboard,
    timezone_keyboard,
    time_format_keyboard,
    settings_about_keyboard,
)
from bot.keyboards.inline.profile import language_keyboard
from bot.states.settings import TimezoneStates
from bot.states.profile import ProfileStates

router = Router(name="settings")


@router.callback_query(F.data == "settings_root")
async def settings_root_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Обработчик корня настроек."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    await callback.message.edit_text(
        _("⚙️ Настройки\n\nВыберите категорию настроек:"),
        reply_markup=settings_root_keyboard(user, settings),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_general")
async def settings_general_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Обработчик общих настроек."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    await callback.message.edit_text(
        _("⚙️ Общие настройки"),
        reply_markup=settings_general_keyboard(user, settings),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notifications")
async def settings_notifications_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Обработчик настроек уведомлений."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    await callback.message.edit_text(
        _("🔔 Управление уведомлениями"),
        reply_markup=settings_notifications_keyboard(settings),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_about")
async def settings_about_handler(
    callback: types.CallbackQuery,
) -> None:
    """Обработчик раздела 'О проекте и Поддержка'."""
    await callback.message.edit_text(
        _("Информация о проекте и помощь"),
        reply_markup=settings_about_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "edit_name")
async def edit_name_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Обработчик запроса на изменение имени."""
    await callback.message.answer(
        _("Введите новое имя (от 2 до 100 символов):")
    )
    await state.set_state(ProfileStates.waiting_for_name)
    await callback.answer()




@router.callback_query(F.data == "back_to_profile")
async def back_to_profile_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Возврат в профиль."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    from bot.keyboards.inline.profile import profile_keyboard
    
    # Формируем текст профиля
    from bot.handlers.sections.profile_handlers import get_profile_text
    profile_text = get_profile_text(user, settings)
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=profile_keyboard(user, settings),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Возврат в корень настроек."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    await callback.message.edit_text(
        _("⚙️ Настройки\n\nВыберите категорию настроек:"),
        reply_markup=settings_root_keyboard(user, settings),
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_general")
async def back_to_general_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Возврат в общие настройки."""
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    await callback.message.edit_text(
        _("⚙️ Общие настройки"),
        reply_markup=settings_general_keyboard(user, settings),
    )
    await callback.answer()


@router.callback_query(F.data == "general_language")
async def general_language_handler(
    callback: types.CallbackQuery,
) -> None:
    """Показ клавиатуры выбора языка."""
    await callback.message.edit_reply_markup(reply_markup=language_keyboard())
    await callback.answer()


@router.callback_query(F.data == "general_timezone")
async def general_timezone_handler(
    callback: types.CallbackQuery,
) -> None:
    """Показ клавиатуры выбора часового пояса."""
    await callback.message.edit_text(
        _("⏳ Выберите часовой пояс:"),
        reply_markup=timezone_keyboard(),
    )
    await callback.answer()




@router.callback_query(F.data == "general_time_format")
async def general_time_format_handler(
    callback: types.CallbackQuery,
) -> None:
    """Показ клавиатуры выбора формата времени."""
    await callback.message.edit_text(
        _("🕒 Выберите формат времени:"),
        reply_markup=time_format_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_setting_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Универсальный обработчик переключения настроек."""
    setting_type = callback.data.replace("toggle_", "")
    
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    # Определяем какое поле менять
    if setting_type == "general_notifications":
        settings.notification_on = not settings.notification_on
        message = _("Общие уведомления {}").format(
            _("включены") if settings.notification_on else _("выключены")
        )
    elif setting_type == "prayer_notifications":
        settings.prayer_notifications_on = not settings.prayer_notifications_on
        message = _("Уведомления о намазах {}").format(
            _("включены") if settings.prayer_notifications_on else _("выключены")
        )
    elif setting_type == "event_notifications":
        settings.event_notifications_on = not settings.event_notifications_on
        message = _("Уведомления о событиях {}").format(
            _("включены") if settings.event_notifications_on else _("выключены")
        )
    else:
        await callback.answer(_("Неизвестная настройка."), show_alert=True)
        return
    
    await session.commit()
    
    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=settings_notifications_keyboard(settings)
    )
    await callback.answer(message)


@router.callback_query(F.data.startswith("timezone_select:"))
async def timezone_select_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Обработчик выбора часового пояса из списка."""
    timezone = callback.data.split(":")[1]
    
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    settings.timezone = timezone
    await session.commit()
    
    await callback.message.edit_text(
        _("⏳ Часовой пояс обновлен на: {tz}").format(tz=timezone),
        reply_markup=settings_general_keyboard(user, settings),
    )
    await callback.answer()


@router.callback_query(F.data == "timezone_manual")
async def timezone_manual_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Запуск FSM для ручного ввода часового пояса."""
    await callback.message.answer(
        _("Введите часовой пояс (например, Europe/Moscow или +3):")
    )
    await state.set_state(TimezoneStates.entering_timezone)
    await callback.answer()




@router.callback_query(F.data.startswith("time_format_select:"))
async def time_format_select_handler(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    """Обработчик выбора формата времени."""
    time_format_str = callback.data.split(":")[1]
    time_format_bool = time_format_str == "24h"
    
    telegram_id = callback.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return
    
    settings.time_format = time_format_bool
    await session.commit()
    
    display_format = _("24-часовой") if time_format_bool else _("12-часовой")
    await callback.message.edit_text(
        _("� Формат времени обновлен на: {fmt}").format(fmt=display_format),
        reply_markup=settings_general_keyboard(user, settings),
    )
    await callback.answer()






@router.message(TimezoneStates.entering_timezone)
async def process_timezone(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обработка введённого часового пояса."""
    timezone_input = message.text.strip()
    
    # Простая валидация: проверяем, что ввод не пустой
    if not timezone_input:
        await message.answer(_("Пожалуйста, введите часовой пояс."))
        return
    
    telegram_id = message.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await message.answer(_("Пользователь не найден."))
        await state.clear()
        return
    
    # Сохраняем часовой пояс (можно добавить более сложную валидацию через pytz)
    settings.timezone = timezone_input
    await session.commit()
    
    await state.clear()
    
    # Показываем обновленные настройки
    await message.answer(
        _("⏳ Часовой пояс обновлен на: {tz}").format(tz=timezone_input),
        reply_markup=settings_general_keyboard(user, settings),
    )


@router.message(ProfileStates.waiting_for_name)
async def process_name(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Обработка введённого имени."""
    new_name = message.text.strip()
    
    # Валидация: длина от 2 до 100 символов
    if len(new_name) < 2 or len(new_name) > 100:
        await message.answer(
            _("Имя должно содержать от 2 до 100 символов. Попробуйте снова:")
        )
        return
    
    telegram_id = message.from_user.id
    user, settings = await get_user_with_settings(session, telegram_id)
    
    if not user or not settings:
        await message.answer(_("Пользователь не найден."))
        await state.clear()
        return
    
    # Обновляем имя пользователя
    user.full_name = new_name
    await session.commit()
    
    await state.clear()
    
    # Показываем обновленные настройки
    await message.answer(
        _("✅ Имя успешно обновлено на: {name}").format(name=new_name),
        reply_markup=settings_general_keyboard(user, settings),
    )
