"""
Обработчики для модуля Хадисов.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.knowledge.main_kb import KnowledgeCallback
from bot.keyboards.inline.knowledge.hadith_kb import (
    get_hadith_books_kb,
    get_hadith_reading_kb
)
from bot.data.hadith_data import get_random_hadith, get_book_by_id

logger = logging.getLogger(__name__)
router = Router(name="hadith_catalog")


@router.callback_query(KnowledgeCallback.filter((F.action == "section") & (F.section == "hadith")))
async def hadith_entry(callback: CallbackQuery, callback_data: KnowledgeCallback):
    """
    Обработчик входа в модуль Хадисы из меню Знаний.
    Показывает меню выбора сборника (Полка).
    """
    try:
        keyboard = get_hadith_books_kb()
        
        message_text = _(
            "📜 **Хадисы**\n\n"
            "Выберите сборник хадисов:\n"
            "_(Для навигации используйте кнопки ниже)_"
        )
        
        if callback.message.text != message_text:
            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in hadith_entry: {e}")
        await callback.answer(_("Произошла ошибка. Попробуйте позже."), show_alert=True)


@router.callback_query(KnowledgeCallback.filter(F.action == "open_book"))
async def open_book_handler(callback: CallbackQuery, callback_data: KnowledgeCallback):
    """
    Обработчик открытия сборника хадисов.
    Показывает случайный хадис из выбранного сборника.
    """
    try:
        book_id = callback_data.book_id
        if not book_id:
            await callback.answer(_("Ошибка: не указан сборник."), show_alert=True)
            return
        
        book = get_book_by_id(book_id)
        if not book:
            await callback.answer(_("Сборник не найден."), show_alert=True)
            return
        
        # Получаем случайный хадис из сборника
        hadith = get_random_hadith(book_id=book_id)
        
        # Формируем сообщение
        message_text = _(
            "📖 **{book_name}**\n\n"
            "**Хадис #{number}**\n"
            "_{source}_\n\n"
            "**Арабский текст:**\n"
            "{arabic_text}\n\n"
            "**Перевод (Кулиев):**\n"
            "{translation}\n\n"
            "**Передатчик:** {narrator}\n"
            "**Достоверность:** {grade}\n"
        ).format(
            book_name=book["name_translation"],
            number=hadith["number"],
            source=hadith["source"],
            arabic_text=hadith["arabic_text"],
            translation=hadith["translation"]["kuliev"],
            narrator=hadith["narrator"],
            grade=hadith["grade"]
        )
        
        keyboard = get_hadith_reading_kb(book_id=book_id, hadith_id=hadith["id"])
        
        if callback.message.text != message_text:
            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in open_book_handler: {e}")
        await callback.answer(_("Произошла ошибка при загрузке хадиса."), show_alert=True)
