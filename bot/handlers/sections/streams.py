"""
Обработчики для модуля Эфиры (Streams).
Реализует навигацию по эфирам с использованием CallbackData фильтров.
"""

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.streams import (
    StreamsCallback,
    StreamsAction,
    get_streams_main_keyboard,
    get_streams_list_keyboard,
    get_stream_details_keyboard,
    get_back_to_streams_keyboard
)
from bot.data.streams_data import get_stream_by_id
from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard, KnowledgeCallback

router = Router(name="streams")


@router.callback_query(KnowledgeCallback.filter((F.action == "section") & (F.section == "streams")))
async def open_streams_main_menu(callback: types.CallbackQuery) -> None:
    """
    Обработчик входа в модуль эфиров из меню знаний
    """
    await callback.answer()
    
    text = _(
        "🎙 <b>Исламские Эфиры</b>\n\n"
        "Здесь вы можете найти исламские лекции, уроки и прямые трансляции.\n"
        "Выберите категорию:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_main_keyboard().as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.MAIN))
async def streams_main_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Главное меню эфиров
    """
    await callback.answer()
    
    text = _(
        "📺 *Эфиры и лекции*\n\n"
        "Здесь вы можете найти исламские лекции, уроки и прямые трансляции.\n"
        "Выберите категорию:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_main_keyboard().as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.LIST))
async def streams_list_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Список всех эфиров (смешанные: живые и записи)
    """
    await callback.answer()
    
    text = _(
        "📺 *Все эфиры*\n\n"
        "Список всех доступных эфиров и лекций, отсортированных по дате "
        "(новые первыми).\n"
        "🔴 - живые трансляции\n"
        "📼 - записи"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_list_keyboard().as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.LIVE))
async def streams_live_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Список живых трансляций
    """
    await callback.answer()
    
    text = _(
        "🔴 *Живые трансляции*\n\n"
        "Актуальные прямые эфиры, которые вы можете смотреть в реальном времени."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_list_keyboard(show_live_only=True).as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.RECORDED))
async def streams_recorded_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Список записей
    """
    await callback.answer()
    
    text = _(
        "📼 *Записи эфиров*\n\n"
        "Архив записанных лекций и уроков, которые вы можете посмотреть в любое время."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_list_keyboard(show_recorded_only=True).as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.DETAILS))
async def stream_details_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Детали конкретного эфира
    """
    await callback.answer()
    
    stream_id = callback_data.stream_id
    if not stream_id:
        await callback.message.answer(_("Ошибка: не указан ID эфира"))
        return
    
    stream = get_stream_by_id(stream_id)
    if not stream:
        await callback.message.answer(_("Эфир не найден"))
        return
    
    # Формируем текст с деталями
    status_emoji = "🔴" if stream.is_live else "📼"
    status_text = _("ЖИВАЯ ТРАНСЛЯЦИЯ") if stream.is_live else _("ЗАПИСЬ")
    
    text = _(
        "{status_emoji} *{status_text}*\n\n"
        "📌 *{title}*\n"
        "👤 *Лектор:* {speaker}\n"
        "📅 *Дата:* {date}\n\n"
        "📝 *Описание:*\n{description}\n\n"
        "Нажмите кнопку ниже, чтобы посмотреть эфир:"
    ).format(
        status_emoji=status_emoji,
        status_text=status_text,
        title=stream.title,
        speaker=stream.speaker,
        date=stream.date,
        description=stream.description
    )
    
    # Пытаемся отправить изображение с превью
    try:
        await callback.message.answer_photo(
            photo=stream.thumbnail_url,
            caption=text,
            reply_markup=get_stream_details_keyboard(stream_id).as_markup(),
            parse_mode="Markdown"
        )
        # Удаляем предыдущее сообщение со списком
        await callback.message.delete()
    except TelegramBadRequest as e:
        # Если не удалось отправить фото (например, невалидный URL),
        # отправляем просто текстовое сообщение
        error_msg = str(e)
        if "wrong file identifier" in error_msg or "failed" in error_msg:
            await callback.message.answer(
                text,
                reply_markup=get_stream_details_keyboard(stream_id).as_markup(),
                parse_mode="Markdown"
            )
            await callback.message.delete()
        else:
            raise


@router.callback_query(StreamsCallback.filter(F.action == StreamsAction.BACK))
async def streams_back_handler(
    callback: types.CallbackQuery,
    callback_data: StreamsCallback
) -> None:
    """
    Возврат из модуля эфиров в главное меню знаний
    """
    await callback.answer()
    
    text = _(
        "📚 *Раздел знаний*\n\n"
        "Выберите интересующий вас раздел:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_knowledge_main_keyboard().as_markup(),
        parse_mode="Markdown"
    )


# Обработчик для входа в модуль эфиров из главного меню знаний
@router.callback_query(F.data == "knowledge_streams")
async def knowledge_streams_entry_handler(callback: types.CallbackQuery) -> None:
    """
    Вход в модуль эфиров из главного меню знаний
    """
    await callback.answer()
    
    text = _(
        "📺 *Эфиры и лекции*\n\n"
        "Здесь вы можете найти исламские лекции, уроки и прямые трансляции.\n"
        "Выберите категорию:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_streams_main_keyboard().as_markup(),
        parse_mode="Markdown"
    )
