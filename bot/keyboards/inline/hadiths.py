"""
Клавиатуры и CallbackData для модуля Хадисы (группировка по темам).
Используем aiogram.filters.callback_data.CallbackData для type-safe навигации.
"""

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum
from typing import Optional

from bot.data.hadith_topics_data import (
    get_all_topics,
    get_topic_by_id,
    get_total_hadiths_in_topic
)


class HadithAction(str, Enum):
    """Действия модуля Хадисы"""
    MAIN = "main"          # Главное меню (выбор темы)
    TOPIC = "topic"        # Выбор темы
    SHOW = "show"          # Показать хадис
    PREV = "prev"          # Предыдущий хадис
    NEXT = "next"          # Следующий хадис
    BACK = "back"          # Назад


class HadithCallback(CallbackData, prefix="hadith"):
    """
    CallbackData для навигации по хадисам
    
    Формат: hadith:{action}:{topic_id}:{index}
    Примеры:
      hadith:main:None:None       # Главное меню хадисов
      hadith:topic:topic_nawawi:None  # Выбор темы "40 хадисов Ан-Навави"
      hadith:show:topic_nawawi:0      # Показать первый хадис темы
      hadith:prev:topic_nawawi:1      # Предыдущий хадис (с текущего индекса 1)
      hadith:next:topic_nawawi:1      # Следующий хадис (с текущего индекса 1)
    """
    action: HadithAction
    topic_id: Optional[str] = None
    index: Optional[int] = None


def get_hadith_topics_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура выбора темы хадисов
    
    Возвращает:
        [40 хадисов Ан-Навави]
        [Характер и нравственность]
        [Намаз (Салят)]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    topics = get_all_topics()
    for topic in topics:
        builder.button(
            text=topic.name,
            callback_data=HadithCallback(
                action=HadithAction.TOPIC,
                topic_id=topic.id
            )
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HadithCallback(action=HadithAction.BACK)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_hadith_pagination_keyboard(topic_id: str, current_index: int, total_count: int) -> InlineKeyboardBuilder:
    """
    Клавиатура пагинации для хадисов
    
    Args:
        topic_id: ID темы
        current_index: Текущий индекс хадиса (0-based)
        total_count: Общее количество хадисов в теме
        
    Возвращает:
        [⬅️ Prev] [ {index+1}/{total} ] [Next ➡️]
        [🔙 Back to Topics]
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Предыдущий"
    if current_index > 0:
        builder.button(
            text="⬅️ Prev",
            callback_data=HadithCallback(
                action=HadithAction.PREV,
                topic_id=topic_id,
                index=current_index - 1
            )
        )
    else:
        # Неактивная кнопка если на первом хадисе
        builder.button(
            text="⬅️ Prev",
            callback_data=HadithCallback(
                action=HadithAction.PREV,
                topic_id=topic_id,
                index=current_index
            )
        )
    
    # Кнопка с номером хадиса
    builder.button(
        text=f"{current_index + 1}/{total_count}",
        callback_data=HadithCallback(
            action=HadithAction.SHOW,
            topic_id=topic_id,
            index=current_index
        )
    )
    
    # Кнопка "Следующий"
    if current_index < total_count - 1:
        builder.button(
            text="Next ➡️",
            callback_data=HadithCallback(
                action=HadithAction.NEXT,
                topic_id=topic_id,
                index=current_index + 1
            )
        )
    else:
        # Неактивная кнопка если на последнем хадисе
        builder.button(
            text="Next ➡️",
            callback_data=HadithCallback(
                action=HadithAction.NEXT,
                topic_id=topic_id,
                index=current_index
            )
        )
    
    # Кнопка "Назад к темам"
    builder.button(
        text="🔙 Back to Topics",
        callback_data=HadithCallback(action=HadithAction.MAIN)
    )
    
    builder.adjust(3, 1)  # 3 кнопки в первом ряду, 1 во втором
    return builder


def get_back_to_hadiths_keyboard() -> InlineKeyboardBuilder:
    """Простая клавиатура для возврата в главное меню хадисов"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📜 К хадисам",
        callback_data=HadithCallback(action=HadithAction.MAIN)
    )
    return builder
