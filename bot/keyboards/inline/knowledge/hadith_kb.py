"""
Клавиатуры для модуля Хадисов.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.knowledge.main_kb import KnowledgeCallback
from bot.data.hadith_data import get_all_books, get_random_hadith


def get_hadith_books_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора сборника хадисов (Полка).
    
    Returns:
        InlineKeyboardMarkup с кнопками сборников и кнопкой "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    books = get_all_books()
    for book in books:
        builder.row(
            InlineKeyboardButton(
                text=_(book["name_translation"]),
                callback_data=KnowledgeCallback(
                    action="open_book",
                    book_id=book["id"]
                ).pack()
            )
        )
    
    # Кнопка "Назад" в меню Знаний
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад в Знания"),
            callback_data=KnowledgeCallback(action="section", section="hadith").pack()
        )
    )
    
    return builder.as_markup()


def get_hadith_reading_kb(book_id: str, hadith_id: str = None) -> InlineKeyboardMarkup:
    """
    Клавиатура чтения хадиса (бесконечная лента).
    
    Args:
        book_id: ID сборника
        hadith_id: ID текущего хадиса (не используется для случайного, но можно для будущего)
    
    Returns:
        InlineKeyboardMarkup с кнопками "Еще хадис" и "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка "🎲 Еще хадис" (случайный из того же сборника)
    builder.row(
        InlineKeyboardButton(
            text=_("🎲 Еще хадис"),
            callback_data=KnowledgeCallback(
                action="open_book",
                book_id=book_id
            ).pack()
        )
    )
    
    # Кнопка "📚 Сменить сборник" (возврат к выбору книг)
    builder.row(
        InlineKeyboardButton(
            text=_("📚 Сменить сборник"),
            callback_data=KnowledgeCallback(
                action="section",
                section="hadith"
            ).pack()
        )
    )
    
    # Кнопка "🔙 Назад в Знания"
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад в Знания"),
            callback_data=KnowledgeCallback(action="section", section="hadith").pack()
        )
    )
    
    return builder.as_markup()
