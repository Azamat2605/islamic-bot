from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="events_calendar")


@router.callback_query(F.data == "events_calendar")
async def events_calendar_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Календарь событий'."""
    await callback.answer(
        "Раздел 'Календарь событий' находится в разработке.",
        show_alert=True,
    )
