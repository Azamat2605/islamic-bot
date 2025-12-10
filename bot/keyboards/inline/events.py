"""
Инлайн-клавиатуры для работы с мероприятиями и календарём.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import EventType, EventStatus


def get_events_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню календаря событий."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎪 Мероприятия общины", callback_data="events_community"),
        InlineKeyboardButton(text="📅 Религиозные события", callback_data="events_religious")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад в главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_community_events_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура меню мероприятий общины."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Список мероприятий", callback_data="events_list"),
        InlineKeyboardButton(text="📝 Мои записи", callback_data="events_my_registrations")
    )
    
    builder.row(
        InlineKeyboardButton(text="➕ Предложить мероприятие", callback_data="events_propose"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_main")
    )
    
    return builder.as_markup()


def get_religious_events_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура меню религиозных событий."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Календарь Хиджры", callback_data="religious_calendar"),
        InlineKeyboardButton(text="⏩ Ближайшие события", callback_data="religious_upcoming")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔔 Напоминания", callback_data="religious_reminders"),
        InlineKeyboardButton(text="📜 Праздники на год", callback_data="religious_year_list")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_main")
    )
    
    return builder.as_markup()


def get_events_list_keyboard(events, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """Клавиатура со списком мероприятий с пагинацией."""
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_events = events[start_idx:end_idx]
    
    for event in paginated_events:
        event_text = f"{event.title[:20]}..." if len(event.title) > 20 else event.title
        builder.row(
            InlineKeyboardButton(
                text=f"📅 {event_text} ({event.start_time.strftime('%d.%m %H:%M')})",
                callback_data=f"event_detail_{event.id}"
            )
        )
    
    # Пагинация
    if page > 0:
        builder.row(
            InlineKeyboardButton(text="⬅️ Предыдущие", callback_data=f"events_page_{page-1}")
        )
    
    if end_idx < len(events):
        builder.row(
            InlineKeyboardButton(text="Следующие ➡️", callback_data=f"events_page_{page+1}")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_community")
    )
    
    return builder.as_markup()


def get_event_detail_keyboard(event_id: int, is_registered: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура детальной информации о мероприятии."""
    builder = InlineKeyboardBuilder()
    
    if not is_registered:
        builder.row(
            InlineKeyboardButton(text="✅ Записаться", callback_data=f"event_register_{event_id}")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"event_cancel_{event_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="📋 К списку мероприятий", callback_data="events_list"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_community")
    )
    
    return builder.as_markup()


def get_my_registrations_keyboard(registrations) -> InlineKeyboardMarkup:
    """Клавиатура для списка моих записей."""
    builder = InlineKeyboardBuilder()
    
    if not registrations:
        builder.row(
            InlineKeyboardButton(text="📋 К списку мероприятий", callback_data="events_list")
        )
    else:
        for reg in registrations:
            event_text = f"{reg.event.title[:20]}..." if len(reg.event.title) > 20 else reg.event.title
            builder.row(
                InlineKeyboardButton(
                    text=f"❌ {event_text} ({reg.event.start_time.strftime('%d.%m %H:%M')})",
                    callback_data=f"cancel_registration_{reg.id}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_community")
    )
    
    return builder.as_markup()


def get_calendar_month_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по месяцам календаря."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Предыдущий месяц", callback_data=f"calendar_prev_{year}_{month}"),
        InlineKeyboardButton(text="Следующий месяц ➡️", callback_data=f"calendar_next_{year}_{month}")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_religious")
    )
    
    return builder.as_markup()


def get_reminders_settings_keyboard(
    notify_1day: bool,
    notify_on_day: bool,
    notify_juma: bool
) -> InlineKeyboardMarkup:
    """Клавиатура для настройки напоминаний."""
    builder = InlineKeyboardBuilder()
    
    # Кнопки-переключатели
    notify_1day_text = "✅ За 1 день" if notify_1day else "❌ За 1 день"
    notify_on_day_text = "✅ В день события" if notify_on_day else "❌ В день события"
    notify_juma_text = "✅ Пятничные" if notify_juma else "❌ Пятничные"
    
    builder.row(
        InlineKeyboardButton(text=notify_1day_text, callback_data="toggle_reminder_1day")
    )
    
    builder.row(
        InlineKeyboardButton(text=notify_on_day_text, callback_data="toggle_reminder_on_day")
    )
    
    builder.row(
        InlineKeyboardButton(text=notify_juma_text, callback_data="toggle_reminder_juma")
    )
    
    builder.row(
        InlineKeyboardButton(text="💾 Сохранить", callback_data="save_reminders"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="events_religious")
    )
    
    return builder.as_markup()


def get_event_proposal_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения предложения мероприятия."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Отправить", callback_data="proposal_submit"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="proposal_cancel")
    )
    
    return builder.as_markup()


def get_admin_proposal_action_keyboard(proposal_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для действий администратора с предложением."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_proposal_approve_{proposal_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_proposal_reject_{proposal_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="📝 Добавить комментарий", callback_data=f"admin_proposal_comment_{proposal_id}")
    )
    
    return builder.as_markup()


def get_back_to_events_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура для возврата к мероприятиям."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад к мероприятиям", callback_data="events_community")
    )
    
    return builder.as_markup()
