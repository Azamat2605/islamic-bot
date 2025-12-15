from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.enums import ParseMode
from aiogram.utils.i18n import lazy_gettext as __

from bot.states.ai_assistant import AIAssistantState
from bot.keyboards.inline.ai_assistant import get_ai_menu_kb, get_ai_chat_actions_kb
from bot.keyboards.reply.ai_assistant import get_ai_quick_questions_kb
from bot.services.ai_service import AIService

router = Router(name="ai_assistant")

# Инициализация сервиса
ai_service = AIService()

# Баннер и заглушки изображений (безопасные placeholder URLs)
BANNER_IMAGE_URL = "https://images.unsplash.com/photo-1516387938699-a93567ec168e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
TEASER_IMAGE_URL = "https://images.unsplash.com/photo-1541961017774-22349e4a1262?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"


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
    await state.set_state(AIAssistantState.waiting_for_question)
    
    await callback.message.edit_caption(
        caption="💬 *Режим общения*\n\nВведите ваш вопрос, и я постараюсь дать развернутый ответ на основе исламских знаний.",
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
async def image_generation_stub(callback: CallbackQuery):
    """
    Заглушка для функции генерации изображений.
    """
    caption = (
        "🎨 *Генерация исламского искусства*\n\n"
        "Эта функция находится в разработке. "
        "Мы готовим кисти и палитры для создания красивых исламских узоров и каллиграфии. "
        "Скоро вы сможете генерировать уникальные изображения на основе исламских мотивов!\n\n"
        "🖌️ *Скоро будет доступно...*"
    )
    
    await callback.message.answer_photo(
        photo=TEASER_IMAGE_URL,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
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
