# Техническое задание: Модуль "Halal Places" (Халяль места)

## Обзор
Модуль "Halal Places" предоставляет пользователям возможность находить проверенные халяль места поблизости: мечети, рестораны, магазины, магазины одежды. Модуль реализует полный цикл: главный экран с статистикой → поиск ближайших мест (по геолокации) → поиск по категориям → детальная карточка места.

## Функциональные требования

### User Flow:

1. **Главный экран**:
   - Заголовок: "🥩 Халяль места"
   - Описание: "Find verified places nearby..."
   - Динамическая статистика: "🕌 Mosques: [count] 🍴 Restaurants: [count] 🛒 Shops: [count]"
   - Кнопки: [📍 Nearest Places], [🔍 Search / Categories], [Back]

2. **Сценарий "📍 Nearest Places"**:
   - Бот запрашивает геолокацию (ReplyButton)
   - Пользователь отправляет геопозицию
   - Логика: вычисление расстояния от пользователя до мест в БД, сортировка по расстоянию (возрастание)
   - Вывод: список 3-5 ближайших мест с расстоянием (например, "~0.8 км"), статусом (Открыто/Закрыто) и кнопкой [Details]
   - Кнопка внизу: [🗺 Show all on map] (опционально для MVP, можно пока просто список)

3. **Сценарий "🔍 Search / Categories"**:
   - Кнопки: [🕌 Mosques], [🍴 Restaurants], [🛒 Shops], [👕 Clothes]
   - Логика фильтрации: показать список, отфильтрованный по категории

4. **Карточка места (детальный просмотр)**:
   - Содержание: Название, Адрес, Время работы, Описание, Расстояние (если известна геопозиция)
   - Кнопки: [🗺 Show on map] (отправляет Venue/Location), [⭐️ Add to Favorites]

## Стек технологий
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.x + PostgreSQL
- Алгоритм гаверсинуса для расчёта расстояний
- Inline и Reply клавиатуры

## 1. Data Model Schema

### 1.1 Модель HalalPlace (добавить в database/models.py)

```python
import enum
from sqlalchemy import Enum, String, Float, Boolean, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class PlaceType(enum.Enum):
    MOSQUE = "mosque"          # Мечеть
    RESTAURANT = "restaurant"  # Ресторан
    SHOP = "shop"              # Магазин (продукты)
    CLOTHES = "clothes"        # Магазин одежды
    OTHER = "other"            # Другое

class HalalPlace(Base):
    __tablename__ = "halal_places"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place_type: Mapped[PlaceType] = mapped_column(Enum(PlaceType, native_enum=False), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    working_hours: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    photo_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    favorites: Mapped[list["HalalFavorite"]] = relationship(
        "HalalFavorite", back_populates="place", cascade="all, delete-orphan"
    )
```

### 1.2 Модель для избранного (опционально, можно добавить позже)

```python
class HalalFavorite(Base):
    __tablename__ = "halal_favorites"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    place_id: Mapped[int] = mapped_column(Integer, ForeignKey("halal_places.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    place: Mapped["HalalPlace"] = relationship("HalalPlace", back_populates="favorites")
    
    __table_args__ = (UniqueConstraint('user_id', 'place_id', name='uq_user_place_favorite'),)
```

### 1.3 Функция для расчёта расстояния (формула гаверсинуса)

```python
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Вычисляет расстояние между двумя точками на Земле (в км)
    используя формулу гаверсинуса.
    """
    R = 6371.0  # Радиус Земли в километрах
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)  # Округляем до 2 знаков после запятой
```

## 2. Callback Data Structure

### 2.1 CallbackData классы (bot/callbacks/halal.py)

```python
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from typing import Optional

class HalalAction(str, Enum):
    MAIN = "main"               # Главное меню
    NEAREST = "nearest"         # Ближайшие места
    CATEGORY = "category"       # Выбор категории
    PLACE_LIST = "place_list"   # Список мест
    PLACE_DETAILS = "place_details"  # Детали места
    FAVORITE = "favorite"       # Добавить в избранное
    MAP = "map"                 # Показать на карте
    BACK = "back"               # Назад

class HalalCallback(CallbackData, prefix="halal"):
    action: HalalAction
    category: Optional[str] = None
    place_id: Optional[int] = None
    page: Optional[int] = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
```

### 2.2 Альтернатива: простые строки для MVP

