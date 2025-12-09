from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from bot.keyboards.inline.contacts import contacts_keyboard

router = Router(name="support")


@router.message(Command(commands=["supports", "support", "contacts", "contact"]))
@router.message(F.text == __("🆘 Поддержка"))
async def support_handler(message: types.Message) -> None:
    """Return a button with a link to the project."""
    await message.answer(_("support text"), reply_markup=contacts_keyboard())
