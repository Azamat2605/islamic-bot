"""
Обработчики для раздела "Календарь событий" (упрощённая версия).
"""
import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.events import (
    get_events_main_keyboard,
    get_community_events_keyboard,
    get_religious_events_keyboard,
    get_events_list_keyboard,
    get_event_detail_keyboard,
    get_my_registrations_keyboard,
    get_back_to_events_keyboard
)
from bot.states.events import EventProposalState
from bot.services.event_service import EventService
from database.models import EventProposal, ProposalStatus

router = Router(name="events_calendar")


# ===== Основные обработчики меню =====

@router.message(F.text == __("Календарь событий"))
async def events_calendar_text_handler(message: types.Message) -> None:
    """Обработчик текстового сообщения "Календарь событий" из reply-клавиатуры."""
    text = _(
        "📅 *Календарь событий*\n\n"
        "Выберите раздел:"
    )
    
    await message.answer(
        text,
        reply_markup=get_events_main_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "events_calendar")
async def events_calendar_main_handler(callback: types.CallbackQuery) -> None:
    """Главное меню календаря событий."""
    text = _(
        "📅 *Календарь событий*\n\n"
        "Выберите раздел:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_events_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "events_main")
async def events_main_handler(callback: types.CallbackQuery) -> None:
    """Возврат в главное меню календаря событий."""
    await events_calendar_main_handler(callback)


@router.callback_query(F.data == "events_community")
async def events_community_handler(callback: types.CallbackQuery) -> None:
    """Меню мероприятий общины."""
    text = _(
        "🎪 *Мероприятия общины*\n\n"
        "Здесь вы можете просмотреть предстоящие мероприятия, "
        "записаться на них или предложить своё мероприятие."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_community_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "events_religious")
async def events_religious_handler(callback: types.CallbackQuery) -> None:
    """Меню религиозных событий."""
    text = _(
        "📅 *Религиозные события*\n\n"
        "Календарь Хиджры, важные исламские даты и настройки напоминаний."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_religious_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ===== Мероприятия общины =====

@router.callback_query(F.data == "events_list")
async def events_list_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Список предстоящих мероприятий."""
    events = await EventService.get_upcoming_events(session, limit=20)
    
    if not events:
        text = _("На данный момент нет предстоящих мероприятий.")
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_events_keyboard()
        )
    else:
        text = _("📋 *Предстоящие мероприятия:*")
        await callback.message.edit_text(
            text,
            reply_markup=get_events_list_keyboard(events),
            parse_mode="Markdown"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("event_detail_"))
async def event_detail_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Детальная информация о мероприятии."""
    event_id = int(callback.data.split("_")[-1])
    event = await EventService.get_event_by_id(session, event_id)
    
    if not event:
        await callback.answer(_("Мероприятие не найдено."), show_alert=True)
        return
    
    # Проверяем, зарегистрирован ли пользователь
    user_id = callback.from_user.id
    registrations = await EventService.get_user_registrations(session, user_id)
    is_registered = any(reg.event_id == event_id for reg in registrations)
    
    # Форматируем дату и время
    start_time = event.start_time.strftime("%d.%m.%Y %H:%M")
    
    # Форматируем тип мероприятия
    event_type_map = {
        "lecture": "Лекция",
        "meeting": "Встреча",
        "course": "Курс",
        "other": "Другое"
    }
    event_type = event_type_map.get(event.event_type.value, event.event_type.value)
    
    text = _(
        "📅 *{title}*\n\n"
        "📝 *Описание:* {description}\n"
        "📅 *Дата и время:* {start_time}\n"
        "📍 *Место:* {location}\n"
        "🎯 *Тип:* {event_type}\n"
        "👥 *Участников:* {current}/{max}\n"
        "📌 *Статус:* {status}\n"
    ).format(
        title=event.title,
        description=event.description or _("Не указано"),
        start_time=start_time,
        location=event.location or _("Не указано"),
        event_type=event_type,
        current=await EventService.get_event_registrations_count(session, event.id),
        max=event.max_participants or _("Не ограничено"),
        status=_("Активно") if event.status.value == "active" else _("Отменено")
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_event_detail_keyboard(event.id, is_registered),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("event_register_"))
async def event_register_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Регистрация на мероприятие."""
    event_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    success, message = await EventService.register_for_event(session, user_id, event_id)
    
    if success:
        await callback.answer(_("✅ Вы успешно зарегистрировались!"), show_alert=True)
        # Обновляем сообщение
        await event_detail_handler(callback, session)
    else:
        await callback.answer(message, show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("event_cancel_"))
async def event_cancel_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Отмена регистрации на мероприятие."""
    event_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    # Находим регистрацию
    registrations = await EventService.get_user_registrations(session, user_id)
    registration = next((reg for reg in registrations if reg.event_id == event_id), None)
    
    if not registration:
        await callback.answer(_("Регистрация не найдена."), show_alert=True)
        return
    
    success, message = await EventService.cancel_registration(
        session, registration.id, user_id
    )
    
    if success:
        await callback.answer(_("✅ Регистрация отменена."), show_alert=True)
        # Обновляем сообщение
        await event_detail_handler(callback, session)
    else:
        await callback.answer(message, show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data == "events_my_registrations")
async def events_my_registrations_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Мои записи на мероприятия."""
    user_id = callback.from_user.id
    registrations = await EventService.get_user_registrations(session, user_id)
    
    if not registrations:
        text = _("У вас пока нет активных записей на мероприятия.")
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_events_keyboard()
        )
    else:
        text = _("📝 *Мои записи на мероприятия:*")
        await callback.message.edit_text(
            text,
            reply_markup=get_my_registrations_keyboard(registrations),
            parse_mode="Markdown"
        )
    
    await callback.answer()


# ===== Предложение мероприятий =====

@router.callback_query(F.data == "events_propose")
async def events_propose_start_handler(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Начало процесса предложения мероприятия."""
    await state.set_state(EventProposalState.waiting_for_title)
    
    text = _(
        "➕ *Предложение мероприятия*\n\n"
        "Пожалуйста, введите *название* мероприятия:"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(EventProposalState.waiting_for_title)
async def events_propose_title_handler(
    message: types.Message,
    state: FSMContext
) -> None:
    """Обработка названия мероприятия."""
    if len(message.text) > 200:
        await message.answer(
            _("Название слишком длинное. Максимум 200 символов. Попробуйте снова:")
        )
        return
    
    await state.update_data(title=message.text)
    await state.set_state(EventProposalState.waiting_for_date)
    
    await message.answer(
        _("Отлично! Теперь введите *дату и время* мероприятия в формате ДД.ММ.ГГГГ ЧЧ:MM\n\n"
          "Например: 25.12.2024 19:00")
    )


@router.message(EventProposalState.waiting_for_date)
async def events_propose_date_handler(
    message: types.Message,
    state: FSMContext
) -> None:
    """Обработка даты мероприятия."""
    try:
        date_str = message.text.strip()
        suggested_date = datetime.datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        
        # Проверяем, что дата в будущем
        if suggested_date < datetime.datetime.now():
            await message.answer(
                _("Дата должна быть в будущем. Попробуйте снова:")
            )
            return
        
        await state.update_data(suggested_date=suggested_date)
        await state.set_state(EventProposalState.waiting_for_description)
        
        await message.answer(
            _("Отлично! Теперь введите *описание* мероприятия (можно пропустить):")
        )
        
    except ValueError:
        await message.answer(
            _("Неверный формат даты. Используйте формат ДД.ММ.ГГГГ ЧЧ:MM\n"
              "Например: 25.12.2024 19:00\n\nПопробуйте снова:")
        )


@router.message(EventProposalState.waiting_for_description)
async def events_propose_description_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Обработка описания мероприятия и сохранение предложения."""
    description = message.text if message.text else None
    
    # Получаем данные из состояния
    data = await state.get_data()
    title = data.get("title")
    suggested_date = data.get("suggested_date")
    
    # Сохраняем предложение
    proposal = EventProposal(
        user_id=message.from_user.id,
        title=title,
        description=description,
        suggested_date=suggested_date,
        status=ProposalStatus.PENDING
    )
    
    session.add(proposal)
    await session.commit()
    
    # Очищаем состояние
    await state.clear()
    
    text = _(
        "✅ *Предложение мероприятия отправлено!*\n\n"
        "Название: *{title}*\n"
        "Дата: *{date}*\n"
        "Описание: {description}\n\n"
        "Администраторы рассмотрят ваше предложение и уведомят о решении."
    ).format(
        title=title,
        date=suggested_date.strftime("%d.%m.%Y %H:%M"),
        description=description or _("Не указано")
    )
    
    await message.answer(text, parse_mode="Markdown")


# ===== Религиозные события (заглушки) =====

@router.callback_query(F.data == "religious_calendar")
async def religious_calendar_handler(callback: types.CallbackQuery) -> None:
    """Календарь Хиджры (заглушка)."""
    text = _(
        "📅 *Календарь Хиджры*\n\n"
        "Эта функция находится в разработке.\n"
        "Скоро здесь появится календарь исламских месяцев и важных дат."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "religious_upcoming")
async def religious_upcoming_handler(callback: types.CallbackQuery) -> None:
    """Ближайшие религиозные события (заглушка)."""
    text = _(
        "⏩ *Ближайшие религиозные события*\n\n"
        "Эта функция находится в разработке.\n"
        "Скоро здесь появится информация о ближайших исламских праздниках."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "religious_reminders")
async def religious_reminders_handler(callback: types.CallbackQuery) -> None:
    """Настройки напоминаний (заглушка)."""
    text = _(
        "🔔 *Настройки напоминаний*\n\n"
        "Эта функция находится в разработке.\n"
        "Скоро здесь можно будет настроить уведомления о религиозных событиях."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "religious_year_list")
async def religious_year_list_handler(callback: types.CallbackQuery) -> None:
    """Праздники на год (заглушка)."""
    text = _(
        "📜 *Праздники на год*\n\n"
        "Эта функция находится в разработке.\n"
        "Скоро здесь появится список исламских праздников на текущий год."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_events_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
