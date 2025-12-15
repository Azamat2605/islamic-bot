from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import get_main_menu
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

    welcome_text = _("Здравствуйте! Это ваш бот-помощник. Воспользуйтесь меню ниже для навигации:")
    await message.answer(welcome_text, reply_markup=get_main_menu())
