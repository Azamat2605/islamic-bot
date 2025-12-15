from aiogram.filters.callback_data import CallbackData
from enum import Enum
from typing import Optional


class HalalAction(str, Enum):
    """Действия для модуля Halal Places."""
    MAIN = "main"               # Главное меню
    NEAREST = "nearest"         # Ближайшие места
    CATEGORY = "category"       # Выбор категории
    PLACE_LIST = "place_list"   # Список мест
    PLACE_DETAILS = "place_details"  # Детали места
    FAVORITE = "favorite"       # Добавить в избранное
    MAP = "map"                 # Показать на карте
    BACK = "back"               # Назад


class HalalCallback(CallbackData, prefix="halal"):
    """Callback данные для модуля Halal Places."""
    action: HalalAction
    category: Optional[str] = None
    place_id: Optional[int] = None
    page: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    from_state: Optional[str] = None
