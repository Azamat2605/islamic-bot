from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="knowledge")


@router.callback_query(F.data == "knowledge")
async def knowledge_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Знания'."""
    await callback.answer(
        "Раздел 'Знания' находится в разработке.",
        show_alert=True,
    )
