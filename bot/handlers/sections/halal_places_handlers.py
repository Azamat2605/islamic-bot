from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="halal_places")


@router.callback_query(F.data == "halal_places")
async def halal_places_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Халяль места'."""
    await callback.answer(
        "Раздел 'Халяль места' находится в разработке.",
        show_alert=True,
    )
