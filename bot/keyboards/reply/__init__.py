from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Возвращает главное меню в виде Reply-клавиатуры.
    Клавиатура располагается под полем ввода (постоянная клавиатура).
    Содержит 7 кнопок в 4 рядах (2+2+2+1).
    """
    buttons = [
        [
            KeyboardButton(text=_("🤖 Исламский помощник")),
            KeyboardButton(text=_("👤 Мой профиль")),
        ],
        [
            KeyboardButton(text=_("Расписание намазов")),
            KeyboardButton(text=_("Халяль места")),
        ],
        [
            KeyboardButton(text=_("Обучение")),
            KeyboardButton(text=_("Календарь событий")),
        ],
        [
            KeyboardButton(text=_("Знания")),
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=_("Выберите действие")
    )
