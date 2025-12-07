from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="profile")


@router.callback_query(F.data == "profile_settings")
async def profile_settings_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Мой профиль / настройки'."""
    await callback.answer(
        "Раздел '👤 МОЙ ПРОФИЛЬ / НАСТРОЙКИ' находится в разработке.",
        show_alert=True,
    )
