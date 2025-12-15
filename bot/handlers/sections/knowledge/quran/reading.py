"""
Обработчики чтения сур.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.data.mock_knowledge import get_surah_by_id
from bot.keyboards.inline.knowledge.quran_kb import (
    get_surah_reading_kb,
    get_translator_settings_kb,
    get_favorite_toggle_kb,
)

logger = logging.getLogger(__name__)

router = Router(name="quran_reading")

# In-memory хранилище для сессий пользователей (для MVP)
user_sessions = {}


def get_user_session(user_id: int) -> dict:
    """Получить сессию пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "current_translator": "kuliev",
            "favorites": set(),  # ID избранных сур
        }
    return user_sessions[user_id]


def toggle_favorite(user_id: int, surah_id: int) -> bool:
    """Переключить избранное"""
    session = get_user_session(user_id)
    if surah_id in session["favorites"]:
        session["favorites"].remove(surah_id)
        return False
    else:
        session["favorites"].add(surah_id)
        return True


def is_favorite(user_id: int, surah_id: int) -> bool:
    """Проверить, в избранном ли сура"""
    session = get_user_session(user_id)
    return surah_id in session["favorites"]


@router.callback_query(F.data.startswith("quran:read:"))
async def quran_read_handler(callback: CallbackQuery):
    """
    Обработчик чтения суры.
    Формат callback_data: quran:read:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1

        # Получаем данные суры
        surah = get_surah_by_id(surah_id)
        if not surah:
            await callback.answer("Сура не найдена", show_alert=True)
            return

        # Получаем сохраненные настройки пользователя
        user_id = callback.from_user.id
        session = get_user_session(user_id)
        is_fav = is_favorite(user_id, surah_id)
        current_translator = session["current_translator"]

        # Формируем текст суры
        translation = surah["translations"].get(current_translator, "")
        message_text = (
            f"**{surah['name_transliteration']} ({surah['name_translation']})**\n"
            f"_{surah['name_arabic']}_\n\n"
            f"**Арабский текст:**\n"
            f"`{surah['arabic_text'][:200]}...`\n\n"
            f"**Перевод ({current_translator}):**\n"
            f"{translation[:300]}..."
        )

        # Получаем клавиатуру чтения
        keyboard = get_surah_reading_kb(
            surah_id=surah_id,
            is_favorite=is_fav,
            current_translator=current_translator
        )

        # Отправляем сообщение
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in quran_read_handler: {e}")
        await callback.answer("Ошибка загрузки суры", show_alert=True)


@router.callback_query(F.data.startswith("quran:listen:"))
async def quran_listen_handler(callback: CallbackQuery):
    """
    Обработчик аудио (заглушка).
    Формат callback_data: quran:listen:{surah_id}
    """
    await callback.answer("🎧 Аудио функция в разработке", show_alert=False)


@router.callback_query(F.data.startswith("quran:favorite:"))
async def quran_favorite_handler(callback: CallbackQuery):
    """
    Обработчик избранного (toggle).
    Формат callback_data: quran:favorite:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1

        # Переключаем избранное
        user_id = callback.from_user.id
        new_favorite_state = toggle_favorite(user_id, surah_id)

        # Получаем обновленную клавиатуру
        session = get_user_session(user_id)
        keyboard = get_favorite_toggle_kb(
            surah_id=surah_id,
            is_favorite=new_favorite_state
        )

        # Обновляем сообщение
        await callback.message.edit_reply_markup(reply_markup=keyboard)

        # Показываем уведомление
        if new_favorite_state:
            await callback.answer("✅ Добавлено в избранное")
        else:
            await callback.answer("❌ Удалено из избранного")

    except Exception as e:
        logger.error(f"Error in quran_favorite_handler: {e}")
        await callback.answer("Ошибка обновления избранного", show_alert=True)


