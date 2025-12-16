from typing import Union, Optional
import logging
from aiogram import types
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.ui_config import ui_assets
from bot.keyboards.main_menu import main_menu_keyboard

logger = logging.getLogger(__name__)


async def show_main_menu(
    message_or_callback: Union[types.Message, types.CallbackQuery],
    session: Optional[AsyncSession] = None,
    delete_previous: bool = False
) -> None:
    """
    Универсальная функция отображения главного меню.
    
    Поддерживает как Message (команда /start, /menu), так и CallbackQuery (возврат из подраздела).
    
    Args:
        message_or_callback: Объект Message или CallbackQuery
        session: Сессия базы данных (опционально)
        delete_previous: Удалить предыдущее сообщение перед отправкой нового
    """
    # Определяем тип входящего объекта
    is_callback = isinstance(message_or_callback, types.CallbackQuery)
    
    if is_callback:
        callback = message_or_callback
        message = callback.message
        user_id = callback.from_user.id
    else:
        message = message_or_callback
        callback = None
        user_id = message.from_user.id
    
    logger.info(f"Showing main menu for user {user_id}, delete_previous={delete_previous}")
    
    try:
        # Удаляем предыдущее сообщение, если требуется
        if delete_previous and message:
            try:
                await message.delete()
                logger.debug(f"Deleted previous message for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not delete previous message for user {user_id}: {e}")
        
        # Получаем изображение и подпись
        file_id, image_url = ui_assets.get_main_menu_image()
        caption = ui_assets.get_localized_caption(
            username=message.from_user.full_name if message.from_user else "",
            language="ru"  # TODO: Получить язык пользователя из базы
        )
        
        # Отправляем фото-меню
        if file_id:
            # Используем file_id, если изображение уже загружено в Telegram
            sent_message = await message.answer_photo(
                photo=file_id,
                caption=caption,
                parse_mode=ui_assets.MAIN_MENU_PARSE_MODE,
                reply_markup=main_menu_keyboard()
            )
            logger.debug(f"Main menu sent with file_id for user {user_id}")
        else:
            # Используем URL
            sent_message = await message.answer_photo(
                photo=image_url,
                caption=caption,
                parse_mode=ui_assets.MAIN_MENU_PARSE_MODE,
                reply_markup=main_menu_keyboard()
            )
            logger.debug(f"Main menu sent with URL for user {user_id}")
        
        # Отвечаем на callback, если он есть
        if callback:
            await callback.answer()
            logger.debug(f"Callback answered for user {user_id}")
            
    except Exception as e:
        logger.error(f"Failed to show main menu for user {user_id}: {e}")
        
        # Fallback: отправляем текстовое меню в случае ошибки
        try:
            fallback_text = _("Главное меню")
            await message.answer(
                fallback_text,
                reply_markup=main_menu_keyboard()
            )
            if callback:
                await callback.answer()
            logger.info(f"Fallback text menu sent for user {user_id}")
        except Exception as fallback_error:
            logger.error(f"Fallback also failed for user {user_id}: {fallback_error}")
            if callback:
                await callback.answer(_("Произошла ошибка"), show_alert=True)
