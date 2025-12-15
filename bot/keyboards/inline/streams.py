"""
Клавиатуры и CallbackData для модуля Эфиры (Streams).
Используем aiogram.filters.callback_data.CallbackData для type-safe навигации.
"""

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from enum import Enum
from typing import Optional

from bot.data.streams_data import (
    get_all_streams,
    get_stream_by_id,
    get_live_streams,
    get_recorded_streams,
    get_streams_sorted_by_date
)


class StreamsAction(str, Enum):
    """Действия модуля Эфиры"""
    MAIN = "main"          # Главное меню
    LIST = "list"          # Список всех эфиров
    LIVE = "live"          # Живые трансляции
    RECORDED = "recorded"  # Записи
    DETAILS = "details"    # Детали эфира
    BACK = "back"          # Назад


class StreamsCallback(CallbackData, prefix="streams"):
    """
    CallbackData для навигации по эфирам
    
    Формат: streams:{action}:{stream_id}
    Примеры:
      streams:main:None       # Главное меню эфиров
      streams:list:None       # Список всех эфиров
      streams:live:None       # Живые трансляции
      streams:recorded:None   # Записи
      streams:details:stream_1  # Детали эфира ID=stream_1
    """
    action: StreamsAction
    stream_id: Optional[str] = None


def get_streams_main_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура главного меню эфиров
    
    Возвращает:
        [📺 Все эфиры]
        [🔴 Живые трансляции]
        [📼 Записи]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📺 Все эфиры",
        callback_data=StreamsCallback(action=StreamsAction.LIST)
    )
    
    builder.button(
        text="🔴 Живые трансляции",
        callback_data=StreamsCallback(action=StreamsAction.LIVE)
    )
    
    builder.button(
        text="📼 Записи",
        callback_data=StreamsCallback(action=StreamsAction.RECORDED)
    )
    
    builder.button(
        text="🔙 Назад",
        callback_data=StreamsCallback(action=StreamsAction.BACK)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_streams_list_keyboard(show_live_only: bool = False, show_recorded_only: bool = False) -> InlineKeyboardBuilder:
    """
    Клавиатура списка эфиров
    
    Args:
        show_live_only: Показывать только живые трансляции
        show_recorded_only: Показывать только записи
        
    Возвращает:
        [1. 🔴 Название живого эфира]
        [2. 📼 Название записи]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    if show_live_only:
        streams = get_live_streams()
        prefix = "🔴"
    elif show_recorded_only:
        streams = get_recorded_streams()
        prefix = "📼"
    else:
        streams = get_streams_sorted_by_date()
        # Определяем префикс для каждого эфира
        prefixes = {True: "🔴", False: "📼"}
    
    for i, stream in enumerate(streams, 1):
        if show_live_only or show_recorded_only:
            prefix_display = prefix
        else:
            prefix_display = "🔴" if stream.is_live else "📼"
        
        # Обрезаем длинное название для кнопки
        button_text = f"{i}. {prefix_display} {stream.title}"
        if len(button_text) > 30:
            button_text = button_text[:27] + "..."
        
        builder.button(
            text=button_text,
            callback_data=StreamsCallback(
                action=StreamsAction.DETAILS,
                stream_id=stream.id
            )
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=StreamsCallback(action=StreamsAction.MAIN)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_stream_details_keyboard(stream_id: str) -> InlineKeyboardBuilder:
    """
    Клавиатура деталей эфира
    
    Args:
        stream_id: ID эфира (строка)
        
    Возвращает:
        [▶️ Watch on YouTube] (URL кнопка)
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    stream = get_stream_by_id(stream_id)
    if not stream:
        return builder
    
    # URL кнопка для просмотра
    builder.button(
        text="▶️ Watch on YouTube",
        url=stream.url
    )
    
    # Кнопка "Назад" - возвращает в соответствующий список
    if stream.is_live:
        back_action = StreamsAction.LIVE
    else:
        back_action = StreamsAction.RECORDED
    
    builder.button(
        text="🔙 Назад",
        callback_data=StreamsCallback(action=back_action)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_back_to_streams_keyboard() -> InlineKeyboardBuilder:
    """Простая клавиатура для возврата в главное меню эфиров"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📺 К эфирам",
        callback_data=StreamsCallback(action=StreamsAction.MAIN)
    )
    return builder
