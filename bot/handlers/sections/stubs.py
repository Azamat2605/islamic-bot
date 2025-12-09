from aiogram import Router, types, F
from aiogram.utils.i18n import gettext as _

router = Router(name="stubs")


# Список текстов кнопок, которые будут обрабатываться заглушкой
STUB_BUTTONS = {
    "Исламский помошник",
    "Расписание намазов",
    "Халяль места",
    "Обучение",
    "Календарь событий",
    "Знания",
}


@router.message(F.text.in_(STUB_BUTTONS))
async def section_stub_handler(message: types.Message) -> None:
    """
    Универсальный обработчик для кнопок, которые пока в разработке.
    Отправляет сообщение-заглушку.
    """
    await message.answer(_("Кнопка пока в разработке"))
