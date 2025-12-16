from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.common.show_main_menu import show_main_menu
from bot.services.analytics import analytics
from database.crud import get_or_create_user_with_settings

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession) -> None:
    """Welcome message."""
    from_user = message.from_user
    # Сохраняем/обновляем пользователя в базе
    user, settings = await get_or_create_user_with_settings(
        session=session,
        telegram_id=from_user.id,
        full_name=from_user.full_name,
        username=from_user.username,
    )

    # Удаляем старую Reply Keyboard (Ghost Keyboard fix)
    remove_msg = await message.answer(
        "⌛",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await remove_msg.delete()

    # Показываем главное меню с Rich Media (изображение + HTML-текст)
    await show_main_menu(message)
