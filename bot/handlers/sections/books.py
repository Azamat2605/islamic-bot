"""
Обработчики для модуля Книги.
Реализует полный user flow: категории -> список книг -> детали -> чтение.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from bot.data.books_data import (
    BookCategory,
    get_book_by_id,
    get_books_by_category,
    get_category_name,
    get_category_description
)
from bot.keyboards.inline.books import (
    BooksCallback,
    PaginationCallback,
    BooksAction,
    PaginationAction,
    get_categories_keyboard,
    get_books_list_keyboard,
    get_book_details_keyboard,
    get_reading_keyboard,
    get_back_to_books_keyboard
)
from bot.keyboards.inline.knowledge.main_kb import KnowledgeCallback

# Создаем роутер для модуля книг
books_router = Router(name="books")


@books_router.message(Command("books"))
async def cmd_books(message: Message):
    """
    Обработчик команды /books
    Показывает главное меню книг с категориями
    """
    text = (
        "📚 *КНИГИ*\n\n"
        "Добро пожаловать в раздел исламской литературы! Здесь вы найдете книги по:\n\n"
        "• *Акыда* (Вероубеждение)\n"
        "• *Фикх* (Исламское право)\n"
        "• *Тасаввуф* (Духовность)\n"
        "• *История*\n"
        "• *Биографии*\n\n"
        "Выберите категорию:"
    )
    
    keyboard = get_categories_keyboard()
    
    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.MAIN))
async def show_books_main(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Показывает главное меню книг
    """
    text = (
        "📚 *КНИГИ*\n\n"
        "Добро пожаловать в раздел исламской литературы! Здесь вы найдете книги по:\n\n"
        "• *Акыда* (Вероубеждение)\n"
        "• *Фикх* (Исламское право)\n"
        "• *Тасаввуф* (Духовность)\n"
        "• *История*\n"
        "• *Биографии*\n\n"
        "Выберите категорию:"
    )
    
    keyboard = get_categories_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.CATEGORY))
