from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from database.models import Settings
from bot.services.prayer_service import PrayerService
from bot.core.config import BASHKIRIA_CITIES


def get_prayer_main_kb() -> InlineKeyboardMarkup:
    """Главное меню намаза"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("📆 НЕДЕЛЯ"),
            callback_data="prayer_week"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("⚙️ НАСТРОЙКИ"),
            callback_data="prayer_settings"
        )
    )
    
    # Кнопка возврата в главное меню бота
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 В главное меню"),
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_prayer_week_kb(offset_days: int = 0) -> InlineKeyboardMarkup:
    """Меню недели с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки пагинации
    if offset_days > 0:
        builder.row(
            InlineKeyboardButton(
                text=_("⬅️ Назад"),
                callback_data=f"prayer_week:{offset_days - 7}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("➡️ След. неделя"),
            callback_data=f"prayer_week:{offset_days + 7}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 В меню"),
            callback_data="prayer_main"
        )
    )
    
    return builder.as_markup()


def get_notification_settings_kb(settings: Settings, timings: dict = None) -> InlineKeyboardMarkup:
    """Клавиатура настроек уведомлений для намазов"""
    builder = InlineKeyboardBuilder()
    
    # Тогглы уведомлений для каждого намаза
    prayer_configs = [
        ("Fajr", "notify_fajr", _("Фаджр")),
        ("Dhuhr", "notify_dhuhr", _("Зухр")),
        ("Asr", "notify_asr", _("Аср")),
        ("Maghrib", "notify_maghrib", _("Магриб")),
        ("Isha", "notify_isha", _("Иша")),
    ]
    
    for prayer_key, setting_field, display_name in prayer_configs:
        # Получаем статус уведомления
        is_enabled = getattr(settings, setting_field, True)
        status = "✅" if is_enabled else "▢"
        
        # Получаем время намаза, если доступно
        time_display = ""
        if timings and prayer_key in timings:
            time_str = timings.get(prayer_key, "")
            if time_str:
                # Форматируем время
                try:
                    from datetime import datetime
                    dt = datetime.strptime(time_str, "%H:%M")
                    time_display = dt.strftime("%H:%M")
                except ValueError:
                    time_display = time_str
                display_text = f"{display_name}: {time_display} {status}"
            else:
                display_text = f"{display_name}: {status}"
        else:
            display_text = f"{display_name}: {status}"
        
        builder.row(
            InlineKeyboardButton(
                text=display_text,
                callback_data=f"prayer_toggle:{prayer_key.lower()}"
            )
        )
    
    # Кнопка назад в главное меню настроек
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="open_prayer_settings"
        )
    )
    
    return builder.as_markup()


def get_prayer_settings_kb(settings: Settings, city: str, timings: dict = None) -> InlineKeyboardMarkup:
    """Главное меню настроек намазов (очищенное)"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка города
    city_display = city if city else _("Не указан")
    city_button = InlineKeyboardButton(
        text=_("📍 Город: {city}").format(city=city_display),
        callback_data="prayer_change_city"
    )
    
    # Кнопка мазхаба (read-only)
    madhab_display = settings.madhab if settings.madhab else "Hanafi"
    madhab_button = InlineKeyboardButton(
        text=_("🕌 Мазхаб: {madhab}").format(madhab=madhab_display),
        callback_data="noop"  # Read-only
    )
    
    # Пробуем разместить город и мазхаб в одном ряду, если длина позволяет
    # Проверяем примерную длину текста (грубая оценка)
    city_text_len = len(city_button.text)
    madhab_text_len = len(madhab_button.text)
    
    # Если суммарная длина не превышает ~50 символов (безопасный предел)
    if city_text_len + madhab_text_len <= 50:
        builder.row(city_button, madhab_button)
    else:
        # Иначе размещаем в отдельных рядах
        builder.row(city_button)
        builder.row(madhab_button)
    
    # Кнопка настройки уведомлений
    builder.row(
        InlineKeyboardButton(
            text=_("🔔 Настройка уведомлений"),
            callback_data="open_notification_settings"
        )
    )
    
    # Кнопка назад в меню расписания
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="prayer_main"
        )
    )
    
    return builder.as_markup()


def get_madhab_selection_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора мазхаба"""
    builder = InlineKeyboardBuilder()
    
    madhabs = [
        ("Hanafi", _("Ханафитский")),
        ("Shafi", _("Шафиитский")),
        ("Maliki", _("Маликитский")),
        ("Hanbali", _("Ханбалитский")),
    ]
    
    for madhab_key, madhab_name in madhabs:
        builder.row(
            InlineKeyboardButton(
                text=madhab_name,
                callback_data=f"prayer_madhab:{madhab_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="prayer_settings"
        )
    )
    
    return builder.as_markup()


def get_city_selection_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора города из списка Башкирии"""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с городами (по 2 в ряд)
    for i in range(0, len(BASHKIRIA_CITIES), 2):
        row_cities = BASHKIRIA_CITIES[i:i+2]
        buttons = []
        for city in row_cities:
            buttons.append(
                InlineKeyboardButton(
                    text=city,
                    callback_data=f"prayer_select_city:{city}"
                )
            )
        builder.row(*buttons)
    
    # Кнопка "Назад"
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="prayer_settings"
        )
    )
    
    return builder.as_markup()


def get_city_confirmation_kb(city: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения города"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("✅ Подтвердить"),
            callback_data=f"prayer_confirm_city:{city}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("❌ Отмена"),
            callback_data="prayer_settings"
        )
    )
    
    return builder.as_markup()
