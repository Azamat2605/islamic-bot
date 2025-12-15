# Техническая спецификация 004: Модуль "Книги" (Books) в разделе "Знания"

## Обзор
Модуль "Книги" предоставляет пользователям доступ к исламской литературе по категориям: Акыда, Фикх, Тасаввуф, История, Биографии. Модуль является подразделом раздела "Знания" и реализует полный цикл: выбор категории → список книг → детали книги → режим чтения (галерея страниц).

## Стек технологий
- Python 3.11
- Aiogram 3.x
- Static mock data (Python dictionaries) - без базы данных для MVP
- InlineKeyboardBuilder для создания клавиатур
- Callback Factories для навигации

## 1. Архитектура модуля

### 1.1 Интеграция с существующей структурой
Модуль "Книги" является подмодулем раздела "Знания". Существующая структура:
```
bot/handlers/sections/knowledge/
├── __init__.py
├── menu.py (главное меню раздела "Знания")
├── quran/ (существующий подмодуль)
├── hadith/ (существующий подмодуль)
└── books/ (новый подмодуль)
    ├── __init__.py
    ├── catalog.py (категории и список книг)
    ├── details.py (детали книги)
    └── reading.py (режим чтения/галерея)
```

### 1.2 Точка входа
Пользователь проходит путь:
1. Главное меню → "Знания" → "📚 Книги"
2. Открывается **Screen 1: Главное меню книг** с категориями

## 2. Структура файлов

### 2.1 Новые файлы

#### Обработчики
```
bot/handlers/sections/knowledge/books/
├── __init__.py              # Роутер модуля Книги
├── catalog.py               # Обработчики категорий и списка книг
├── details.py               # Обработчики деталей книги
└── reading.py               # Обработчики режима чтения (галерея)
```

#### Клавиатуры
```
bot/keyboards/inline/knowledge/
├── __init__.py
├── main_kb.py (существующий)
├── quran_kb.py (существующий)
├── hadith_kb.py (существующий)
└── books_kb.py (новый)      # Клавиатуры модуля Книги
```

#### Данные
```
bot/data/
├── __init__.py
├── mock_knowledge.py (существующий)
├── hadith_data.py (существующий)
└── books_data.py (новый)    # Мок-данные для книг
```

#### Callback Factories
```
bot/callbacks/
├── __init__.py
└── books.py (новый)         # CallbackData классы для книг
```

### 2.2 Роутеры и иерархия
```python
# bot/handlers/sections/knowledge/books/__init__.py
from aiogram import Router

books_router = Router(name="books")

# Импорт обработчиков
from . import catalog, details, reading

# Включение подроутеров
books_router.include_router(catalog.router)
books_router.include_router(details.router)
books_router.include_router(reading.router)

# bot/handlers/sections/knowledge/__init__.py (обновить)
from .books import books_router
knowledge_router.include_router(books_router)
```

## 3. Структура данных

