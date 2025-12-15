"""
Обработчики каталога сур.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline.knowledge.quran_kb import get_surah_catalog_kb
from bot.keyboards.inline.knowledge.main_kb import KnowledgeCallback

logger = logging.getLogger(__name__)

router = Router(name="quran_catalog")


@router.callback_query(KnowledgeCallback.filter((F.action == "section") & (F.section == "quran")))
async def quran_entry(callback: CallbackQuery, callback_data: KnowledgeCallback):
    """
    Обработчик входа в модуль Коран из меню Знаний.
    Показывает первую страницу каталога сур.
    """
    try:
        # Получаем клавиатуру каталога (страница 0)
        keyboard = get_surah_catalog_kb(page=0)

        # Формируем сообщение
        message_text = (
            "📖 **Коран**\n\n"
            "Выберите суру для чтения:\n"
            "_(Для навигации используйте кнопки ниже)_"
        )

        # Отправляем или редактируем сообщение
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
        logger.error(f"Error in quran_entry: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data.startswith("quran:page:"))
async def quran_page_handler(callback: CallbackQuery):
    """
    Обработчик пагинации каталога сур.
    Формат callback_data: quran:page:{page_number}
    """
    try:
        # Парсим номер страницы
        page_str = callback.data.split(":")[2]
        page = int(page_str) if page_str.isdigit() else 0

        # Получаем клавиатуру для запрошенной страницы
        keyboard = get_surah_catalog_kb(page=page)

        # Обновляем сообщение
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in quran_page_handler: {e}")
        await callback.answer("Ошибка пагинации", show_alert=True)


@router.callback_query(F.data == "know:quran_back")
async def quran_back_to_knowledge(callback: CallbackQuery):
    """
    Обработчик возврата из модуля Коран в меню Знаний.
    """
    try:
        # Импортируем здесь, чтобы избежать циклических импортов
        from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard

        keyboard = get_knowledge_main_keyboard()
        message_text = (
            "📚 **Знания (Ilm)**\n\n"
            "Добро пожаловать в раздел Знаний! Здесь вы найдете достоверные источники "
            "для изучения религии. Выберите интересующий вас раздел:"
        )

        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in quran_back_to_knowledge: {e}")
        await callback.answer("Ошибка возврата в меню Знаний", show_alert=True)
