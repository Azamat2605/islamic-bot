"""
Knowledge module menu handlers.
"""
import logging
from contextlib import suppress

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from bot.keyboards.inline.knowledge.main_kb import (
    get_knowledge_main_keyboard,
    KnowledgeCallback
)

# Create router for knowledge menu
router = Router(name="knowledge_menu")
logger = logging.getLogger(__name__)


@router.message(F.text == __("Знания"))
@router.message(F.text == "Знания")  # Fallback for exact match
async def knowledge_entry(message: types.Message) -> None:
    """
    Entry point for Knowledge section (Reply Button).
    
    Handles the "Знания" text message from the main menu.
    """
    logger.info(f"User {message.from_user.id} entered Knowledge section via text message")
    
    try:
        # Debug log
        logger.info(f"DEBUG: Text received: '{message.text}'")
        
        # Hide the Reply Keyboard when entering inline-based Knowledge section
        from aiogram.types import ReplyKeyboardRemove
        
        # Welcome text for Knowledge section
        text = _(
            "📖 ЗНАНИЯ (ILM)\n\n"
            "Добро пожаловать в раздел Знаний! 🌟\n\n"
            "Здесь вы найдете достоверные источники для изучения религии:\n"
            "• Священный Коран с переводом и тафсиром\n"
            "• Хадисы Пророка ﷺ с объяснениями\n"
            "• Книги исламских ученых\n"
            "• Познавательные статьи\n"
            "• Прямые эфиры с преподавателями\n"
            "• Умный поиск по всем материалам\n\n"
            "Выберите интересующий вас раздел:"
        )
        
        # Send message with ReplyKeyboardRemove to hide the large keyboard
        await message.answer(
            text,
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Get the keyboard
        keyboard = get_knowledge_main_keyboard()
        logger.info(f"Keyboard created successfully, type: {type(keyboard)}")
        
        # Send a separate message with the Knowledge inline keyboard
        await message.answer(
            _("📚 Раздел Знаний: Выберите категорию"),
            reply_markup=keyboard
        )
        
        logger.info(f"Knowledge menu sent to user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in knowledge_entry handler: {e}", exc_info=True)
        # Try to send error message to user
        try:
            await message.answer(
                _("Произошла ошибка при загрузке меню. Пожалуйста, попробуйте позже.")
            )
        except:
            pass


@router.callback_query(F.data == "knowledge")
async def knowledge_callback_entry(callback: types.CallbackQuery) -> None:
    """
    Entry point for Knowledge section (Callback from main menu).
    
    Handles the callback from the main menu inline keyboard.
    """
    logger.info(f"User {callback.from_user.id} entered Knowledge section via main menu callback")
    
    # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение
    # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete previous message: {e}")
    
    # Welcome text for Knowledge section
    text = _(
        "📖 ЗНАНИЯ (ILM)\n\n"
        "Добро пожаловать в раздел Знаний! 🌟\n\n"
        "Здесь вы найдете достоверные источники для изучения религии:\n"
        "• Священный Коран с переводом и тафсиром\n"
        "• Хадисы Пророка ﷺ с объяснениями\n"
        "• Книги исламских ученых\n"
        "• Познавательные статьи\n"
        "• Прямые эфиры с преподавателями\n"
        "• Умный поиск по всем материалам\n\n"
        "Выберите интересующий вас раздел:"
    )
    
    # Отправляем новое сообщение с клавиатурой знаний
    await callback.message.answer(
        text,
        reply_markup=get_knowledge_main_keyboard()
    )
    await callback.answer()


@router.callback_query(KnowledgeCallback.filter(F.action == "section"))
async def knowledge_section_handler(
    callback: types.CallbackQuery,
    callback_data: KnowledgeCallback
) -> None:
    """
    Handle section selection in Knowledge menu.
    
    Shows stub message for sections under development, except for Quran
    which has its own handler in quran/catalog.py.
    """
    section = callback_data.section
    logger.info(f"User {callback.from_user.id} selected Knowledge section: {section}")
    
    # If section is "quran", "hadith", "books", or "streams", let their routers handle it
    # This handler should not process these callbacks
    if section in ["quran", "hadith", "books", "streams"]:
        # Let the callback fall through to other handlers
        # DO NOT call callback.answer() - let specific handlers do it
        return
    
    # Map section codes to human-readable names
    section_names = {
        "hadith": _("Хадисы"),
        "books": _("Книги"),
        "articles": _("Статьи"),
        "streams": _("Эфиры"),
        "search": _("Поиск")
    }
    
    section_name = section_names.get(section, _("Раздел"))
    
    # Stub message for sections under development
    text = _(
        "🚧 РАЗДЕЛ В РАЗРАБОТКЕ\n\n"
        "Функция \"{section_name}\" находится в разработке.\n"
        "Мы работаем над добавлением качественного контента!\n\n"
        "Ожидайте обновления в ближайшее время. ⏳"
    ).format(section_name=section_name)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_knowledge_main_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery) -> None:
    """
    Navigation handler for 'Main Menu' button.
    
    Returns to the root Main Menu and shows the Reply Keyboard.
    """
    logger.info(f"User {callback.from_user.id} clicked Main Menu from Knowledge")
    
    # Используем универсальную функцию show_main_menu для возврата в главное меню
    # Она сама удалит предыдущее сообщение и отправит фото-меню
    from bot.handlers.common.show_main_menu import show_main_menu
    await show_main_menu(callback, delete_previous=True)