```
halal:main                     # Главное меню
halal:nearest                  # Ближайшие места (запрос геолокации)
halal:category:{category}      # Выбор категории
halal:place_list:{category}:{page}   # Список мест с пагинацией
halal:place_details:{place_id} # Детали места
halal:favorite:{place_id}      # Избранное (toggle)
halal:map:{place_id}           # Показать на карте
halal:back:{from_state}        # Назад
```

## 3. Interface States (Точные тексты/клавиатуры для каждого шага)

### 3.1 Screen 1: Главное меню Halal Places

**Текст**:
```
🥩 ХАЛЯЛЬ МЕСТА

Найдите проверенные места поблизости:
• Мечети для молитвы
• Рестораны с халяль едой
• Магазины с халяль продуктами
• Магазины одежды

📊 Статистика:
🕌 Мечети: {mosques_count}
🍴 Рестораны: {restaurants_count} 
🛒 Магазины: {shops_count}

Выберите действие:
```

**Клавиатура (Inline)**:
```
[📍 Ближайшие места] [🔍 Поиск по категориям]
[🔙 Назад]
```

### 3.2 Screen 2: Запрос геолокации (Nearest Places)

**Текст**:
```
📍 БЛИЖАЙШИЕ МЕСТА

Для поиска мест поблизости, пожалуйста, поделитесь своей геолокацией.

Нажмите кнопку ниже, чтобы отправить ваше местоположение:
```

**Клавиатура (Reply)**:
```
[📍 Отправить местоположение]
[🔙 Назад]
```

### 3.3 Screen 3: Список ближайших мест

**Текст** (пример):
```
📍 БЛИЖАЙШИЕ МЕСТА (отсортированы по расстоянию)

1. 🕌 Мечеть "Хазрат Султан"
   📍 ~0.8 км
   🕒 Открыто до 20:00
   ⭐ 4.8 (124 отзыва)

2. 🍴 Ресторан "Al-Noor"
   📍 ~1.2 км  
   🕒 Открыто до 23:00
   ⭐ 4.5 (89 отзывов)

3. 🛒 Магазин "Halal Market"
   📍 ~1.5 км
   🕒 Открыто до 22:00
   ⭐ 4.7 (203 отзыва)

Выберите место для подробной информации:
```

**Клавиатура (Inline)**:
```
[1. Мечеть "Хазрат Султан" →]
[2. Ресторан "Al-Noor" →]
[3. Магазин "Halal Market" →]
[🗺 Показать все на карте]
[🔙 Назад]
```

### 3.4 Screen 4: Поиск по категориям

**Текст**:
```
🔍 ПОИСК ПО КАТЕГОРИЯМ

Выберите категорию для поиска:

• 🕌 Мечети - места для молитвы
• 🍴 Рестораны - халяль кухня
• 🛒 Магазины - продукты
• 👕 Магазины одежды - мусульманская одежда
```

**Клавиатура (Inline)**:
```
[🕌 Мечети] [🍴 Рестораны]
[🛒 Магазины] [👕 Одежда]
[🔙 Назад]
```

### 3.5 Screen 5: Список мест в категории

**Текст** (пример для мечетей):
```
🕌 МЕЧЕТИ

Список мечетей в базе данных:

1. Мечеть "Хазрат Султан"
   📍 ул. Навои, 45
   🕒 05:00-20:00

2. Мечеть "Аль-Бухари"
   📍 пр. Амира Темура, 12
   🕒 05:00-21:00

3. Мечеть "Нур-Ислам"
   📍 ул. Шахрисабз, 78
   🕒 05:00-19:00

Выберите мечеть для подробной информации:
```

**Клавиатура (Inline)**:
```
[1. Мечеть "Хазрат Султан" →]
[2. Мечеть "Аль-Бухари" →]
[3. Мечеть "Нур-Ислам" →]
[🔙 Назад]
```

### 3.6 Screen 6: Детальная карточка места

**Текст** (пример):
```
🕌 МЕЧЕТЬ "ХАЗРАТ СУЛТАН"

📍 Адрес: ул. Навои, 45, Ташкент
🕒 Время работы: 05:00 - 20:00 (ежедневно)
📞 Телефон: +998 71 123 45 67
⭐ Рейтинг: 4.8 (124 отзыва)

Описание:
Одна из крупнейших мечетей города, построена в 2007 году. 
Вместимость: 5000 человек. Есть отдельные залы для женщин.

📍 Расстояние от вас: ~0.8 км
```

