from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.menu import main_keyboard

router = Router(name="menu")


@router.message(Command(commands=["menu", "main"]))
async def menu_handler(message: types.Message) -> None:
    """Return main menu."""
    await message.answer(_("title main keyboard"), reply_markup=main_keyboard())


@router.callback_query(F.data == "wallet")
async def wallet_callback(callback: types.CallbackQuery) -> None:
    """Handle wallet button press."""
    await callback.answer(_("Wallet feature is under development"), show_alert=True)


@router.callback_query(F.data == "premium")
async def premium_callback(callback: types.CallbackQuery) -> None:
    """Handle premium button press."""
    await callback.answer(_("Premium feature is under development"), show_alert=True)
