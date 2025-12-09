from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from database.models import User, Settings


def profile_keyboard(user: User, settings: Settings) -> InlineKeyboardMarkup:
    """Клавиатура для меню профиля с улучшенной группировкой кнопок (2x2)."""
    builder = InlineKeyboardBuilder()

    # Ряд 1: Настройки и назад (2 кнопки в ряд)
    builder.row(
        InlineKeyboardButton(
            text=_("⚙️ Настройки"),
            callback_data="settings_root",
        ),
        InlineKeyboardButton(
            text=_("🔙 Назад в меню"),
            callback_data="main_menu",
        ),
        width=2
    )
    
    # Ряд 2: О проекте и Поддержка
    builder.row(
        InlineKeyboardButton(
            text=_("ℹ️ О проекте и Поддержка"),
            callback_data="settings_about",
        )
    )

    return builder.as_markup()


def gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора пола (если нужно предопределённые варианты)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("Мужской"), callback_data="gender_male"),
        InlineKeyboardButton(text=_("Женский"), callback_data="gender_female"),
    )
    builder.row(
        InlineKeyboardButton(text=_("Другой"), callback_data="gender_other"),
    )
    builder.row(
        InlineKeyboardButton(text=_("Отмена"), callback_data="cancel"),
    )
    return builder.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора языка."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    )
    builder.row(
        InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
    )
    builder.row(
        InlineKeyboardButton(text=_("Отмена"), callback_data="cancel"),
    )
    return builder.as_markup()