**Клавиатура (Inline)**:
```
[🗺 Показать на карте] [⭐️ Добавить в избранное]
[🔙 Назад]
```

### 3.7 Screen 7: Показать на карте

**Текст**:
```
🗺 МЕЧЕТЬ "ХАЗРАТ СУЛТАН"

Местоположение отправлено.
Вы можете открыть его в картах.
```

**Действие**: Бот отправляет `Venue` или `Location` с координатами места.

## 4. Service Layer (bot/services/halal_service.py)

### 4.1 Основные методы сервиса

```python
from typing import List, Optional, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import math

class HalalService:
    """Сервис для работы с халяль местами."""
    
    @staticmethod
    async def get_nearby_places(
        latitude: float,
        longitude: float,
        session: AsyncSession,
        limit: int = 5,
        radius_km: float = 10.0
    ) -> List[Dict]:
        """
        Получить ближайшие места в радиусе radius_km.
        """
        # Получаем все места из БД
        stmt = select(HalalPlace)
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        # Вычисляем расстояние и фильтруем
        nearby_places = []
        for place in places:
            distance = haversine_distance(latitude, longitude, place.latitude, place.longitude)
            if distance <= radius_km:
                place_dict = {
                    "id": place.id,
                    "title": place.title,
                    "place_type": place.place_type.value,
                    "address": place.address,
                    "distance": distance,
                    "working_hours": place.working_hours,
                    "phone": place.phone,
                    "is_verified": place.is_verified
                }
                nearby_places.append(place_dict)
        
        # Сортируем по расстоянию
        nearby_places.sort(key=lambda x: x["distance"])
        
        return nearby_places[:limit]
    
    @staticmethod
    async def get_places_by_category(
        category: str,
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict]:
        """
        Получить места по категории.
        """
        stmt = select(HalalPlace).where(
            HalalPlace.place_type == category
        ).order_by(HalalPlace.title).limit(limit)
        
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        return [
            {
                "id": place.id,
                "title": place.title,
                "address": place.address,
                "working_hours": place.working_hours,
                "phone": place.phone,
                "is_verified": place.is_verified
            }
            for place in places
        ]
    
    @staticmethod
    async def get_place_details(
        place_id: int,
        session: AsyncSession
    ) -> Optional[Dict]:
        """
        Получить детальную информацию о месте.
        """
        stmt = select(HalalPlace).where(HalalPlace.id == place_id)
        result = await session.execute(stmt)
        place = result.scalar_one_or_none()
        
        if not place:
            return None
        
        return {
            "id": place.id,
            "title": place.title,
            "place_type": place.place_type.value,
            "description": place.description,
            "address": place.address,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "working_hours": place.working_hours,
            "phone": place.phone,
            "photo_id": place.photo_id,
            "is_verified": place.is_verified,
            "created_at": place.created_at
        }
    
    @staticmethod
    async def get_counts_by_category(
        session: AsyncSession
    ) -> Dict[str, int]:
        """
        Получить статистику по категориям для главного экрана.
        """
        from database.models import PlaceType
        
        counts = {}
        for place_type in PlaceType:
            stmt = select(func.count(HalalPlace.id)).where(
                HalalPlace.place_type == place_type
            )
            result = await session.execute(stmt)
            count = result.scalar() or 0
            counts[place_type.value] = count
        
        return counts
    
    @staticmethod
    async def search_places(
        query: str,
        category: Optional[str] = None,
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict]:
        """
        Поиск мест по названию или адресу.
        """
        stmt = select(HalalPlace).where(
            HalalPlace.title.ilike(f"%{query}%") |
            HalalPlace.address.ilike(f"%{query}%")
        )
        
        if category:
            stmt = stmt.where(HalalPlace.place_type == category)
        
        stmt = stmt.order_by(HalalPlace.title).limit(limit)
        
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        return [
            {
                "id": place.id,
                "title": place.title,
                "address": place.address,
                "place_type": place.place_type.value,
                "working_hours": place.working_hours
            }
            for place in places
        ]
```

## 5. States (FSM) в bot/states/halal.py

