from aiogram import Router, F, types
from aiogram.utils.i18n import gettext as _
import logging

from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="common_nav")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery) -> None:
    """Обработчик возврата в главное меню."""
    logger.info(f"User {callback.from_user.id} clicked main_menu callback (common_nav handler)")
    try:
        await callback.message.edit_text(
            _("Главное меню"),
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"Main menu message edited for user {callback.from_user.id}")
    except Exception as e:
        logger.warning(f"Failed to edit message for user {callback.from_user.id}: {e}, sending new message")
        await callback.message.answer(
            _("Главное меню"),
            reply_markup=main_menu_keyboard()
        )
    await callback.answer()
