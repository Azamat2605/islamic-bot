from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="prayer_schedule")


@router.callback_query(F.data == "prayer_schedule")
async def prayer_schedule_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Расписание намазов'."""
    await callback.answer(
        "Раздел 'Расписание намазов' находится в разработке.",
        show_alert=True,
    )