```python
from aiogram.fsm.state import State, StatesGroup

class HalalStates(StatesGroup):
    """
    Состояния FSM для модуля Halal Places.
    """
    waiting_for_location = State()      # Ожидание геолокации
    waiting_for_search_query = State()  # Ожидание поискового запроса
    viewing_place_details = State()     # Просмотр деталей места
```

## 6. Keyboards Structure (bot/keyboards/inline/halal.py)

### 6.1 Основные клавиатуры

```python
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Optional

def get_halal_main_keyboard(counts: Dict[str, int]) -> InlineKeyboardMarkup:
    """
    Главная клавиатура Halal Places.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=f"📍 Ближайшие места",
        callback_data=HalalCallback(action="nearest")
    )
    builder.button(
        text=f"🔍 Поиск по категориям",
        callback_data=HalalCallback(action="category")
    )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action="back", from_state="main")
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
            callback_data=HalalCallback(action="category", category=category)
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action="back", from_state="categories")
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
    """
    builder = InlineKeyboardBuilder()
    
    for i, place in enumerate(places, 1):
        builder.button(
            text=f"{i}. {place['title']} →",
            callback_data=HalalCallback(
                action="place_details",
                place_id=place['id']
            )
        )
    
    # Кнопка показа на карте (если есть координаты)
    if places and len(places) > 0:
        builder.button(
            text="🗺 Показать все на карте",
            callback_data=HalalCallback(action="map", place_id=0)  # Специальный ID для "всех мест"
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action="back", from_state="list")
    )
    
    builder.adjust(1)  # По одному в ряд
    return builder.as_markup()

def get_place_details_keyboard(place_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """
    Клавиатура детальной карточки места.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🗺 Показать на карте",
        callback_data=HalalCallback(action="map", place_id=place_id)
    )
    
    favorite_text = "❤️ Убрать из избранного" if is_favorite else "⭐️ Добавить в избранное"
    builder.button(
        text=favorite_text,
        callback_data=HalalCallback(action="favorite", place_id=place_id)
    )
    
    builder.button(
        text="🔙 Назад",
        callback_data=HalalCallback(action="back", from_state="details")
    )
    
    builder.adjust(1)
    return builder.as_markup()
```

## 7. Handlers Structure (bot/handlers/sections/halal_places_handlers.py)

### 7.1 Основные обработчики

