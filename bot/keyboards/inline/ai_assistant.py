from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_ai_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню ИИ-помощника."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💬 ОБЩЕНИЕ", callback_data="ai_chat_mode")
    )
    builder.row(
        InlineKeyboardButton(text="🎨 Создание изображений", callback_data="ai_image_mode")
    )
    return builder.as_markup()


def get_ai_chat_actions_kb(result_id: str = "") -> InlineKeyboardMarkup:
    """
    Клавиатура действий после ответа ИИ.
    
    Args:
        result_id: Идентификатор результата для кнопки "Поделиться".
                   Если пустой, кнопка "Поделиться" будет неактивной.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Спросить другое", callback_data="ai_new_question")
    )
    # Заглушка для кнопки "Поделиться" - можно позже реализовать switch_inline_query
    share_button = InlineKeyboardButton(
        text="📤 Поделиться",
        callback_data="ai_share_stub"  # временная заглушка
    )
    builder.row(share_button)
    return builder.as_markup()