async def show_category_books(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Показывает список книг в выбранной категории
    """
    if not callback_data.category:
        await callback.answer("Ошибка: категория не указана")
        return
    
    try:
        category = BookCategory(callback_data.category)
    except ValueError:
        await callback.answer("Ошибка: неверная категория")
        return
    
    category_name = get_category_name(category)
    category_desc = get_category_description(category)
    books = get_books_by_category(category)
    
    if not books:
        text = f"📖 *{category_name.upper()}*\n\n{category_desc}\n\nВ этой категории пока нет книг."
        keyboard = get_back_to_books_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Формируем текст со списком книг
    books_list = "\n".join([
        f"{i+1}. *{book.title}*\n   Автор: {book.author}"
        for i, book in enumerate(books)
    ])
    
    text = (
        f"📖 *{category_name.upper()}*\n\n"
        f"{category_desc}\n\n"
        f"{books_list}\n\n"
        f"Выберите книгу для подробного просмотра:"
    )
    
    keyboard = get_books_list_keyboard(category)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.DETAILS))
async def show_book_details(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Показывает детали выбранной книги
    """
    if not callback_data.book_id:
        await callback.answer("Ошибка: ID книги не указан")
        return
    
    book = get_book_by_id(callback_data.book_id)
    if not book:
        await callback.answer("Ошибка: книга не найдена")
        return
    
    category_name = get_category_name(book.category)
    
    text = (
        f"📘 *{book.title.upper()}*\n\n"
        f"*Автор:* {book.author}\n\n"
        f"{book.description}\n\n"
        f"📖 *Страниц:* {len(book.page_images)}\n"
        f"🏷️ *Категория:* {category_name}"
    )
    
    keyboard = get_book_details_keyboard(book.id)
    
    # Отправляем изображение обложки с обработкой ошибок
    try:
        # Удаляем предыдущее сообщение
        await callback.message.delete()
        
        # Пытаемся отправить фото с обложкой
        await callback.message.answer_photo(
            photo=book.cover_url,
            caption=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        # Если не удалось загрузить изображение, отправляем текстовое сообщение
        import logging
        logging.error(f"Не удалось отправить обложку книги {book.id}: {e}")
        
        # Вместо фото отправляем текстовое сообщение с теми же деталями
        await callback.message.edit_text(
            text=f"📘 *{book.title.upper()}*\n\n"
                 f"*Автор:* {book.author}\n\n"
                 f"{book.description}\n\n"
                 f"📖 *Страниц:* {len(book.page_images)}\n"
                 f"🏷️ *Категория:* {category_name}\n\n"
                 f"⚠️ *Примечание:* Обложка временно недоступна",
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
        await callback.answer("⚠️ Обложка временно недоступна")
        return
    
    await callback.answer()


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.READ))
async def start_reading(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Начинает чтение книги (первая страница)
    """
    if not callback_data.book_id:
        await callback.answer("Ошибка: ID книги не указан")
        return
    
    book = get_book_by_id(callback_data.book_id)
    if not book:
        await callback.answer("Ошибка: книга не найдена")
        return
    
    page_index = callback_data.page or 0
    total_pages = len(book.page_images)
    
    if page_index < 0 or page_index >= total_pages:
        await callback.answer("Ошибка: неверный номер страницы")
        return
    
    page_url = book.page_images[page_index]
    
    text = f"📖 *{book.title}*\nСтраница {page_index + 1} из {total_pages}"
    
    keyboard = get_reading_keyboard(book.id, page_index, total_pages)
    
    # Отправляем первую страницу с обработкой ошибок
    try:
        # Удаляем предыдущее сообщение
        await callback.message.delete()
        
        # Пытаемся отправить фото со страницей
        await callback.message.answer_photo(
            photo=page_url,
            caption=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        # Если не удалось загрузить изображение, отправляем текстовое сообщение
        import logging
        logging.error(f"Не удалось отправить страницу книги {book.id}: {e}")
        
        # Вместо фото отправляем текстовое сообщение
        await callback.message.edit_text(
            text=f"📖 *{book.title}*\n"
                 f"Страница {page_index + 1} из {total_pages}\n\n"
                 f"⚠️ *Примечание:* Изображение страницы временно недоступно\n"
                 f"Используйте кнопки навигации для перехода к другим страницам.",
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
        await callback.answer("⚠️ Изображение страницы временно недоступно")
        return
    
    await callback.answer()


@books_router.callback_query(PaginationCallback.filter(F.action == PaginationAction.PREV))
async def prev_page(callback: CallbackQuery, callback_data: PaginationCallback):
    """
    Переход на предыдущую страницу
    """
    book = get_book_by_id(callback_data.book_id)
    if not book:
        await callback.answer("Ошибка: книга не найдена")
        return
    
    page_index = callback_data.page
    total_pages = len(book.page_images)
    
    if page_index < 0:
        await callback.answer("Это первая страница")
        return
    
    page_url = book.page_images[page_index]
    
    text = f"📖 *{book.title}*\nСтраница {page_index + 1} из {total_pages}"
    
    keyboard = get_reading_keyboard(book.id, page_index, total_pages)
    
    # Обновляем изображение через edit_media с обработкой ошибок
    media = InputMediaPhoto(media=page_url, caption=text, parse_mode="Markdown")
    try:
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard.as_markup()
        )
    except TelegramBadRequest as e:
        # Если не удалось загрузить изображение
        await callback.answer("❌ Не удалось загрузить изображение страницы. Проверьте данные книги.", show_alert=True)
        return
    
    await callback.answer()


@books_router.callback_query(PaginationCallback.filter(F.action == PaginationAction.NEXT))
async def next_page(callback: CallbackQuery, callback_data: PaginationCallback):
    """
    Переход на следующую страницу
    """
    book = get_book_by_id(callback_data.book_id)
    if not book:
        await callback.answer("Ошибка: книга не найдена")
        return
    
    page_index = callback_data.page
    total_pages = len(book.page_images)
    
    if page_index >= total_pages:
        await callback.answer("Это последняя страница")
        return
    
    page_url = book.page_images[page_index]
    
    text = f"📖 *{book.title}*\nСтраница {page_index + 1} из {total_pages}"
    
    keyboard = get_reading_keyboard(book.id, page_index, total_pages)
    
    # Обновляем изображение через edit_media с обработкой ошибок
    media = InputMediaPhoto(media=page_url, caption=text, parse_mode="Markdown")
    try:
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard.as_markup()
        )
    except TelegramBadRequest as e:
        # Если не удалось загрузить изображение
        await callback.answer("❌ Не удалось загрузить изображение страницы. Проверьте данные книги.", show_alert=True)
        return
    
    await callback.answer()


@books_router.callback_query(PaginationCallback.filter(F.action == PaginationAction.CLOSE))
async def close_reading(callback: CallbackQuery, callback_data: PaginationCallback):
    """
    Закрывает режим чтения и возвращает к деталям книги
    """
    book = get_book_by_id(callback_data.book_id)
    if not book:
        await callback.answer("Ошибка: книга не найдена")
        return
    
    # Возвращаемся к деталям книги
    category_name = get_category_name(book.category)
    
    text = (
        f"📘 *{book.title.upper()}*\n\n"
        f"*Автор:* {book.author}\n\n"
        f"{book.description}\n\n"
        f"📖 *Страниц:* {len(book.page_images)}\n"
        f"🏷️ *Категория:* {category_name}"
    )
    
    keyboard = get_book_details_keyboard(book.id)
    
    # Удаляем сообщение с чтением и отправляем детали
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=book.cover_url,
        caption=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.FAVORITE))
async def toggle_favorite(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Заглушка для добавления в избранное
    В MVP просто показывает уведомление
    """
    if callback_data.book_id:
        book = get_book_by_id(callback_data.book_id)
        if book:
            await callback.answer(f"Книга '{book.title}' добавлена в избранное (демо)")
        else:
            await callback.answer("Добавлено в избранное (демо)")
    else:
        await callback.answer("Функция 'Избранные' в разработке (демо)")
    
    # Не меняем сообщение, только показываем уведомление


@books_router.callback_query(BooksCallback.filter(F.action == BooksAction.BACK))
async def go_back(callback: CallbackQuery, callback_data: BooksCallback):
    """
    Обработчик кнопки "Назад"
    В зависимости от контекста возвращает на предыдущий экран
    """
    # В MVP просто возвращаем в главное меню книг
    text = (
        "📚 *КНИГИ*\n\n"
        "Добро пожаловать в раздел исламской литературы! Здесь вы найдете книги по:\n\n"
        "• *Акыда* (Вероубеждение)\n"
        "• *Фикх* (Исламское право)\n"
        "• *Тасаввуф* (Духовность)\n"
        "• *История*\n"
        "• *Биографии*\n\n"
        "Выберите категорию:"
    )
    
    keyboard = get_categories_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@books_router.callback_query(KnowledgeCallback.filter(
    (F.action == "section") & (F.section == "books")
))
async def handle_books_section(callback: CallbackQuery, callback_data: KnowledgeCallback):
    """
    Обработчик для кнопки "Книги" в меню знаний
    Показывает главное меню книг
    """
    text = (
        "📚 *КНИГИ*\n\n"
        "Добро пожаловать в раздел исламской литературы! Здесь вы найдете книги по:\n\n"
        "• *Акыда* (Вероубеждение)\n"
        "• *Фикх* (Исламское право)\n"
        "• *Тасаввуф* (Духовность)\n"
        "• *История*\n"
        "• *Биографии*\n\n"
        "Выберите категорию:"
    )
    
    keyboard = get_categories_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()