```python
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.halal_service import HalalService
from bot.states.halal import HalalStates
from bot.keyboards.inline.halal import (
    get_halal_main_keyboard,
    get_categories_keyboard,
    get_location_request_keyboard,
    get_places_list_keyboard,
    get_place_details_keyboard
)
from bot.callbacks.halal import HalalCallback, HalalAction

router = Router(name="halal_places")

# Главный обработчик раздела Halal Places
@router.callback_query(F.data == "halal_places")
async def halal_places_main_handler(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """
    Главный экран Halal Places.
    """
    # Получаем статистику по категориям
    counts = await HalalService.get_counts_by_category(session)
    
    # Формируем текст со статистикой
    text = _(
        "🥩 ХАЛЯЛЬ МЕСТА\n\n"
        "Найдите проверенные места поблизости:\n"
        "• Мечети для молитвы\n"
        "• Рестораны с халяль едой\n"
        "• Магазины с халяль продуктами\n"
        "• Магазины одежды\n\n"
        "📊 Статистика:\n"
        "🕌 Мечети: {mosques_count}\n"
        "🍴 Рестораны: {restaurants_count}\n"
        "🛒 Магазины: {shops_count}\n\n"
        "Выберите действие:"
    ).format(
        mosques_count=counts.get("mosque", 0),
        restaurants_count=counts.get("restaurant", 0),
        shops_count=counts.get("shop", 0) + counts.get("clothes", 0)
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_halal_main_keyboard(counts)
    )
    await callback.answer()

# Обработчик ближайших мест
@router.callback_query(HalalCallback.filter(F.action == HalalAction.NEAREST))
async def nearest_places_handler(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Запрос геолокации для поиска ближайших мест.
    """
    text = _(
        "📍 БЛИЖАЙШИЕ МЕСТА\n\n"
        "Для поиска мест поблизости, пожалуйста, поделитесь своей геолокацией.\n\n"
        "Нажмите кнопку ниже, чтобы отправить ваше местоположение:"
    )
    
    await callback.message.edit_text(text)
    await callback.message.answer(
        _("Пожалуйста, отправьте ваше местоположение:"),
        reply_markup=get_location_request_keyboard()
    )
    
    await state.set_state(HalalStates.waiting_for_location)
    await callback.answer()

# Обработчик полученной геолокации
@router.message(HalalStates.waiting_for_location, F.location)
async def location_received_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """
    Обработка полученной геолокации.
    """
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    
    # Получаем ближайшие места
    nearby_places = await HalalService.get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        session=session,
        limit=5,
        radius_km=10.0
    )
    
    if not nearby_places:
        text = _(
            "📍 БЛИЖАЙШИЕ МЕСТА\n\n"
            "К сожалению, в радиусе 10 км не найдено халяль мест.\n"
            "Попробуйте поискать по категориям."
        )
        await message.answer(text, reply_markup=get_categories_keyboard())
        await state.clear()
        return
    
    # Формируем текст со списком мест
    places_text = ""
    for i, place in enumerate(nearby_places, 1):
        place_type_emoji = {
            "mosque": "🕌",
            "restaurant": "🍴",
            "shop": "🛒",
            "clothes": "👕",
            "other": "📍"
        }.get(place["place_type"], "📍")
        
        places_text += _(
            "{i}. {emoji} {title}\n"
            "   📍 ~{distance} км\n"
            "   🕒 {working_hours}\n\n"
        ).format(
            i=i,
            emoji=place_type_emoji,
            title=place["title"],
            distance=place["distance"],
            working_hours=place["working_hours"] or _("Не указано")
        )
    
    text = _("📍 БЛИЖАЙШИЕ МЕСТА (отсортированы по расстоянию)\n\n{places}").format(
        places=places_text
    )
    
    await message.answer(
        text,
        reply_markup=get_places_list_keyboard(nearby_places)
    )
    await state.clear()

# Обработчик выбора категории
@router.callback_query(HalalCallback.filter(F.action == HalalAction.CATEGORY))
async def category_selection_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ списка мест в выбранной категории.
    """
    category = callback_data.category
    
    # Маппинг категорий на русские названия
    category_names = {
        "mosque": "🕌 МЕЧЕТИ",
        "restaurant": "🍴 РЕСТОРАНЫ",
        "shop": "🛒 МАГАЗИНЫ",
        "clothes": "👕 МАГАЗИНЫ ОДЕЖДЫ"
    }
    
    category_name = category_names.get(category, _("Категория"))
    
    # Получаем места по категории
    places = await HalalService.get_places_by_category(
        category=category,
        session=session,
        limit=10
    )
    
    if not places:
        text = _(
            "{category_name}\n\n"
            "В этой категории пока нет мест.\n"
            "Мы работаем над добавлением новых мест!"
        ).format(category_name=category_name)
        
        await callback.message.edit_text(
            text,
            reply_markup=get_categories_keyboard()
        )
        await callback.answer()
        return
    
    # Формируем текст со списком мест
    places_text = ""
    for i, place in enumerate(places, 1):
        places_text += _(
            "{i}. {title}\n"
            "   📍 {address}\n"
            "   🕒 {working_hours}\n\n"
        ).format(
            i=i,
            title=place["title"],
            address=place["address"],
            working_hours=place["working_hours"] or _("Не указано")
        )
    
    text = _("{category_name}\n\n{places}").format(
        category_name=category_name,
        places=places_text
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_places_list_keyboard(places)
    )
    await callback.answer()

# Обработчик деталей места
@router.callback_query(HalalCallback.filter(F.action == HalalAction.PLACE_DETAILS))
async def place_details_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ детальной информации о месте.
    """
    place_id = callback_data.place_id
    
    # Получаем детали места
    place = await HalalService.get_place_details(place_id, session)
    
    if not place:
        await callback.answer(_("Место не найдено."), show_alert=True)
        return
    
    # Маппинг типов мест на эмодзи
    place_type_emoji = {
        "mosque": "🕌",
        "restaurant": "🍴",
        "shop": "🛒",
        "clothes": "👕",
        "other": "📍"
    }.get(place["place_type"], "📍")
    
    # Формируем текст
    text = _(
        "{emoji} {title}\n\n"
        "📍 Адрес: {address}\n"
        "🕒 Время работы: {working_hours}\n"
        "📞 Телефон: {phone}\n"
        "{verified}\n\n"
        "{description}"
    ).format(
        emoji=place_type_emoji,
        title=place["title"],
        address=place["address"],
        working_hours=place["working_hours"] or _("Не указано"),
        phone=place["phone"] or _("Не указан"),
        verified=_("✅ Проверено") if place["is_verified"] else "",
        description=place["description"] or _("Описание отсутствует.")
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_place_details_keyboard(place_id, is_favorite=False)
    )
    await callback.answer()

# Обработчик показа на карте
@router.callback_query(HalalCallback.filter(F.action == HalalAction.MAP))
async def show_on_map_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ места на карте.
    """
    place_id = callback_data.place_id
    
    if place_id == 0:
        # Показать все места на карте (заглушка)
        await callback.answer(
            _("Функция показа всех мест на карте в разработке."),
            show_alert=True
        )
        return
    
    # Получаем детали места
    place = await HalalService.get_place_details(place_id, session)
    
    if not place:
        await callback.answer(_("Место не найдено."), show_alert=True)
        return
    
    # Отправляем местоположение
    await callback.message.answer_venue(
        latitude=place["latitude"],
        longitude=place["longitude"],
        title=place["title"],
        address=place["address"]
    )
    
    await callback.answer()

# Обработчик кнопки "Назад"
@router.callback_query(HalalCallback.filter(F.action == HalalAction.BACK))
async def back_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Обработка кнопки "Назад".
    """
    from_state = callback_data.from_state
    
    if from_state == "main":
        # Возврат в главное меню
        counts = await HalalService.get_counts_by_category(session)
        
        text = _(
            "🥩 ХАЛЯЛЬ МЕСТА\n\n"
            "Найдите проверенные места поблизости:\n"
            "• Мечети для молитвы\n"
            "• Рестораны с халяль едой\n"
            "• Магазины с халяль продуктами\n"
            "• Магазины одежды\n\n"
            "📊 Статистика:\n"
            "🕌 Мечети: {mosques_count}\n"
            "🍴 Рестораны: {restaurants_count}\n"
            "🛒 Магазины: {shops_count}\n\n"
            "Выберите действие:"
        ).format(
            mosques_count=counts.get("mosque", 0),
            restaurants_count=counts.get("restaurant", 0),
            shops_count=counts.get("shop", 0) + counts.get("clothes", 0)
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_halal_main_keyboard(counts)
        )
    
    elif from_state == "categories":
        # Возврат к выбору категории
        await callback.message.edit_text(
            _("🔍 ПОИСК ПО КАТЕГОРИЯМ\n\nВыберите категорию:"),
            reply_markup=get_categories_keyboard()
        )
    
    elif from_state in ["list", "details"]:
        # Возврат к списку категорий
        await callback.message.edit_text(
            _("🔍 ПОИСК ПО КАТЕГОРИЯМ\n\nВыберите категорию:"),
            reply_markup=get_categories_keyboard()
        )
    
    await callback.answer()
```

