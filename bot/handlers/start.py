from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext as _

from bot.keyboards.main_menu import main_menu_keyboard
from bot.services.analytics import analytics

router = Router(name="start")


@router.message(CommandStart())
@analytics.track_event("Sign Up")
async def start_handler(message: types.Message) -> None:
    """Welcome message."""
    welcome_text = "Здравствуйте! Это ваш бот-помощник. Воспользуйтесь меню ниже для навигации:"
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())
