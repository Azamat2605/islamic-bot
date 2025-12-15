"""
Обработчики для модуля Статьи (Articles).
Реализует навигацию по статьям с использованием CallbackData фильтров.
"""

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.articles import (
    ArticlesCallback,
    ArticlesAction,
    get_articles_list_keyboard,
    get_article_read_keyboard
)
from bot.data.articles_data import get_article_by_id
from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard, KnowledgeCallback

router = Router(name="articles")


@router.callback_query(KnowledgeCallback.filter((F.action == "section") & (F.section == "articles")))
async def open_articles_main_menu(callback: types.CallbackQuery) -> None:
    """
    Обработчик входа в модуль статей из меню знаний
    """
    await callback.answer()
    
    text = _(
        "📰 <b>Исламские статьи</b>\n\n"
        "Здесь вы можете найти короткие исламские статьи на различные темы.\n"
        "Выберите статью для чтения:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_articles_list_keyboard().as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(ArticlesCallback.filter(F.action == ArticlesAction.MAIN))
async def articles_main_handler(
    callback: types.CallbackQuery,
    callback_data: ArticlesCallback
) -> None:
    """
    Главное меню статей (список статей)
    """
    await callback.answer()
    
    text = _(
        "📰 <b>Исламские статьи</b>\n\n"
        "Здесь вы можете найти короткие исламские статьи на различные темы.\n"
        "Выберите статью для чтения:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_articles_list_keyboard().as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(ArticlesCallback.filter(F.action == ArticlesAction.READ))
async def article_read_handler(
    callback: types.CallbackQuery,
    callback_data: ArticlesCallback
) -> None:
    """
    Обработчик чтения статьи
    """
    await callback.answer()
    
    article_id = callback_data.article_id
    if not article_id:
        await callback.message.answer(_("Ошибка: не указан ID статьи"))
        return
    
    article = get_article_by_id(article_id)
    if not article:
        await callback.message.answer(_("Статья не найдена"))
        return
    
    # Формируем текст статьи
    text = _(
        "📰 <b>{title}</b>\n\n"
        "{text}"
    ).format(
        title=article.title,
        text=article.text
    )
    
    # Пытаемся отправить изображение с текстом в подписи
    try:
        await callback.message.answer_photo(
            photo=article.image_url,
            caption=text,
            reply_markup=get_article_read_keyboard(article_id).as_markup(),
            parse_mode="HTML"
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
                reply_markup=get_article_read_keyboard(article_id).as_markup(),
                parse_mode="HTML"
            )
            await callback.message.delete()
        else:
            raise


@router.callback_query(ArticlesCallback.filter(F.action == ArticlesAction.BACK))
async def articles_back_handler(
    callback: types.CallbackQuery,
    callback_data: ArticlesCallback
) -> None:
    """
    Возврат из модуля статей в главное меню знаний
    """
    await callback.answer()
    
    text = _(
        "📚 <b>Раздел знаний</b>\n\n"
        "Выберите интересующий вас раздел:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_knowledge_main_keyboard().as_markup(),
        parse_mode="HTML"
    )


# Обработчик для входа в модуль статей из главного меню знаний
@router.callback_query(F.data == "knowledge_articles")
async def knowledge_articles_entry_handler(callback: types.CallbackQuery) -> None:
    """
    Вход в модуль статей из главного меню знаний
    (Альтернативный вход через KnowledgeCallback)
    """
    await callback.answer()
    
    text = _(
        "📰 <b>Исламские статьи</b>\n\n"
        "Здесь вы можете найти короткие исламские статьи на различные темы.\n"
        "Выберите статью для чтения:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_articles_list_keyboard().as_markup(),
        parse_mode="HTML"
    )