## 8. Implementation Steps (Пошаговый план для разработчика)

### Шаг 1: Миграция базы данных
1. **Добавить модель HalalPlace в `database/models.py`**
   - Скопировать код модели из раздела 1.1
   - Добавить импорт enum и необходимых полей
2. **Создать миграцию через Alembic**
   ```bash
   alembic revision -m "add_halal_places_table"
   ```
3. **Отредактировать созданный файл миграции**, добавив создание таблицы `halal_places`
4. **Запустить миграцию**:
   ```bash
   alembic upgrade head
   ```
5. **Создать скрипт для seeding тестовых данных** (`scripts/seed_halal.py`):
   - 5-10 тестовых мест (мечети, рестораны, магазины)
   - Использовать реальные координаты городов (Ташкент, Москва и т.д.)

### Шаг 2: Сервисный слой
1. **Создать файл `bot/services/halal_service.py`**
   - Скопировать код сервиса из раздела 4
   - Добавить функцию `haversine_distance`
   - Убедиться в правильности импортов
2. **Протестировать методы сервиса** через отдельный скрипт или интерактивно

### Шаг 3: Callback Data и состояния
1. **Создать `bot/callbacks/halal.py`** с CallbackData классами
2. **Создать `bot/states/halal.py`** с состояниями FSM
3. **Обновить `bot/callbacks/__init__.py`** для экспорта

