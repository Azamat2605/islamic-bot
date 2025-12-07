from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="education")


@router.callback_query(F.data == "education")
async def education_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Обучение'."""
    await callback.answer(
        "Раздел 'Обучение' находится в разработке.",
        show_alert=True,
    )
