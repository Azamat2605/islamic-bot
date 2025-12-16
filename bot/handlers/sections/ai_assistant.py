from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile, InputMediaPhoto, InlineKeyboardMarkup
from aiogram.enums import ParseMode, ContentType
from aiogram.utils.i18n import lazy_gettext as __
from typing import Union, Optional

from bot.states.ai_assistant import AIAssistantState
from bot.keyboards.inline.ai_assistant import get_ai_menu_kb, get_ai_chat_actions_kb, get_ai_image_mode_kb
from bot.keyboards.reply.ai_assistant import get_ai_quick_questions_kb
from bot.services.ai_service import AIService

router = Router(name="ai_assistant")

# Инициализация сервиса
ai_service = AIService()

# Баннер и заглушки изображений (безопасные placeholder URLs)
BANNER_IMAGE_URL = "https://images.unsplash.com/photo-1516387938699-a93567ec168e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
TEASER_IMAGE_URL = "https://images.unsplash.com/photo-1541961017774-22349e4a1262?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"


async def safe_edit_message(
    message: Union[Message, CallbackQuery],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None,
    photo_url: Optional[str] = None
) -> Union[Message, bool]:
    """
    Безопасное редактирование сообщения с учетом его типа.
    
    Args:
        message: Сообщение или callback для редактирования
        text: Текст или caption
        reply_markup: Клавиатура
        parse_mode: Режим парсинга (Markdown/HTML)
        photo_url: URL фото (если нужно отправить фото)
    
    Returns:
        Отредактированное сообщение или False в случае ошибки
    """
    if isinstance(message, CallbackQuery):
        message = message.message
    
    try:
        # Если нужно отправить фото
        if photo_url:
            # Если текущее сообщение - фото, редактируем медиа
            if message.content_type == ContentType.PHOTO:
                media = InputMediaPhoto(media=photo_url, caption=text, parse_mode=parse_mode)
                return await message.edit_media(media=media, reply_markup=reply_markup)
            # Иначе удаляем старое и отправляем новое
            else:
                await message.delete()
                return await message.answer_photo(
                    photo=photo_url,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        
        # Редактирование текста/подписи
        if message.content_type == ContentType.TEXT:
            return await message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        elif message.content_type == ContentType.PHOTO:
            return await message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            # Для других типов удаляем и отправляем новое текстовое сообщение
            await message.delete()
            return await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    except Exception as e:
        # В случае ошибки удаляем старое и отправляем новое
        try:
            await message.delete()
        except:
            pass
        if photo_url:
            return await message.answer_photo(
                photo=photo_url,
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            return await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )


@router.callback_query(F.data == "islamic_assistant")
async def on_ai_assistant_entry(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик входа в раздел ИИ-помощника из главного меню.
    """
    await state.clear()
    await state.set_state(AIAssistantState.main_menu)
    # Не устанавливаем состояние waiting_for_question, пока пользователь не выберет "ОБЩЕНИЕ"
    text = (
        "🤖 *Исламский ИИ-Помощник*\n\n"
        "«Аллах — с терпеливыми» (Коран 2:153)\n\n"
        "Добро пожаловать в интеллектуальный помощник по исламским знаниям! "
        "Задавайте вопросы о Коране, Сунне, фикхе, истории ислама и духовности. "
        "Я постараюсь ответить на основе авторитетных источников."
    )
    await callback.message.edit_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_menu_kb()
    )
    await callback.answer()


@router.message(F.text == __("🤖 Исламский помощник"))
async def ai_assistant_entry(message: Message):
    """
    Точка входа в модуль ИИ-помощника.
    Отправляет баннер с описанием и меню действий.
    """
    caption = (
        "🤖 *Исламский ИИ-Помощник*\n\n"
        "«Аллах — с терпеливыми» (Коран 2:153)\n\n"
        "Добро пожаловать в интеллектуальный помощник по исламским знаниям! "
        "Задавайте вопросы о Коране, Сунне, фикхе, истории ислама и духовности. "
        "Я постараюсь ответить на основе авторитетных источников."
    )
    
    await message.answer_photo(
        photo=BANNER_IMAGE_URL,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_menu_kb()
    )


@router.callback_query(F.data == "ai_chat_mode")
async def start_chat_mode(callback: CallbackQuery, state: FSMContext):
    """
    Начало режима чата с ИИ.
    Устанавливает состояние ожидания вопроса и показывает быстрые вопросы.
    """
    await state.set_state(AIAssistantState.chat_mode)
    # Для обратной совместимости также устанавливаем waiting_for_question
    await state.set_state(AIAssistantState.waiting_for_question)
    
    # Безопасное редактирование сообщения
    await safe_edit_message(
        message=callback,
        text="💬 *Режим общения*\n\nВведите ваш вопрос, и я постараюсь дать развернутый ответ на основе исламских знаний.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await callback.message.answer(
        "✍️ *Введите ваш вопрос...*\n\n"
        "Или выберите один из быстрых вопросов ниже:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_quick_questions_kb()
    )
    await callback.answer()


@router.message(AIAssistantState.waiting_for_question, F.text == "🔙 Выход")
async def exit_chat_mode(message: Message, state: FSMContext):
    """Выход из режима чата."""
    await state.clear()
    await message.answer(
        "✅ Режим общения завершен.",
        reply_markup=None  # Убираем reply-клавиатуру
    )
    # Возвращаем к главному меню
    await ai_assistant_entry(message)


@router.message(AIAssistantState.waiting_for_question, F.text)
async def process_user_question(message: Message, state: FSMContext):
    """
    Обработка вопроса пользователя в состоянии ожидания.
    """
    user_question = message.text.strip()
    
    # Отправляем индикатор "печатает"
    thinking_msg = await message.answer("⏳ *Думаю...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Получаем ответ от ИИ
        ai_response = await ai_service.get_answer(user_question)
        
        # Отправляем ответ с форматированием Markdown
        await thinking_msg.edit_text(
            f"🤖 *Ответ:*\n\n{ai_response}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_ai_chat_actions_kb()
        )
        
    except Exception as e:
        await thinking_msg.edit_text(
            "❌ *Произошла ошибка при обработке запроса.*\n\n"
            "Пожалуйста, попробуйте позже или задайте другой вопрос.",
            parse_mode=ParseMode.MARKDOWN
        )


@router.callback_query(F.data == "ai_new_question")
async def new_question_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Спросить другое".
    Сохраняет состояние и предлагает ввести новый вопрос.
    """
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await callback.message.answer(
        "🔄 *Жду следующий вопрос...*\n\n"
        "Введите ваш вопрос или выберите быстрый вопрос:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_quick_questions_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "ai_image_mode")
async def image_generation_stub(callback: CallbackQuery, state: FSMContext):
    """
    Заглушка для функции генерации изображений.
    """
    await state.set_state(AIAssistantState.image_mode)
    
    caption = (
        "🎨 *Генерация исламского искусства*\n\n"
        "Эта функция находится в разработке. "
        "Мы готовим кисти и палитры для создания красивых исламских узоров и каллиграфии. "
        "Скоро вы сможете генерировать уникальные изображения на основе исламских мотивов!\n\n"
        "🖌️ *Скоро будет доступно...*"
    )
    
    # Безопасное редактирование сообщения с фото и клавиатурой "Назад"
    await safe_edit_message(
        message=callback,
        text=caption,
        photo_url=TEASER_IMAGE_URL,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_image_mode_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "ai_assistant_back")
async def ai_assistant_back_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Назад" в режиме генерации изображений.
    Возвращает в главное меню ИИ-помощника.
    """
    await state.clear()
    text = (
        "🤖 *Исламский ИИ-Помощник*\n\n"
        "«Аллах — с терпеливыми» (Коран 2:153)\n\n"
        "Добро пожаловать в интеллектуальный помощник по исламским знаниям! "
        "Задавайте вопросы о Коране, Сунне, фикхе, истории ислама и духовности. "
        "Я постараюсь ответить на основе авторитетных источников."
    )
    # Используем safe_edit_message для безопасного возврата
    await safe_edit_message(
        message=callback,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_ai_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "ai_share_stub")
async def share_stub_handler(callback: CallbackQuery):
    """
    Заглушка для функции "Поделиться".
    """
    await callback.answer(
        "Функция 'Поделиться' в разработке. Скоро вы сможете делиться ответами с друзьями!",
        show_alert=False
    )
