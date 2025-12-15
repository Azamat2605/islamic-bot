"""
Обработчики для модуля Хадисы (группировка по темам).
Реализует навигацию по хадисам с использованием CallbackData фильтров и пагинации.
"""

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.hadiths import (
    HadithCallback,
    HadithAction,
    get_hadith_topics_keyboard,
    get_hadith_pagination_keyboard,
    get_back_to_hadiths_keyboard
)
from bot.data.hadith_topics_data import (
    get_topic_by_id,
    get_hadith_by_topic_and_index,
    get_total_hadiths_in_topic
)
from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard

router = Router(name="hadiths")


@router.callback_query(HadithCallback.filter(F.action == HadithAction.MAIN))
async def hadiths_main_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Главное меню хадисов (выбор темы)
    """
    await callback.answer()
    
    text = _(
        "📜 *Хадисы Пророка ﷺ*\n\n"
        "Выберите тему для изучения хадисов:\n"
        "Каждая тема содержит коллекцию хадисов с навигацией."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_hadith_topics_keyboard().as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(HadithCallback.filter(F.action == HadithAction.TOPIC))
async def hadith_topic_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Обработчик выбора темы хадисов
    Показывает первый хадис выбранной темы
    """
    await callback.answer()
    
    topic_id = callback_data.topic_id
    if not topic_id:
        await callback.message.answer(_("Ошибка: не указана тема"))
        return
    
    topic = get_topic_by_id(topic_id)
    if not topic:
        await callback.message.answer(_("Тема не найдена"))
        return
    
    # Получаем первый хадис темы
    hadith = get_hadith_by_topic_and_index(topic_id, 0)
    if not hadith:
        await callback.message.answer(_("Хадисы в этой теме не найдены"))
        return
    
    total_count = get_total_hadiths_in_topic(topic_id)
    
    # Формируем текст с хадисом
    text = _(
        "📖 *{topic_name}*\n\n"
        "**Хадис {current}/{total}**\n\n"
        "{hadith_text}\n\n"
        "📚 *Источник:* {source}\n\n"
        "Используйте кнопки ниже для навигации:"
    ).format(
        topic_name=topic.name,
        current=1,
        total=total_count,
        hadith_text=hadith.text,
        source=hadith.source
    )
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_hadith_pagination_keyboard(
                topic_id=topic_id,
                current_index=0,
                total_count=total_count
            ).as_markup(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        # Если текст не изменился (маловероятно при переходе между темами)
        error_msg = str(e)
        if "message is not modified" in error_msg:
            # Просто обновляем клавиатуру
            await callback.message.edit_reply_markup(
                reply_markup=get_hadith_pagination_keyboard(
                    topic_id=topic_id,
                    current_index=0,
                    total_count=total_count
                ).as_markup()
            )
        else:
            raise


@router.callback_query(HadithCallback.filter(F.action == HadithAction.SHOW))
async def hadith_show_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Показать конкретный хадис по индексу
    """
    await callback.answer()
    
    topic_id = callback_data.topic_id
    index = callback_data.index
    
    if not topic_id or index is None:
        await callback.message.answer(_("Ошибка: не указана тема или индекс"))
        return
    
    topic = get_topic_by_id(topic_id)
    if not topic:
        await callback.message.answer(_("Тема не найдена"))
        return
    
    hadith = get_hadith_by_topic_and_index(topic_id, index)
    if not hadith:
        await callback.message.answer(_("Хадис не найден"))
        return
    
    total_count = get_total_hadiths_in_topic(topic_id)
    
    # Формируем текст с хадисом
    text = _(
        "📖 *{topic_name}*\n\n"
        "**Хадис {current}/{total}**\n\n"
        "{hadith_text}\n\n"
        "📚 *Источник:* {source}\n\n"
        "Используйте кнопки ниже для навигации:"
    ).format(
        topic_name=topic.name,
        current=index + 1,
        total=total_count,
        hadith_text=hadith.text,
        source=hadith.source
    )
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_hadith_pagination_keyboard(
                topic_id=topic_id,
                current_index=index,
                total_count=total_count
            ).as_markup(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        # Если текст не изменился (например, нажали на ту же кнопку)
        error_msg = str(e)
        if "message is not modified" in error_msg:
            # Просто обновляем клавиатуру
            await callback.message.edit_reply_markup(
                reply_markup=get_hadith_pagination_keyboard(
                    topic_id=topic_id,
                    current_index=index,
                    total_count=total_count
                ).as_markup()
            )
        else:
            raise


@router.callback_query(HadithCallback.filter(F.action == HadithAction.PREV))
async def hadith_prev_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Обработчик кнопки "Предыдущий хадис"
    """
    await callback.answer()
    
    topic_id = callback_data.topic_id
    index = callback_data.index
    
    if not topic_id or index is None:
        await callback.message.answer(_("Ошибка: не указана тема или индекс"))
        return
    
    # Если нажали на неактивную кнопку (уже на первом хадисе)
    if index < 0:
        await callback.answer(_("Вы уже на первом хадисе"), show_alert=True)
        return
    
    # Перенаправляем на обработчик SHOW с новым индексом
    callback_data.action = HadithAction.SHOW
    await hadith_show_handler(callback, callback_data)


@router.callback_query(HadithCallback.filter(F.action == HadithAction.NEXT))
async def hadith_next_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Обработчик кнопки "Следующий хадис"
    """
    await callback.answer()
    
    topic_id = callback_data.topic_id
    index = callback_data.index
    
    if not topic_id or index is None:
        await callback.message.answer(_("Ошибка: не указана тема или индекс"))
        return
    
    total_count = get_total_hadiths_in_topic(topic_id)
    
    # Если нажали на неактивную кнопку (уже на последнем хадисе)
    if index >= total_count - 1:
        await callback.answer(_("Вы уже на последнем хадисе"), show_alert=True)
        return
    
    # Перенаправляем на обработчик SHOW с новым индексом
    callback_data.action = HadithAction.SHOW
    await hadith_show_handler(callback, callback_data)


@router.callback_query(HadithCallback.filter(F.action == HadithAction.BACK))
async def hadith_back_handler(
    callback: types.CallbackQuery,
    callback_data: HadithCallback
) -> None:
    """
    Возврат из модуля хадисов в главное меню знаний
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


# Обработчик для входа в модуль хадисов из главного меню знаний
@router.callback_query(F.data == "knowledge_hadiths")
async def knowledge_hadiths_entry_handler(callback: types.CallbackQuery) -> None:
    """
    Вход в модуль хадисов из главного меню знаний
    (Альтернативный вход через KnowledgeCallback)
    """
    await callback.answer()
    
    text = _(
        "📜 *Хадисы Пророка ﷺ*\n\n"
        "Выберите тему для изучения хадисов:\n"
        "Каждая тема содержит коллекцию хадисов с навигацией."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_hadith_topics_keyboard().as_markup(),
        parse_mode="Markdown"
    )
