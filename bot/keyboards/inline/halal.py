from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Optional

from bot.callbacks.halal import HalalCallback, HalalAction


def get_halal_main_keyboard(counts: Dict[str, int]) -> InlineKeyboardMarkup:
    """
    Главная клавиатура Halal Places.
    
    Args:
        counts: Словарь с количеством мест по категориям
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=f"📍 Ближайшие места",
        callback_data=HalalCallback(action=HalalAction.NEAREST)
    )
    builder.button(
        text=f"🔍 Поиск по категориям",
        callback_data=HalalCallback(action=HalalAction.CATEGORY)
    )
    
    builder.button(
        text="🏠 В главное меню",
        callback_data="main_menu"
    )
    
    builder.adjust(1)  # По одному в ряд
    return builder.as_markup()


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора категории.
    """
    builder = InlineKeyboardBuilder()
    
    categories = [
        ("🕌 Мечети", "mosque"),
        ("🍴 Рестораны", "restaurant"),
        ("🛒 Магазины", "shop"),
        ("👕 Магазины одежды", "clothes"),
    ]
    
    for text, category in categories:
        builder.button(
            text=text,
            callback_data=HalalCallback(action=HalalAction.CATEGORY, category=category)
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action=HalalAction.BACK, from_state="categories")
    )
    
    builder.adjust(2)  # По 2 в ряд
    return builder.as_markup()


def get_location_request_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура запроса геолокации (Reply).
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить местоположение", request_location=True)],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_places_list_keyboard(places: List[Dict], current_page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура списка мест.
    
    Args:
        places: Список словарей с информацией о местах
        current_page: Текущая страница пагинации
    """
    builder = InlineKeyboardBuilder()
    
    for i, place in enumerate(places, 1):
        builder.button(
            text=f"{i}. {place['title']} →",
            callback_data=HalalCallback(
                action=HalalAction.PLACE_DETAILS,
                place_id=place['id']
            )
        )
    
    # Кнопка показа на карте (если есть координаты)
    if places and len(places) > 0:
        builder.button(
            text="🗺 Показать все на карте",
            callback_data=HalalCallback(action=HalalAction.MAP, place_id=0)  # Специальный ID для "всех мест"
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action=HalalAction.BACK, from_state="list")
    )
    
    builder.adjust(1)  # По одному в ряд
    return builder.as_markup()


def get_place_details_keyboard(place_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """
    Клавиатура детальной карточки места.
    
    Args:
        place_id: ID места
        is_favorite: Флаг, находится ли место в избранном
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🗺 Показать на карте",
        callback_data=HalalCallback(action=HalalAction.MAP, place_id=place_id)
    )
    
    favorite_text = "❤️ Убрать из избранного" if is_favorite else "⭐️ Добавить в избранное"
    builder.button(
        text=favorite_text,
        callback_data=HalalCallback(action=HalalAction.FAVORITE, place_id=place_id)
    )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action=HalalAction.BACK, from_state="details")
    )
    
    builder.adjust(1)
    return builder.as_markup()
