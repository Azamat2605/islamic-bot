from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from database.models import Settings


def settings_root_keyboard(user, settings) -> InlineKeyboardMarkup:
    """Клавиатура корня настроек."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("⚙️ Общие настройки"),
            callback_data="settings_general",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🔔 Уведомления"),
            callback_data="settings_notifications",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад в Профиль"),
            callback_data="back_to_profile",
        )
    )
    
    return builder.as_markup()


def settings_general_keyboard(user, settings: Settings) -> InlineKeyboardMarkup:
    """Клавиатура общих настроек."""
    builder = InlineKeyboardBuilder()
    
    # Кнопки редактирования профиля
    name_text = _("✏️ Изменить Имя ({name})").format(name=user.full_name or "—")
    builder.row(
        InlineKeyboardButton(
            text=name_text,
            callback_data="edit_name",
        ),
    )
    
    gender_text = _("Изменить Пол ({gender})").format(gender=user.gender or "—")
    builder.row(
        InlineKeyboardButton(
            text=gender_text,
            callback_data="edit_gender",
        ),
    )
    
    city_text = _("Изменить Город ({city})").format(city=user.city or "—")
    builder.row(
        InlineKeyboardButton(
            text=city_text,
            callback_data="edit_city",
        )
    )
    
    # Язык
    language_text = _("🇷🇺 Язык: {lang}").format(lang=settings.language.upper())
    builder.row(
        InlineKeyboardButton(
            text=language_text,
            callback_data="general_language",
        )
    )
    
    # Часовой пояс
    timezone_text = _("⏳ Часовой пояс: {tz}").format(tz=settings.timezone)
    builder.row(
        InlineKeyboardButton(
            text=timezone_text,
            callback_data="general_timezone",
        )
    )
    
    # Формат времени
    time_format_display = _("24h") if settings.time_format else _("12h")
    time_format_text = _("🕒 Формат времени: {fmt}").format(fmt=time_format_display)
    builder.row(
        InlineKeyboardButton(
            text=time_format_text,
            callback_data="general_time_format",
        )
    )
    
    # Назад
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад в Настройки"),
            callback_data="back_to_settings",
        )
    )
    
    return builder.as_markup()


def settings_notifications_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    """Клавиатура настроек уведомлений."""
    builder = InlineKeyboardBuilder()
    
    # Общие уведомления
    general_status = _("Вкл") if settings.notification_on else _("Выкл")
    general_text = _("🔔 Общие: {status}").format(status=general_status)
    builder.row(
        InlineKeyboardButton(
            text=general_text,
            callback_data="toggle_general_notifications",
        )
    )
    
    # Уведомления о намазах
    prayer_status = _("Вкл") if settings.prayer_notifications_on else _("Выкл")
    prayer_text = _("🕌 Намазы: {status}").format(status=prayer_status)
    builder.row(
        InlineKeyboardButton(
            text=prayer_text,
            callback_data="toggle_prayer_notifications",
        )
    )
    
    # Уведомления о событиях
    event_status = _("Вкл") if settings.event_notifications_on else _("Выкл")
    event_text = _("📅 События: {status}").format(status=event_status)
    builder.row(
        InlineKeyboardButton(
            text=event_text,
            callback_data="toggle_event_notifications",
        )
    )
    
    # Назад
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад в Настройки"),
            callback_data="back_to_settings",
        )
    )
    
    return builder.as_markup()




def timezone_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора часового пояса (популярные)."""
    builder = InlineKeyboardBuilder()
    
    popular_timezones = [
        ("Europe/Moscow", "Москва (+3)"),
        ("Europe/London", "Лондон (+0)"),
        ("Europe/Berlin", "Берлин (+1)"),
        ("Asia/Tashkent", "Ташкент (+5)"),
        ("Asia/Almaty", "Алматы (+6)"),
        ("America/New_York", "Нью-Йорк (-5)"),
    ]
    
    for tz_code, tz_name in popular_timezones:
        builder.row(
            InlineKeyboardButton(
                text=tz_name,
                callback_data=f"timezone_select:{tz_code}",
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("✏️ Ввести вручную"),
            callback_data="timezone_manual",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data="back_to_general",
        )
    )
    
    return builder.as_markup()




def time_format_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора формата времени."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("24-часовой"),
            callback_data="time_format_select:24h",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("12-часовой"),
            callback_data="time_format_select:12h",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data="back_to_general",
        )
    )
    
    return builder.as_markup()


def settings_about_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура 'О проекте и Поддержка'."""
    builder = InlineKeyboardBuilder()
    
    # Помощь проекту
    builder.row(
        InlineKeyboardButton(
            text=_("💰 Помощь проекту"),
            url="https://github.com/donBarbos/telegram-bot-template/donations",
        )
    )
    
    # Поддержка
    builder.row(
        InlineKeyboardButton(
            text=_("🆘 Поддержка"),
            url="https://t.me/your_support_chat",
        )
    )
    
    # О проекте
    builder.row(
        InlineKeyboardButton(
            text=_("📖 О проекте"),
            url="https://github.com/donBarbos/telegram-bot-template",
        )
    )
    
    # Назад
    builder.row(
        InlineKeyboardButton(
            text=_("↩️ Назад в Настройки"),
            callback_data="back_to_settings",
        )
    )
    
    return builder.as_markup()
