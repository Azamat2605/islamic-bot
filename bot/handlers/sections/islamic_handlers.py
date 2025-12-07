from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="islamic")


@router.callback_query(F.data == "islamic_assistant")
async def islamic_assistant_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Исламский помощник'."""
    await callback.answer(
        "Раздел '📢 Исламский помощник' находится в разработке.",
        show_alert=True,
    )