### 3.1 Мок-данные книг (bot/data/books_data.py)
```python
"""
Мок-данные для модуля Книги.
Для MVP используем hardcoded данные по требованиям.
"""

from typing import TypedDict, List, Optional
from dataclasses import dataclass
from enum import Enum


class BookCategory(str, Enum):
    """Категории книг"""
    AQIDAH = "aqidah"      # Акыда
    FIQH = "fiqh"          # Фикх
    TASAWWUF = "tasawwuf"  # Тасаввуф
    HISTORY = "history"    # История
    BIOGRAPHY = "biography" # Биографии


@dataclass
class Book:
    """Модель книги"""
    id: int
    category: BookCategory
    title: str
    author: str
    description: str
    cover_url: str  # URL обложки
    page_images: List[str]  # Список URL изображений страниц
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.page_images:
            raise ValueError("Книга должна содержать хотя бы одну страницу")
        if not self.cover_url:
            self.cover_url = self.page_images[0] if self.page_images else ""


# Hardcoded данные книг согласно требованиям
BOOKS_DATA: List[Book] = [
    # Акыда (2 книги)
    Book(
        id=1,
        category=BookCategory.AQIDAH,
        title="Китаб ат-Таухид",
        author="Мухаммад ибн Абд аль-Ваххаб",
        description="Фундаментальный труд по исламскому единобожию (таухиду), "
                   "разъясняющий основы вероубеждения и очищения веры от ширка.",
        cover_url="https://placehold.co/600x800?text=Китаб+ат-Таухид+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Китаб+ат-Таухид+Page+1",
            "https://placehold.co/600x800?text=Китаб+ат-Таухид+Page+2",
            "https://placehold.co/600x800?text=Китаб+ат-Таухид+Page+3",
            "https://placehold.co/600x800?text=Китаб+ат-Таухид+Page+4",
            "https://placehold.co/600x800?text=Китаб+ат-Таухид+Page+5",
        ]
    ),
    Book(
        id=2,
        category=BookCategory.AQIDAH,
        title="Акыда ат-Тахавия",
        author="Имам Абу Джафар ат-Тахави",
        description="Классический текст по вероубеждению ахлю-с-сунна валь-джамаа, "
                   "принятый всеми исламскими мазхабами как эталон правильной акыды.",
        cover_url="https://placehold.co/600x800?text=Акыда+ат-Тахавия+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Акыда+ат-Тахавия+Page+1",
            "https://placehold.co/600x800?text=Акыда+ат-Тахавия+Page+2",
            "https://placehold.co/600x800?text=Акыда+ат-Тахавия+Page+3",
        ]
    ),
    
    # Фикх (2 книги)
    Book(
        id=3,
        category=BookCategory.FIQH,
        title="Мухтасар аль-Кудури",
        author="Абу-ль-Хусейн аль-Кудури (Ханафитский мазхаб)",
        description="Один из основных текстов ханафитского фикха, охватывающий "
                   "все разделы исламского права от очищения до торговли.",
        cover_url="https://placehold.co/600x800?text=Мухтасар+аль-Кудури+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Мухтасар+аль-Кудури+Page+1",
            "https://placehold.co/600x800?text=Мухтасар+аль-Кудури+Page+2",
            "https://placehold.co/600x800?text=Мухтасар+аль-Кудури+Page+3",
            "https://placehold.co/600x800?text=Мухтасар+аль-Кудури+Page+4",
        ]
    ),
    Book(
        id=4,
        category=BookCategory.FIQH,
        title="Сады праведных (избранное)",
        author="Имам ан-Навави",
        description="Избранные хадисы из сборника 'Рийад ас-Салихин', касающиеся "
                   "фикха, нравственности и поклонения.",
        cover_url="https://placehold.co/600x800?text=Сады+праведных+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Сады+праведных+Page+1",
            "https://placehold.co/600x800?text=Сады+праведных+Page+2",
        ]
    ),
    
    # Тасаввуф (1 книга)
    Book(
        id=5,
        category=BookCategory.TASAWWUF,
        title="Благонравие праведников (избранное)",
        author="Абу Хамид аль-Газали",
        description="Избранные главы из 'Ихья улюм ад-дин', посвященные очищению "
                   "души, искренности и духовному совершенствованию.",
        cover_url="https://placehold.co/600x800?text=Благонравие+праведников+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Благонравие+праведников+Page+1",
            "https://placehold.co/600x800?text=Благонравие+праведников+Page+2",
            "https://placehold.co/600x800?text=Благонравие+праведников+Page+3",
        ]
    ),
    
    # История (1 книга)
    Book(
        id=6,
        category=BookCategory.HISTORY,
        title="Истории пророков",
        author="Ибн Касир",
        description="Подробное изложение историй пророков от Адама до Мухаммада ﷺ "
                   "на основе Корана и достоверных хадисов.",
        cover_url="https://placehold.co/600x800?text=Истории+пророков+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Истории+пророков+Page+1",
            "https://placehold.co/600x800?text=Истории+пророков+Page+2",
            "https://placehold.co/600x800?text=Истории+пророков+Page+3",
            "https://placehold.co/600x800?text=Истории+пророков+Page+4",
            "https://placehold.co/600x800?text=Истории+пророков+Page+5",
        ]
    ),
    
    # Биографии (1 книга)
    Book(
        id=7,
        category=BookCategory.BIOGRAPHY,
        title="Жизнь Пророка (Ar-Raheeq Al-Makhtum)",
        author="Сафи ар-Рахман аль-Мубаракфури",
        description="Полная биография Пророка Мухаммада ﷺ, удостоенная первой "
                   "премии на конкурсе биографии Пророка в 1979 году.",
        cover_url="https://placehold.co/600x800?text=Жизнь+Пророка+Cover",
        page_images=[
            "https://placehold.co/600x800?text=Жизнь+Пророка+Page+1",
            "https://placehold.co/600x800?text=Жизнь+Пророка+Page+2",
            "https://placehold.co/600x800?text=Жизнь+Пророка+Page+3",
            "https://placehold.co/600x800?text=Жизнь+Пророка+Page+4",
        ]
    ),
]


# Вспомогательные функции
def get_book_by_id(book_id: int) -> Optional[Book]:
    """Получить книгу по ID"""
    for book in BOOKS_DATA:
        if book.id == book_id:
            return book
    return None


def get_books_by_category(category: BookCategory) -> List[Book]:
    """Получить все книги категории"""
    return [book for book in BOOKS_DATA if book.category == category]


def get_all_categories() -> List[BookCategory]:
    """Получить все уникальные категории"""
    return list(set(book.category for book in BOOKS_DATA))


def get_category_name(category: BookCategory) -> str:
    """Получить русское название категории"""
    category_names = {
        BookCategory.AQIDAH: "Акыда",
        BookCategory.FIQH: "Фикх",
        BookCategory.TASAWWUF: "Тасаввуф",
        BookCategory.HISTORY: "История",
        BookCategory.BIOGRAPHY: "Биографии",
    }
    return category_names.get(category, category.value)


def get_category_description(category: BookCategory) -> str:
    """Получить описание категории"""
    descriptions = {
        BookCategory.AQIDAH: "Книги по исламскому вероубеждению и единобожию",
        BookCategory.FIQH: "Книги по исламскому праву и jurisprudence",
        BookCategory.TASAWWUF: "Книги по духовному очищению и нравственности",
        BookCategory.HISTORY: "Исторические труды и хроники",
        BookCategory.BIOGRAPHY: "Биографии пророков и выдающихся мусульман",
    }
    return descriptions.get(category, "")
```

