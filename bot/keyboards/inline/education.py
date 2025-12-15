"""
Inline keyboards for the Education module.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _


class EducationCallback(CallbackData, prefix="edu"):
    """Callback data factory for Education module."""
    action: str
    course_id: int | None = None
    test_id: int | None = None
    module_id: int | None = None
    question_id: int | None = None
    option_id: int | None = None


# ==================== NEW NAVIGATION KEYBOARDS ====================

def get_education_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Main Education Menu keyboard with 8 buttons (2 per row, except last two).
    
    Structure:
    - Row 1: [📚 Каталог курсов] [▶️ Активные курсы]
    - Row 2: [📝 Тесты] [📈 Прогресс]
    - Row 3: [🏆 Завершенные] [📡 Эфиры]
    - Row 4: [🤖 AI Помощник]
    - Row 5: [🏠 В главное меню]
    """
    builder = InlineKeyboardBuilder()
    
    # Row 1: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("📚 Каталог курсов"),
            callback_data=EducationCallback(action="catalog").pack()
        ),
        InlineKeyboardButton(
            text=_("▶️ Активные курсы"),
            callback_data=EducationCallback(action="active").pack()
        )
    )
    
    # Row 2: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Тесты"),
            callback_data=EducationCallback(action="tests").pack()
        ),
        InlineKeyboardButton(
            text=_("📈 Прогресс"),
            callback_data=EducationCallback(action="progress").pack()
        )
    )
    
    # Row 3: 2 buttons
    builder.row(
        InlineKeyboardButton(
            text=_("🏆 Завершенные"),
            callback_data=EducationCallback(action="completed").pack()
        ),
        InlineKeyboardButton(
            text=_("📡 Эфиры"),
            callback_data=EducationCallback(action="streams").pack()
        )
    )
    
    # Row 4: 1 button (AI Assistant)
    builder.row(
        InlineKeyboardButton(
            text=_("🤖 AI Помощник"),
            callback_data=EducationCallback(action="assistant").pack()
        )
    )
    
    # Row 5: 1 button (Main Menu)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 В главное меню"),
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_education_sub_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generic sub-menu keyboard with standardized navigation buttons.
    
    Structure:
    - Row 1: [⬅️ Назад] [🏠 В главное меню]
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ Назад"),
            callback_data=EducationCallback(action="menu_back").pack()
        ),
        InlineKeyboardButton(
            text=_("🏠 В главное меню"),
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_education_main_keyboard() -> InlineKeyboardMarkup:
    """Main menu of the Education section."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("📚 КАТАЛОГ КУРСОВ"),
            callback_data=EducationCallback(action="catalog").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔄 Активные курсы"),
            callback_data=EducationCallback(action="active").pack()
        ),
        InlineKeyboardButton(
            text=_("✅ Завершенные курсы"),
            callback_data=EducationCallback(action="completed").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Тесты"),
            callback_data=EducationCallback(action="tests").pack()
        ),
        InlineKeyboardButton(
            text=_("🎙️ Эфиры"),
            callback_data=EducationCallback(action="streams").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Прогресс"),
            callback_data=EducationCallback(action="progress").pack()
        ),
        InlineKeyboardButton(
            text=_("🔍 Помощник"),
            callback_data=EducationCallback(action="assistant").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 В главное меню"),
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_dashboard_keyboard() -> InlineKeyboardMarkup:
    """Dashboard keyboard (Screen 1)."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("▶ Продолжить"),
            callback_data=EducationCallback(action="continue").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📚 Каталог"),
            callback_data=EducationCallback(action="catalog").pack()
        ),
        InlineKeyboardButton(
            text=_("✅ Завершенные"),
            callback_data=EducationCallback(action="completed").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Тесты"),
            callback_data=EducationCallback(action="tests").pack()
        ),
        InlineKeyboardButton(
            text=_("🎙️ Эфиры"),
            callback_data=EducationCallback(action="streams").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔍 Помощник"),
            callback_data=EducationCallback(action="assistant").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_catalog_keyboard(categories: list[str] = None) -> InlineKeyboardMarkup:
    """Catalog keyboard (Screen 2)."""
    builder = InlineKeyboardBuilder()
    
    # Default categories if none provided
    if categories is None:
        categories = ["Акыда", "Фикх", "Коран", "История", "Арабский"]
    
    for category in categories:
        builder.row(
            InlineKeyboardButton(
                text=f"📖 {category}",
                callback_data=EducationCallback(action="category", course_id=0).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔍 Поиск курсов"),
            callback_data=EducationCallback(action="search").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_course_detail_keyboard(course_id: int, has_progress: bool = False) -> InlineKeyboardMarkup:
    """Course detail keyboard."""
    builder = InlineKeyboardBuilder()
    
    if has_progress:
        builder.row(
            InlineKeyboardButton(
                text=_("▶ Продолжить"),
                callback_data=EducationCallback(action="continue_course", course_id=course_id).pack()
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("🚀 Начать курс"),
                callback_data=EducationCallback(action="start_course", course_id=course_id).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📋 Уроки"),
            callback_data=EducationCallback(action="course_modules", course_id=course_id).pack()
        ),
        InlineKeyboardButton(
            text=_("⭐ Рейтинг"),
            callback_data=EducationCallback(action="course_rating", course_id=course_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 К каталогу"),
            callback_data=EducationCallback(action="catalog").pack()
        )
    )
    
    return builder.as_markup()


def get_lesson_keyboard(module_id: int, has_video: bool = True, has_audio: bool = True) -> InlineKeyboardMarkup:
    """Lesson view keyboard (Screen 3)."""
    builder = InlineKeyboardBuilder()
    
    if has_video:
        builder.row(
            InlineKeyboardButton(
                text=_("▶ Смотреть видео"),
                callback_data=EducationCallback(action="watch_video", module_id=module_id).pack()
            )
        )
    
    if has_audio:
        builder.row(
            InlineKeyboardButton(
                text=_("🎧 Слушать аудио"),
                callback_data=EducationCallback(action="listen_audio", module_id=module_id).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Читать подробно"),
            callback_data=EducationCallback(action="read_telegraph", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("✅ Я изучил / Далее"),
            callback_data=EducationCallback(action="complete_lesson", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 К курсу"),
            callback_data=EducationCallback(action="course_modules", course_id=0).pack()
        )
    )
    
    return builder.as_markup()


def get_course_modules_keyboard(course_id: int, modules_status: list[tuple[int, str, str]] = None) -> InlineKeyboardMarkup:
    """Course modules list keyboard with status indicators."""
    builder = InlineKeyboardBuilder()
    
    # Default mock data if none provided
    if modules_status is None:
        modules_status = [
            (1, "✅ Модуль 1. Введение", "completed"),
            (2, "✅ Модуль 2. Основы", "completed"),
            (3, "🔄 Модуль 3. Практика", "current"),
            (4, "⏳ Модуль 4. Углубление", "locked"),
            (5, "⏳ Модуль 5. Заключение", "locked"),
        ]
    
    for module_id, title, status in modules_status:
        if status == "locked":
            callback_data = EducationCallback(action="module_locked", module_id=module_id).pack()
        else:
            callback_data = EducationCallback(action="view_module", module_id=module_id).pack()
        
        builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=callback_data
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 К курсу"),
            callback_data=EducationCallback(action="course_detail", course_id=course_id).pack()
        )
    )
    
    return builder.as_markup()


def get_active_courses_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for active courses (mock data)."""
    builder = InlineKeyboardBuilder()
    
    # Mock courses
    builder.row(
        InlineKeyboardButton(
            text=_("Основы ислама (65%)"),
            callback_data=EducationCallback(action="course", course_id=1).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Намаз для начинающих (40%)"),
            callback_data=EducationCallback(action="course", course_id=2).pack()
        )
    )
    
    # Action buttons
    builder.row(
        InlineKeyboardButton(
            text=_("▶ Продолжить"),
            callback_data=EducationCallback(action="continue").pack()
        ),
        InlineKeyboardButton(
            text=_("📊 Прогресс"),
            callback_data=EducationCallback(action="detailed_progress").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_completed_courses_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for completed courses (mock data)."""
    builder = InlineKeyboardBuilder()
    
    # Mock completed courses with medals
    builder.row(
        InlineKeyboardButton(
            text=_("🥇 Введение в ислам"),
            callback_data=EducationCallback(action="review", course_id=1).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🥈 Фикх очищения"),
            callback_data=EducationCallback(action="review", course_id=2).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🥉 История пророков"),
            callback_data=EducationCallback(action="review", course_id=3).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔄 Повторить материал"),
            callback_data=EducationCallback(action="review_all").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_tests_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for tests section (mock data)."""
    builder = InlineKeyboardBuilder()
    
    # Mock test results
    builder.row(
        InlineKeyboardButton(
            text=_("Основы веры (85%)"),
            callback_data=EducationCallback(action="test_result", test_id=1).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Намаз (70%)"),
            callback_data=EducationCallback(action="test_result", test_id=2).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Пост (90%)"),
            callback_data=EducationCallback(action="test_result", test_id=3).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Пройти новый тест"),
            callback_data="start_selection"
        ),
        InlineKeyboardButton(
            text=_("📊 Мои результаты"),
            callback_data=EducationCallback(action="my_results").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_progress_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for progress section."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("📈 Детальная статистика"),
            callback_data=EducationCallback(action="detailed_stats").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📅 За месяц"),
            callback_data=EducationCallback(action="month_stats").pack()
        ),
        InlineKeyboardButton(
            text=_("📅 За год"),
            callback_data=EducationCallback(action="year_stats").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🏆 Достижения"),
            callback_data=EducationCallback(action="achievements").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_stub_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for stub sections (catalog, streams, assistant)."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_test_question_keyboard(question_number: int, total_questions: int) -> InlineKeyboardMarkup:
    """Keyboard for test questions (mock)."""
    builder = InlineKeyboardBuilder()
    
    # Mock answer options
    builder.row(
        InlineKeyboardButton(
            text=_("Вариант 1"),
            callback_data=EducationCallback(action="answer", question_id=1, option_id=1).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Вариант 2"),
            callback_data=EducationCallback(action="answer", question_id=1, option_id=2).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Вариант 3"),
            callback_data=EducationCallback(action="answer", question_id=1, option_id=3).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Вариант 4"),
            callback_data=EducationCallback(action="answer", question_id=1, option_id=4).pack()
        )
    )
    
    # Navigation
    if question_number > 1:
        builder.row(
            InlineKeyboardButton(
                text=_("⬅️ Назад"),
                callback_data=EducationCallback(action="prev_question", question_id=question_number-1).pack()
            )
        )
    
    if question_number < total_questions:
        builder.row(
            InlineKeyboardButton(
                text=_("Далее ➡️"),
                callback_data=EducationCallback(action="next_question", question_id=question_number+1).pack()
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("✅ Завершить тест"),
                callback_data=EducationCallback(action="finish_test").pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("❌ Отменить тест"),
            callback_data=EducationCallback(action="cancel_test").pack()
        )
    )
    
    return builder.as_markup()


# ==================== NEW KEYBOARDS FOR QUIZ & PROGRESS ====================

def get_quiz_question_keyboard(
    question_id: int,
    options: list[dict],
    question_type: str = "single_choice"
) -> InlineKeyboardMarkup:
    """Keyboard for quiz questions."""
    builder = InlineKeyboardBuilder()
    
    for option in options:
        builder.row(
            InlineKeyboardButton(
                text=option["option_text"],
                callback_data=EducationCallback(
                    action="quiz_answer",
                    question_id=question_id,
                    option_id=option["id"]
                ).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("❌ Отменить тест"),
            callback_data=EducationCallback(action="cancel_quiz").pack()
        )
    )
    
    return builder.as_markup()


def get_quiz_result_keyboard(is_correct: bool) -> InlineKeyboardMarkup:
    """Keyboard for quiz result explanation."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("➡️ Далее"),
            callback_data=EducationCallback(action="quiz_next").pack()
        )
    )
    
    if not is_correct:
        builder.row(
            InlineKeyboardButton(
                text=_("🔄 Попробовать еще раз"),
                callback_data=EducationCallback(action="retry_question").pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=_("❌ Отменить тест"),
            callback_data=EducationCallback(action="cancel_quiz").pack()
        )
    )
    
    return builder.as_markup()


def get_streams_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for streams section."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("📡 Ближайшие эфиры"),
            callback_data=EducationCallback(action="upcoming_streams").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📼 Архив эфиров"),
            callback_data=EducationCallback(action="stream_archive").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔔 Настроить уведомления"),
            callback_data=EducationCallback(action="stream_notifications").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_ai_assistant_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for AI assistant section."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("❓ Примеры вопросов"),
            callback_data=EducationCallback(action="example_questions").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📚 База знаний"),
            callback_data=EducationCallback(action="knowledge_base").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data=EducationCallback(action="main").pack()
        )
    )
    
    return builder.as_markup()


def get_lesson_keyboard_with_mark_studied(module_id: int) -> InlineKeyboardMarkup:
    """Lesson keyboard with 'Mark as Studied' button."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=_("▶ Смотреть видео"),
            callback_data=EducationCallback(action="watch_video", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🎧 Слушать аудио"),
            callback_data=EducationCallback(action="listen_audio", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("📝 Читать подробно"),
            callback_data=EducationCallback(action="read_telegraph", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("✅ Я изучил / Далее"),
            callback_data=EducationCallback(action="mark_studied", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("🔙 К курсу"),
            callback_data=EducationCallback(action="course_modules", course_id=0).pack()
        )
    )
    
    return builder.as_markup()
