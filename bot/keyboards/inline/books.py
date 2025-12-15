"""
Клавиатуры и CallbackData для модуля Книги.
Используем aiogram.filters.callback_data.CallbackData для type-safe навигации.
"""

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum
from typing import Optional

from bot.data.books_data import (
    BookCategory,
    get_all_categories,
    get_books_by_category,
    get_book_by_id,
    get_category_name,
    get_category_description
)


class BooksAction(str, Enum):
    """Действия модуля Книги"""
    MAIN = "main"          # Главное меню
    CATEGORY = "category"  # Выбор категории
    LIST = "list"          # Список книг в категории
    DETAILS = "details"    # Детали книги
    READ = "read"          # Чтение книги
    FAVORITE = "favorite"  # Избранное
    BACK = "back"          # Назад


class PaginationAction(str, Enum):
    """Действия пагинации"""
    PREV = "prev"          # Предыдущая страница
    NEXT = "next"          # Следующая страница
    PAGE = "page"          # Конкретная страница
    CLOSE = "close"        # Закрыть


class BooksCallback(CallbackData, prefix="books"):
    """
    CallbackData для навигации по книгам
    
    Формат: books:{action}:{category}:{book_id}:{page}
    Примеры:
      books:main:None:0:0       # Главное меню книг
      books:category:aqidah:0:0 # Выбор категории Акыда
      books:list:aqidah:0:0     # Список книг в Акыде
      books:details:aqidah:book_1:0  # Детали книги ID=book_1
      books:read:aqidah:book_1:1     # Чтение книги ID=book_1, страница 1
    """
    action: BooksAction
    category: Optional[str] = None
    book_id: Optional[str] = None
    page: Optional[int] = 0


class PaginationCallback(CallbackData, prefix="book_pagination"):
    """
    CallbackData для пагинации в режиме чтения
    
    Формат: book_pagination:{action}:{book_id}:{page}
    Примеры:
      book_pagination:prev:book_1:2  # Предыдущая страница книги ID=book_1 (с текущей страницы 2)
      book_pagination:next:book_1:2  # Следующая страница книги ID=book_1 (с текущей страницы 2)
      book_pagination:close:book_1:2 # Закрыть чтение, вернуться к деталям книги ID=book_1
    """
    action: PaginationAction
    book_id: str
    page: int


def get_categories_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура главного меню книг с категориями
    
    Возвращает:
        [Акыда] [Фикх]
        [Тасаввуф] [История]
        [Биографии]
        [Избранные] [Популярные]
        [Назад]
    """
    builder = InlineKeyboardBuilder()
    
    # Категории в 2 колонки
    categories = list(get_all_categories())
    for i in range(0, len(categories), 2):
        row_categories = categories[i:i+2]
        for category in row_categories:
            category_name = get_category_name(category)
            builder.button(
                text=category_name,
                callback_data=BooksCallback(
                    action=BooksAction.CATEGORY,
                    category=category.value
                )
            )
        builder.adjust(len(row_categories))
    
    # Кнопки внизу
    builder.button(
        text="⭐ Избранные",
        callback_data=BooksCallback(action=BooksAction.FAVORITE)
    )
    builder.button(
        text="🔥 Популярные",
        callback_data=BooksCallback(action=BooksAction.FAVORITE)  # Заглушка
    )
    builder.button(
        text="🔙 Назад",
        callback_data=BooksCallback(action=BooksAction.BACK)
    )
    
    builder.adjust(2, 2, 2, 1)  # 2 колонки для категорий, затем 2 кнопки, затем 1 кнопка
    return builder


def get_books_list_keyboard(category: BookCategory) -> InlineKeyboardBuilder:
    """
    Клавиатура списка книг в категории
    
    Args:
        category: Категория книг
        
    Возвращает:
        [1. Название книги 1]
        [2. Название книги 2]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    books = get_books_by_category(category)
    for book in books:
        # Обрезаем длинное название для кнопки
        button_text = f"{book.id}. {book.title}"
        if len(button_text) > 30:
            button_text = button_text[:27] + "..."
        
        builder.button(
            text=button_text,
            callback_data=BooksCallback(
                action=BooksAction.DETAILS,
                category=category.value,
                book_id=book.id
            )
        )
    
    builder.button(
        text="🔙 Назад",
        callback_data=BooksCallback(action=BooksAction.MAIN)
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder


def get_book_details_keyboard(book_id: str) -> InlineKeyboardBuilder:
    """
    Клавиатура деталей книги
    
    Args:
        book_id: ID книги (строка)
        
    Возвращает:
        [📖 Читать] [❤️ В избранное]
        [🔙 Назад]
    """
    builder = InlineKeyboardBuilder()
    
    book = get_book_by_id(book_id)
    if not book:
        return builder
    
    builder.button(
        text="📖 Читать",
        callback_data=BooksCallback(
            action=BooksAction.READ,
            category=book.category.value,
            book_id=book_id,
            page=0  # Первая страница
        )
    )
    
    builder.button(
        text="❤️ В избранное",
        callback_data=BooksCallback(
            action=BooksAction.FAVORITE,
            book_id=book_id
        )
    )
    
    builder.button(
        text="🔙 Назад",
        callback_data=BooksCallback(
            action=BooksAction.CATEGORY,
            category=book.category.value
        )
    )
    
    builder.adjust(2, 1)  # 2 кнопки в первом ряду, 1 во втором
    return builder


def get_reading_keyboard(book_id: str, current_page: int, total_pages: int) -> InlineKeyboardBuilder:
    """
    Клавиатура навигации в режиме чтения
    
    Args:
        book_id: ID книги (строка)
        current_page: Текущая страница (0-based)
        total_pages: Всего страниц
        
    Возвращает:
        [⬅️ Prev] [Page X/Y] [Next ➡️]
        [Закрыть]
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Предыдущая"
    if current_page > 0:
        builder.button(
            text="⬅️ Prev",
            callback_data=PaginationCallback(
                action=PaginationAction.PREV,
                book_id=book_id,
                page=current_page - 1
            )
        )
    else:
        # Неактивная кнопка если на первой странице
        builder.button(
            text="⬅️ Prev",
            callback_data=PaginationCallback(
                action=PaginationAction.PREV,
                book_id=book_id,
                page=current_page
            )
        )
    
    # Кнопка с номером страницы
    builder.button(
        text=f"Page {current_page + 1}/{total_pages}",
        callback_data=PaginationCallback(
            action=PaginationAction.PAGE,
            book_id=book_id,
            page=current_page
        )
    )
    
    # Кнопка "Следующая"
    if current_page < total_pages - 1:
        builder.button(
            text="Next ➡️",
            callback_data=PaginationCallback(
                action=PaginationAction.NEXT,
                book_id=book_id,
                page=current_page + 1
            )
        )
    else:
        # Неактивная кнопка если на последней странице
        builder.button(
            text="Next ➡️",
            callback_data=PaginationCallback(
                action=PaginationAction.NEXT,
                book_id=book_id,
                page=current_page
            )
        )
    
    # Кнопка "Закрыть"
    builder.button(
        text="Закрыть",
        callback_data=PaginationCallback(
            action=PaginationAction.CLOSE,
            book_id=book_id,
            page=current_page
        )
    )
    
    builder.adjust(3, 1)  # 3 кнопки в первом ряду, 1 во втором
    return builder


def get_back_to_books_keyboard() -> InlineKeyboardBuilder:
    """Простая клавиатура для возврата в главное меню книг"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📚 К книгам",
        callback_data=BooksCallback(action=BooksAction.MAIN)
    )
    return builder
