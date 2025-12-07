from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="main_menu")


@router.message(Command(commands=["menu", "main"]))
async def menu_handler(message: types.Message) -> None:
    """Показать главное меню."""
    await message.answer(_("Главное меню"), reply_markup=main_menu_keyboard())
