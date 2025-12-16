from aiogram import Router, F, types
from aiogram.utils.i18n import gettext as _
import logging

from bot.handlers.common.show_main_menu import show_main_menu

router = Router(name="common_nav")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery) -> None:
    """Обработчик возврата в главное меню."""
    logger.info(f"User {callback.from_user.id} clicked main_menu callback (common_nav handler)")
    
    # Используем универсальную функцию show_main_menu с удалением предыдущего сообщения
    # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст
    await show_main_menu(callback, delete_previous=True)
