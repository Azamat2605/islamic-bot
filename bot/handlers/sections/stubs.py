from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

router = Router(name="stubs")


@router.message(F.text == __("Обучение"))
async def section_stub_handler(message: types.Message) -> None:
    """
    Универсальный обработчик для кнопок, которые пока в разработке.
    Отправляет сообщение-заглушку.
    """
    await message.answer(_("Кнопка пока в разработке"))
