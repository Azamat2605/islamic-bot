from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с 7 кнопками."""
    buttons = [
        [InlineKeyboardButton(text=_("🤖 Исламский помощник"), callback_data="islamic_assistant")],
        [
            InlineKeyboardButton(text=_("👤 Профиль"), callback_data="profile_settings"),
            InlineKeyboardButton(text=_("📖 Знания"), callback_data="knowledge"),
        ],
        [
            InlineKeyboardButton(text=_("📚 Обучение"), callback_data="education"),
            InlineKeyboardButton(text=_("🕌 Намаз"), callback_data="prayer_schedule"),
        ],
        [
            InlineKeyboardButton(text=_("🥩 Халяль"), callback_data="halal_places"),
            InlineKeyboardButton(text=_("📅 События"), callback_data="events_calendar"),
        ],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1, 2, 2, 2)  # первый ряд - 1 кнопка, остальные по 2

    return keyboard.as_markup()


def back_to_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой возврата в главное меню."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("🏠 В главное меню"),
        callback_data="main_menu"
    )
    return builder.as_markup()
