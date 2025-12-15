"""
Inline keyboards for the Knowledge module main menu.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _


class KnowledgeCallback(CallbackData, prefix="know"):
    """Callback data factory for Knowledge module."""
    action: str
    section: str | None = None
    page: int | None = None
    surah_id: int | None = None
    book_id: str | None = None
    hadith_id: str | None = None
    # Add any other fields you use in the code


def get_knowledge_main_keyboard() -> InlineKeyboardMarkup:
    """
    Main Knowledge Menu keyboard with 6 buttons in 2x3 grid.
    
    Structure:
    - Row 1: [📖 Коран] [📜 Хадисы]
    - Row 2: [📚 Книги] [🎓 Статьи]
    - Row 3: [🎙️ Эфиры] [🔍 Поиск]
    - Row 4: [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    # Row 1: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("📖 Коран"),
            callback_data=KnowledgeCallback(action="section", section="quran").pack()
        ),
        InlineKeyboardButton(
            text=_("📜 Хадисы"),
            callback_data=KnowledgeCallback(action="section", section="hadith").pack()
        )
    )
    
    # Row 2: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("📚 Книги"),
            callback_data=KnowledgeCallback(action="section", section="books").pack()
        ),
        InlineKeyboardButton(
            text=_("🎓 Статьи"),
            callback_data=KnowledgeCallback(action="section", section="articles").pack()
        )
    )
    
    # Row 3: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("🎙️ Эфиры"),
            callback_data=KnowledgeCallback(action="section", section="streams").pack()
        ),
        InlineKeyboardButton(
            text=_("🔍 Поиск"),
            callback_data=KnowledgeCallback(action="section", section="search").pack()
        )
    )
    
    # Row 4: 1 button (Back to Main Menu)
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()