### Шаг 4: Клавиатуры
1. **Создать `bot/keyboards/inline/halal.py`**
   - Реализовать все клавиатуры из раздела 6
   - Добавить русские тексты и эмодзи
2. **Обновить `bot/keyboards/__init__.py`** для экспорта

### Шаг 5: Обработчики
1. **Переписать `bot/handlers/sections/halal_places_handlers.py`**
   - Удалить существующую заглушку
   - Добавить все обработчики из раздела 7
   - Убедиться в правильных импортах
2. **Обновить `bot/handlers/__init__.py`** для подключения роутера

### Шаг 6: Интеграция и тестирование
1. **Добавить тестовые данные** через seeding скрипт
2. **Протестировать основные сценарии**:
   - Главный экран со статистикой
   - Запрос геолокации → список ближайших мест
   - Поиск по категориям → список мест → детальная карточка
   - Кнопка "Показать на карте"
   - Навигация "Назад"
3. **Исправить баги и улучшить UX**

## 9. Угловые случаи и обработка ошибок

### 9.1 Отсутствие мест в радиусе поиска
- Показать сообщение: "К сожалению, в радиусе X км не найдено халяль мест"
- Предложить поиск по категориям

### 9.2 Ошибка загрузки геолокации
- Если пользователь отказывается делиться геолокацией
- Предложить альтернативный поиск по категориям

### 9.3 Пустые категории
- Показать сообщение: "В этой категории пока нет мест"
- Предложить вернуться к выбору категории

### 9.4 Ошибки в callback данных
- Валидация `callback_data` перед использованием
- Обработка несуществующих `place_id`

### 9.5 Ограничения Telegram
- Максимальное количество кнопок в inline клавиатуре (100)
- Ограничение на длину текста сообщения (4096 символов)
- Форматирование текста (HTML/Markdown)

## 10. Будущие улучшения (post-MVP)

### 10.1 Дополнительные функции
- **Избранное**: Полноценная система избранных мест
- **Отзывы и рейтинги**: Пользовательские оценки и комментарии
- **Фотографии мест**: Галерея фотографий каждого места
- **Фильтры поиска**: По цене, рейтингу, времени работы
- **Маршруты**: Построение маршрута до места

### 10.2 Интеграции
- **Google Maps API**: Более точные карты и маршруты
- **Places API**: Автоматическое обновление информации о местах
- **Yandex Maps**: Для русскоязычной аудитории

### 10.3 Админ-панель
- **CRUD для мест**: Добавление, редактирование, удаление
- **Модерация**: Верификация пользовательских добавлений
- **Аналитика**: Статистика использования модуля

## 11. Критерии успеха MVP

### 11.1 Функциональность
- [ ] Главный экран с динамической статистикой
- [ ] Запрос геолокации и поиск ближайших мест
- [ ] Поиск по категориям (мечети, рестораны, магазины, одежда)
- [ ] Детальная карточка места с полной информацией
- [ ] Показ места на карте через Telegram Venue
- [ ] Навигация "Назад" между экранами

### 11.2 Производительность
- [ ] Быстрый расчет расстояний (гаверсинус)
- [ ] Оптимизированные SQL запросы
- [ ] Кэширование статистики и списков

### 11.3 Надежность
- [ ] Обработка ошибок геолокации
- [ ] Валидация входных данных
- [ ] Защита от несуществующих мест/категорий

### 11.4 UX/UI
- [ ] Понятные русские тексты с эмодзи
- [ ] Интуитивная навигация
- [ ] Соответствие дизайну других модулей бота

## Заключение

Данное техническое задание предоставляет полное описание модуля "Halal Places" для Islamic Telegram Bot. Реализация включает:

1. **Модель БД** с поддержкой геолокации и категорий
2. **Сервисный слой** с методами для поиска и фильтрации
3. **Полный user flow** от главного экрана до детальной карточки
4. **Интеграцию с картами** через Telegram Venue
5. **Навигацию** между всеми экранами модуля

Модуль спроектирован с учетом масштабируемости и может быть расширен в будущем добавлением отзывов, рейтингов, фотографий и интеграции с внешними картографическими сервисами.

---
*Документ подготовлен: 15.12.2025*  
*Версия спецификации: 1.0*  
*Статус: Готов к реализации*  
*Сложность: Средняя (4-5 дней для опытного разработчика)*  
*Автор: Senior Python Developer / Aiogram Specialist*
