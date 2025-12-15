from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_ai_quick_questions_kb() -> ReplyKeyboardMarkup:
    """
    Reply-клавиатура с быстрыми вопросами для ИИ-помощника.
    """
    builder = ReplyKeyboardBuilder()
    
    # Добавляем кнопки в два столбца для лучшего отображения
    builder.add(
        KeyboardButton(text="📜 Толкование аята"),
        KeyboardButton(text="🤲 Дуа на сегодня"),
        KeyboardButton(text="❓ Вопрос по фикху"),
        KeyboardButton(text="🔙 Выход"),
    )
    
    # Распределяем по 2 кнопки в ряд
    builder.adjust(2, 1, 1)
    
    return builder.as_markup(resize_keyboard=True)
