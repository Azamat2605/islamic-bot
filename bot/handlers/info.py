from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

router = Router(name="info")


@router.message(Command(commands=["info", "help", "about"]))
@router.message(F.text == __("ℹ️ Инфо"))
async def info_handler(message: types.Message) -> None:
    """Information about bot."""
    await message.answer(_("about"))