## 4. Callback Data Structure

### 4.1 CallbackData классы (bot/callbacks/books.py)
```python
"""
CallbackData классы для модуля Книги.
Используем aiogram.filters.callback_data.CallbackData для type-safe навигации.
"""

from aiogram.filters.callback_data import CallbackData
from enum import Enum
from typing import Optional


class BooksAction(str, Enum):
    """Действия модуля Книги"""
    CATEGORY = "category"      # Выбор категории
    LIST = "list"              # Список книг в категории
    DETAILS = "details"        # Детали книги
    READ = "read"              # Чтение книги
    FAVORITE = "favorite"      # Избранное
    BACK = "back"              # Назад


class PaginationAction(str, Enum):
    """Действия пагинации"""
    PREV = "prev"              # Предыдущая страница
    NEXT = "next"              # Следующая страница
    PAGE = "page"              # Конкретная страница
    CLOSE = "close"            # Закрыть


class BooksCallback(CallbackData, prefix="books"):
    """
    CallbackData для навигации по книгам
    
    Формат: books:{action}:{category}:{book_id}:{page}
    Примеры:
      books:category:aqidah:0:0     # Выбор категории Акыда
      books:list:aqidah:0:0         # Список книг в Акыде
      books:details:aqidah:1:0      # Детали книги ID=1
      books:read:aqidah:1:1         # Чтение книги ID=1, страница 1
    """
    action: BooksAction
    category: Optional[str] = None
    book_id: Optional[int] = None
    page: Optional[int] = 0


class PaginationCallback(CallbackData, prefix="book_pagination"):
    """
    CallbackData для пагинации в режиме чтения
    
    Формат: book_pagination:{action}:{book_id}:{page}
    Примеры:
      book_pagination:prev:1:2      # Предыдущая страница книги ID=1 (с текущей страницы 2)
      book_pagination:next:1:2      # Следующая страница книги ID=1 (с текущей страницы 2)
      book_pagination:page:1:3      # Перейти на страницу 3 книги ID=1
      book_pagination:close:1:2     # Закрыть чтение, вернуться к деталям книги ID=1
    """
    action: PaginationAction
    book_id: int
    page: int
```

### 4.2 Альтернатива: простые строки (для MVP)
```python
# Для MVP можно использовать простые строковые форматы:
"""
books:main                     # Главное меню книг
books:category:{category}      # Выбор категории (aqidah, fiqh, etc.)
books:list:{category}:{page}   # Список книг в категории с пагинацией
books
