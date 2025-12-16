from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

from bot.handlers.common.show_main_menu import show_main_menu

router = Router(name="main_menu")


@router.message(Command(commands=["menu", "main"]))
async def menu_handler(message: types.Message) -> None:
    """Показать главное меню."""
    await show_main_menu(message)