@router.callback_query(F.data.startswith("quran:settings:"))
async def quran_settings_handler(callback: CallbackQuery):
    """
    Обработчик настроек перевода.
    Формат callback_data: quran:settings:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1

        # Получаем текущего переводчика пользователя
        user_id = callback.from_user.id
        session = get_user_session(user_id)
        current_translator = session["current_translator"]

        # Получаем клавиатуру настроек
        keyboard = get_translator_settings_kb(
            surah_id=surah_id,
            current_translator=current_translator
        )

        # Формируем сообщение
        message_text = (
            f"**Настройки перевода**\n\n"
            f"Выберите переводчика для суры {surah_id}:\n"
            f"_(Изменения применяются сразу)_"
        )

        # Обновляем сообщение
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in quran_settings_handler: {e}")
        await callback.answer("Ошибка открытия настроек", show_alert=True)


@router.callback_query(F.data.startswith("quran:translator:"))
async def quran_translator_handler(callback: CallbackQuery):
    """
    Обработчик выбора переводчика.
    Формат callback_data: quran:translator:{translator_id}
    """
    try:
        # Парсим ID переводчика
        translator_id = callback.data.split(":")[2]

        # Сохраняем выбор пользователя
        user_id = callback.from_user.id
        session = get_user_session(user_id)
        session["current_translator"] = translator_id

        # Получаем ID суры из предыдущего сообщения
        # Для простоты возвращаемся к суре 1
        # В реальной реализации нужно хранить состояние
        surah_id = 1

        # Обновляем сообщение с выбранным переводчиком
        surah = get_surah_by_id(surah_id)
        translation = surah["translations"].get(translator_id, "")

        message_text = (
            f"**{surah['name_transliteration']} ({surah['name_translation']})**\n"
            f"_{surah['name_arabic']}_\n\n"
            f"**Арабский текст:**\n"
            f"`{surah['arabic_text'][:200]}...`\n\n"
            f"**Перевод ({translator_id}):**\n"
            f"{translation[:300]}..."
        )

        # Получаем клавиатуру чтения с обновленным переводчиком
        keyboard = get_surah_reading_kb(
            surah_id=surah_id,
            is_favorite=is_favorite(user_id, surah_id),
            current_translator=translator_id
        )

        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer(f"Переводчик изменен")

    except Exception as e:
        logger.error(f"Error in quran_translator_handler: {e}")
        await callback.answer("Ошибка выбора переводчика", show_alert=True)


@router.callback_query(F.data.startswith("quran:prev:"))
@router.callback_query(F.data.startswith("quran:next:"))
async def quran_navigation_handler(callback: CallbackQuery):
    """
    Обработчик навигации по сурам (предыдущая/следующая).
    Форматы: quran:prev:{surah_id}, quran:next:{surah_id}
    """
    try:
        # Определяем направление и получаем ID суры
        parts = callback.data.split(":")
        direction = parts[1]  # "prev" или "next"
        current_surah_id = int(parts[2]) if parts[2].isdigit() else 1

        # Вычисляем новую суру
        if direction == "prev":
            from bot.data.mock_knowledge import get_prev_surah_id
            new_surah_id = get_prev_surah_id(current_surah_id)
        else:  # "next"
            from bot.data.mock_knowledge import get_next_surah_id
            new_surah_id = get_next_surah_id(current_surah_id)

        # Если сура не найдена (границы достигнуты)
        if not new_surah_id:
            await callback.answer(
                "Это первая/последняя сура" if direction == "prev" else "Это последняя сура",
                show_alert=False
            )
            return

        # Вызываем обработчик чтения суры с новым ID
        callback.data = f"quran:read:{new_surah_id}"
        await quran_read_handler(callback)

    except Exception as e:
        logger.error(f"Error in quran_navigation_handler: {e}")
        await callback.answer("Ошибка навигации", show_alert=True)


@router.callback_query(F.data.startswith("quran:back_to_list:"))
async def quran_back_to_list_handler(callback: CallbackQuery):
    """
    Обработчик возврата к каталогу сур.
    Формат: quran:back_to_list:{page_number}
    """
    try:
        # Парсим номер страницы
        page_str = callback.data.split(":")[2]
        page = int(page_str) if page_str.isdigit() else 0

        # Вызываем обработчик страницы каталога
        callback.data = f"quran:page:{page}"
        from .catalog import quran_page_handler
        await quran_page_handler(callback)

    except Exception as e:
        logger.error(f"Error in quran_back_to_list_handler: {e}")
        await callback.answer("Ошибка возврата к каталогу", show_alert=True)


@router.callback_query(F.data.startswith("quran:back_to_reading:"))
async def quran_back_to_reading_handler(callback: CallbackQuery):
    """
    Обработчик возврата к чтению суры из настроек.
    Формат: quran:back_to_reading:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1

        # Вызываем обработчик чтения суры
        callback.data = f"quran:read:{surah_id}"
        await quran_read_handler(callback)

    except Exception as e:
        logger.error(f"Error in quran_back_to_reading_handler: {e}")
        await callback.answer("Ошибка возврата к чтению", show_alert=True)
