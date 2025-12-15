"""
Клавиатуры и CallbackData для модуля Статьи (Articles).
Используем aiogram.filters.callback_data.CallbackData для type-safe навигации.
"""

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum
from typing import Optional

from bot.data.articles_data import get_all_articles, get_article_by_id


class ArticlesAction(str, Enum):
    """Действия модуля Статьи"""
    MAIN = "main"          # Главное меню (список статей)
    READ = "read"          # Чтение статьи
    BACK = "back"          # Назад


class ArticlesCallback(CallbackData, prefix="articles"):
    """
    CallbackData для навигации по статьям
    
    Формат: articles:{action}:{article_id}
    Примеры:
      articles:main:None       # Главное меню статей
      articles:read:article_1  # Чтение статьи с ID "article_1"
      articles:back:None       # Назад в Knowledge меню
    """
    action: ArticlesAction
    article_id: Optional[str] = None


def get_articles_list_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура списка статей
    
    Возвращает:
        [Важность намерения (Нийя)]
        [Этикет дуа (мольбы)]
        [Достоинства пятничной молитвы]
        [Терпение (Сабур) в исламе]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    articles = get_all_articles()
    for article in articles:
        builder.button(
            text=article.title,
            callback_data=ArticlesCallback(
                action=ArticlesAction.READ,
                article_id=article.id
            )
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=ArticlesCallback(action=ArticlesAction.BACK)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_article_read_keyboard(article_id: str) -> InlineKeyboardBuilder:
    """
    Клавиатура для чтения статьи
    
    Args:
        article_id: ID статьи
        
    Возвращает:
        [🔙 К списку статей]
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙 К списку статей",
        callback_data=ArticlesCallback(action=ArticlesAction.MAIN)
    )
    
    return builder


def get_back_to_articles_keyboard() -> InlineKeyboardBuilder:
    """Простая клавиатура для возврата в главное меню статей"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📰 К статьям",
        callback_data=ArticlesCallback(action=ArticlesAction.MAIN)
    )
    return builder
