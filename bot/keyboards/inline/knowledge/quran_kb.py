"""
Клавиатуры для модуля Коран.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data.mock_knowledge import (
    get_surahs_page,
    get_total_pages,
    get_surah_by_id,
    get_next_surah_id,
    get_prev_surah_id,
)


def get_surah_catalog_kb(page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура каталога сур (Grid View 2x4)

    Args:
        page: Номер страницы (0-based)

    Returns:
        InlineKeyboardMarkup с кнопками сур и пагинацией
    """
    builder = InlineKeyboardBuilder()

    # Получаем суры для текущей страницы
    surahs = get_surahs_page(page, items_per_page=8)

    # Создаем сетку 2x4 (2 строки по 4 кнопки)
    for surah in surahs:
        # Формат: "1. Аль-Фатиха (7)"
        button_text = f"{surah['id']}. {surah['name_transliteration']} ({surah['verse_count']})"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"quran:read:{surah['id']}"
        ))

    # Устанавливаем сетку 2x4
    builder.adjust(4, 4)

    # Пагинация (если нужно)
    total_pages = get_total_pages(items_per_page=8)
    pagination_buttons = []

    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"quran:page:{page-1}"
        ))

    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️ Вперед",
            callback_data=f"quran:page:{page+1}"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Кнопка назад в меню Знаний
    builder.row(InlineKeyboardButton(
        text="🔙 Назад в Знания",
        callback_data="know:quran_back"
    ))

    return builder.as_markup()


def get_surah_reading_kb(surah_id: int, is_favorite: bool = False,
                         current_translator: str = "kuliev") -> InlineKeyboardMarkup:
    """
    Клавиатура чтения суры

    Args:
        surah_id: ID суры
        is_favorite: Добавлена ли в избранное
        current_translator: Текущий переводчик

    Returns:
        InlineKeyboardMarkup с контролами чтения
    """
    builder = InlineKeyboardBuilder()

    # Первая строка: Аудио и Избранное
    favorite_icon = "❤️" if is_favorite else "🤍"
    builder.row(
        InlineKeyboardButton(
            text="▶️ Слушать",
            callback_data=f"quran:listen:{surah_id}"
        ),
        InlineKeyboardButton(
            text=f"{favorite_icon} Избранное",
            callback_data=f"quran:favorite:{surah_id}"
        )
    )

    # Вторая строка: Настройки
    builder.row(
        InlineKeyboardButton(
            text="⚙️ Настройки",
            callback_data=f"quran:settings:{surah_id}"
        )
    )

    # Третья строка: Навигация по сурам
    nav_buttons = []

    prev_id = get_prev_surah_id(surah_id)
    if prev_id:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data=f"quran:prev:{prev_id}"
        ))

    nav_buttons.append(InlineKeyboardButton(
        text="📋 К каталогу",
        callback_data=f"quran:back_to_list:0"
    ))

    next_id = get_next_surah_id(surah_id)
    if next_id:
        nav_buttons.append(InlineKeyboardButton(
            text="Следующая ➡️",
            callback_data=f"quran:next:{next_id}"
        ))

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()


def get_translator_settings_kb(surah_id: int, current_translator: str = "kuliev") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора переводчика

    Args:
        surah_id: ID суры (для возврата)
        current_translator: Текущий выбранный переводчик

    Returns:
        InlineKeyboardMarkup с выбором переводчика
    """
    builder = InlineKeyboardBuilder()

    # Переводчики
    translators = [
        ("kuliev", "Эльмир Кулиев"),
        ("osmanov", "Магомед-Нури Османов")
    ]

    for translator_id, translator_name in translators:
        prefix = "✅" if translator_id == current_translator else "⚪"
        builder.row(InlineKeyboardButton(
            text=f"{prefix} {translator_name}",
            callback_data=f"quran:translator:{translator_id}"
        ))

    # Кнопка назад к чтению
    builder.row(InlineKeyboardButton(
        text="🔙 Назад к чтению",
        callback_data=f"quran:back_to_reading:{surah_id}"
    ))

    return builder.as_markup()


def get_favorite_toggle_kb(surah_id: int, is_favorite: bool) -> InlineKeyboardMarkup:
    """
    Клавиатура для переключения избранного (обновленная версия)

    Args:
        surah_id: ID суры
        is_favorite: Текущее состояние избранного

    Returns:
        InlineKeyboardMarkup с обновленной кнопкой избранного
    """
    builder = InlineKeyboardBuilder()

    favorite_icon = "❤️" if is_favorite else "🤍"
    builder.row(
        InlineKeyboardButton(
            text="▶️ Слушать",
            callback_data=f"quran:listen:{surah_id}"
        ),
        InlineKeyboardButton(
            text=f"{favorite_icon} Избранное",
            callback_data=f"quran:favorite:{surah_id}"
        )
    )

    # Вторая строка: Настройки
    builder.row(
        InlineKeyboardButton(
            text="⚙️ Настройки",
            callback_data=f"quran:settings:{surah_id}"
        )
    )

    # Третья строка: Навигация по сурам
    nav_buttons = []

    prev_id = get_prev_surah_id(surah_id)
    if prev_id:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data=f"quran:prev:{prev_id}"
        ))

    nav_buttons.append(InlineKeyboardButton(
        text="📋 К каталогу",
        callback_data=f"quran:back_to_list:0"
    ))

    next_id = get_next_surah_id(surah_id)
    if next_id:
        nav_buttons.append(InlineKeyboardButton(
            text="Следующая ➡️",
            callback_data=f"quran:next:{next_id}"
        ))

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()
