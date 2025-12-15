"""
Education module handlers.
"""
import logging
from contextlib import suppress
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.education import (
    EducationCallback,
    get_education_menu_keyboard,
    get_education_sub_menu_keyboard,
    get_education_main_keyboard,
    get_dashboard_keyboard,
    get_catalog_keyboard,
    get_course_detail_keyboard,
    get_course_modules_keyboard,
    get_lesson_keyboard,
    get_active_courses_keyboard,
    get_completed_courses_keyboard,
    get_tests_keyboard,
    get_progress_keyboard,
    get_stub_keyboard,
    get_test_question_keyboard,
    get_quiz_question_keyboard,
    get_quiz_result_keyboard,
    get_streams_keyboard,
    get_ai_assistant_keyboard,
)
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from bot.services.education_service import EducationService
from bot.states.education import (
    CourseLearningState,
    QuizState,
    AIAssistantState,
    StreamState,
    CourseLearningData,
    QuizData
)

router = Router(name="education")
logger = logging.getLogger(__name__)


@router.message(F.text == __("Обучение"))
async def education_entry(message: types.Message) -> None:
    """Entry point for Education section (Reply Button)."""
    # Hide the Reply Keyboard when entering inline-based Education section
    from aiogram.types import ReplyKeyboardRemove
    
    text = _(
        "📚 ОБУЧЕНИЕ\n\n"
        "Добро пожаловать в раздел обучения! Здесь вы найдете:\n"
        "• Курсы по основам ислама\n"
        "• Интерактивные тесты\n"
        "• Отслеживание прогресса\n"
        "• AI-помощник для вопросов\n\n"
        "Выберите раздел:"
    )
    
    # Send message with ReplyKeyboardRemove to hide the large keyboard
    # and show the Education Dashboard inline menu
    await message.answer(
        text, 
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Send a separate message with the Education inline keyboard
    await message.answer(
        _("🎓 Раздел Обучения: Выберите категорию"),
        reply_markup=get_education_menu_keyboard()
    )


@router.callback_query(F.data == "education")
async def education_callback_entry(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Entry point for Education section (Callback from main menu)."""
    logger.info(f"User {callback.from_user.id} entered Education section via main menu callback")
    
    # Show Main Education Menu with new standardized keyboard
    text = _("🎓 Раздел Обучения: Выберите категорию")
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_menu_keyboard()
        )
    await callback.answer()

@router.callback_query(EducationCallback.filter(F.action == "main"))
async def education_main(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Main menu of Education section."""
    # Show Dashboard (Screen 1)
    user_id = callback.from_user.id
    
    # Get user progress data
    progress_data = await EducationService.calculate_overall_progress(user_id, session)
    overall_progress = progress_data.get("overall_progress", 0)
    current_status = progress_data.get("current_status", _("Студент"))
    last_activity = progress_data.get("last_activity", _("Недавно"))
    
    # Create progress bar
    progress_bar_length = 10
    filled = int(overall_progress / 100 * progress_bar_length)
    progress_bar = "🟩" * filled + "⬜️" * (progress_bar_length - filled)
    
    text = _(
        "📚 ДАШБОРД ОБУЧЕНИЯ\n\n"
        "Текущий статус: {status}\n"
        "Общий прогресс: {progress_bar} {progress}%\n"
        "Последняя активность: {last_activity}\n\n"
        "Выберите действие:"
    ).format(
        status=current_status,
        progress_bar=progress_bar,
        progress=int(overall_progress),
        last_activity=last_activity
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_dashboard_keyboard())
    await callback.answer()






@router.callback_query(EducationCallback.filter(F.action == "category"))
async def category_courses(callback: types.CallbackQuery, callback_data: EducationCallback, session: AsyncSession) -> None:
    """Courses in a specific category."""
    # For now, show mock courses for the category
    category_id = callback_data.course_id or 0
    categories = ["Акыда", "Фикх", "Коран", "История", "Арабский"]
    category_name = categories[category_id % len(categories)] if category_id > 0 else "Акыда"
    
    # Get courses from database for this category
    courses = await EducationService.get_courses_by_category(category_name, session)
    
    if not courses:
        text = _(
            "📖 {category_name}\n\n"
            "В этой категории пока нет курсов.\n"
            "Мы работаем над добавлением новых материалов!"
        ).format(category_name=category_name)
    else:
        course_list = "\n".join([f"• {course['title']} ({course['level']})" for course in courses[:5]])
        text = _(
            "📖 {category_name}\n\n"
            "Доступные курсы:\n\n"
            "{course_list}\n\n"
            "Выберите курс для подробной информации."
        ).format(category_name=category_name, course_list=course_list)
    
    # For now, use catalog keyboard
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_catalog_keyboard(categories))
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "course_detail"))
async def course_detail_view(callback: types.CallbackQuery, callback_data: EducationCallback, session: AsyncSession) -> None:
    """Course detail view."""
    course_id = callback_data.course_id or 1
    
    # Get course details from database
    course = await EducationService.get_course_detail(course_id, session)
    
    if not course:
        text = _("Курс не найден.")
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=get_catalog_keyboard())
        await callback.answer()
        return
    
    # Check if user has progress
    user_id = callback.from_user.id
    user_progress = await EducationService.get_user_course_progress(user_id, course_id, session)
    has_progress = user_progress is not None
    
    text = _(
        "📖 {title}\n\n"
        "{description}\n\n"
        "Уровень: {level}\n"
        "Продолжительность: {hours} часов\n"
        "Модулей: {modules}\n"
        "Статус: {status}\n\n"
        "Выберите действие:"
    ).format(
        title=course["title"],
        description=course.get("short_description", course.get("description", "")[:200] + "..."),
        level=course.get("level", "beginner"),
        hours=course.get("estimated_hours", 10),
        modules=course.get("total_modules", 5),
        status=_("В процессе") if has_progress else _("Не начат")
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_course_detail_keyboard(course_id, has_progress))
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "course_modules"))
async def course_modules_view(callback: types.CallbackQuery, callback_data: EducationCallback, session: AsyncSession) -> None:
    """Course modules list view."""
    course_id = callback_data.course_id or 1
    
    # Get course modules from database
    modules = await EducationService.get_course_modules(course_id, session)
    
    if not modules:
        text = _("Модули курса не найдены.")
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=get_course_detail_keyboard(course_id, False))
        await callback.answer()
        return
    
    # Get user progress for modules
    user_id = callback.from_user.id
    user_progress = await EducationService.get_user_module_progress(user_id, course_id, session)
    
    # Prepare modules status
    modules_status = []
    for i, module in enumerate(modules, 1):
        status = "locked"
        if i == 1:
            status = "completed"
        elif i == 2:
            status = "current"
        
        modules_status.append((module["id"], f"{'✅' if status == 'completed' else '🔄' if status == 'current' else '⏳'} {module['title']}", status))
    
    text = _(
        "📋 УРОКИ КУРСА\n\n"
        "Список модулей с вашим прогрессом:\n\n"
        "✅ - Завершено\n"
        "🔄 - Текущий урок\n"
        "⏳ - Заблокировано\n\n"
        "Выберите модуль для изучения:"
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_course_modules_keyboard(course_id, modules_status))
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "view_module"))
async def lesson_view(callback: types.CallbackQuery, callback_data: EducationCallback, session: AsyncSession) -> None:
    """Lesson view (Screen 3)."""
    module_id = callback_data.module_id or 1
    
    # Get module details from database
    module = await EducationService.get_module_detail(module_id, session)
    
    if not module:
        text = _("Модуль не найден.")
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=get_course_modules_keyboard(1))
        await callback.answer()
        return
    
    # Get course info for progress
    course_id = module.get("course_id", 1)
    course_modules = await EducationService.get_course_modules(course_id, session)
    module_index = next((i for i, m in enumerate(course_modules, 1) if m["id"] == module_id), 1)
    total_modules = len(course_modules)
    
    text = _(
        "📖 УРОК {current} из {total}\n\n"
        "{title}\n\n"
        "{description}\n\n"
        "Продолжительность: {duration} минут\n"
        "Тип контента: {content_type}\n\n"
        "Выберите формат изучения:"
    ).format(
        current=module_index,
        total=total_modules,
        title=module["title"],
        description=module.get("description", "Описание урока")[:200] + "...",
        duration=module.get("duration_minutes", 15),
        content_type=_("Видео") if module.get("has_video", True) else _("Текст")
    )
    
    has_video = module.get("has_video", True)
    has_audio = module.get("has_audio", True)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_lesson_keyboard_with_mark_studied(module_id))
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action.in_(["streams", "assistant"])))
async def stub_sections(callback: types.CallbackQuery) -> None:
    """Stub sections (streams, assistant)."""
    action = callback.data.split(":")[1] if callback.data else "streams"
    
    if action == "streams":
        section_name = _("Эфиры")
    else:
        section_name = _("Помощник")
    
    text = _(
        "🚧 РАЗДЕЛ В РАЗРАБОТКЕ\n\n"
        "Функция \"{section_name}\" находится в разработке.\n"
        "Мы работаем над добавлением новых курсов!\n\n"
        "Ожидайте обновления в ближайшее время. ⏳"
    ).format(section_name=section_name)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_stub_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "course"))
async def course_detail(
    callback: types.CallbackQuery,
    callback_data: EducationCallback,
    session: AsyncSession
) -> None:
    """Course detail view."""
    course_id = callback_data.course_id
    user_id = callback.from_user.id
    
    # Fetch course details
    course_detail = await EducationService.get_course_detail(course_id, session)
    if not course_detail:
        await callback.answer(_("Курс не найден."), show_alert=True)
        return
    
    # Fetch user progress data to get progress for this course
    data = await EducationService.get_user_progress_data(user_id, session)
    active_courses = data["active_courses"]
    progress = None
    for course in active_courses:
        if course["id"] == course_id:
            progress = course
            break
    
    if progress:
        progress_percentage = progress["progress_percentage"]
        completed_modules = progress["completed_modules"]
        total_modules = progress["total_modules"]
    else:
        # Fallback mock progress
        progress_percentage = 65.0 if course_id == 1 else 40.0
        completed_modules = 3 if course_id == 1 else 2
        total_modules = course_detail["total_modules"] or 5
    
    text = _(
        "📖 {course_name}\n\n"
        "Прогресс: {progress}%\n"
        "Модули: {completed}/{total}\n\n"
        "Выберите действие:"
    ).format(
        course_name=course_detail["title"],
        progress=int(progress_percentage),
        completed=completed_modules,
        total=total_modules,
    )
    
    # Use active courses keyboard for now
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_active_courses_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "continue"))
async def continue_course(callback: types.CallbackQuery) -> None:
    """Continue course action."""
    text = _(
        "▶ ПРОДОЛЖЕНИЕ КУРСА\n\n"
        "Вы продолжаете курс \"Основы ислама\".\n"
        "Следующий модуль: \"Модуль 4: Основы веры\"\n\n"
        "Функция прохождения курса находится в разработке."
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_active_courses_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "detailed_progress"))
async def detailed_progress(callback: types.CallbackQuery) -> None:
    """Detailed progress view."""
    text = _(
        "📊 ДЕТАЛЬНЫЙ ПРОГРЕСС\n\n"
        "Курс: Основы ислама\n"
        "Прогресс: 65%\n"
        "Пройдено модулей: 3 из 5\n"
        "Время обучения: 4ч 30м\n\n"
        "Модули:\n"
        "✅ 1. Введение (15 мин)\n"
        "✅ 2. Основы (45 мин)\n"
        "✅ 3. Практика (1ч 30м)\n"
        "⏳ 4. Углубление (2ч)\n"
        "⏳ 5. Заключение (1ч)\n\n"
        "Продолжайте в том же духе!"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_active_courses_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "review"))
async def review_course(callback: types.CallbackQuery, callback_data: EducationCallback) -> None:
    """Review completed course."""
    course_id = callback_data.course_id
    if course_id == 1:
        course_name = _("Введение в ислам")
        medal = "🥇"
    elif course_id == 2:
        course_name = _("Фикх очищения")
        medal = "🥈"
    else:
        course_name = _("История пророков")
        medal = "🥉"
    
    text = _(
        "{medal} ПОВТОРЕНИЕ КУРСА\n\n"
        "Курс: {course_name}\n"
        "Результат: 92%\n"
        "Время прохождения: 8 часов\n\n"
        "Выберите модуль для повторения:"
    ).format(medal=medal, course_name=course_name)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_completed_courses_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "review_all"))
async def review_all_material(callback: types.CallbackQuery) -> None:
    """Review all material."""
    text = _(
        "🔄 ПОВТОРЕНИЕ МАТЕРИАЛА\n\n"
        "Вы можете повторить любой из завершенных курсов.\n"
        "Выберите курс из списка выше.\n\n"
        "Повторение - мать учения! 📚"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_completed_courses_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "new_test"))
async def new_test(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Start a new test."""
    tests = await EducationService.get_all_tests(session, limit=5)
    lines = []
    for i, test in enumerate(tests, 1):
        lines.append(f'{i}. {test["title"]} ({test["question_count"]} вопросов)')
    
    text = _(
        "📝 НОВЫЙ ТЕСТ\n\n"
        "Доступные тесты:\n{list}\n\n"
        "Выберите тест для прохождения."
    ).format(list="\n".join(lines))
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_tests_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "my_results"))
async def my_results(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """My test results."""
    user_id = callback.from_user.id
    results = await EducationService.get_user_test_results(user_id, session)
    
    lines = []
    total_score = 0
    for i, res in enumerate(results[:3], 1):
        # Fetch test title
        test_detail = await EducationService.get_test_detail(res["test_id"], session)
        title = test_detail["title"] if test_detail else f"Тест {res['test_id']}"
        score = res["score_percentage"]
        correct = res["correct_answers"]
        total = res["total_questions"]
        lines.append(f'{i}. {title} - {score:.0f}% ({correct}/{total})')
        total_score += score
    
    avg_score = total_score / len(results) if results else 0
    best_score = max([r["score_percentage"] for r in results]) if results else 0
    
    text = _(
        "📊 МОИ РЕЗУЛЬТАТЫ\n\n"
        "Последние результаты:\n{list}\n\n"
        "Средний результат: {avg:.0f}%\n"
        "Лучший результат: {best:.0f}%\n\n"
        "Продолжайте совершенствоваться!"
    ).format(list="\n".join(lines), avg=avg_score, best=best_score)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_tests_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "detailed_stats"))
async def detailed_stats(callback: types.CallbackQuery) -> None:
    """Detailed statistics."""
    text = _(
        "📈 ДЕТАЛЬНАЯ СТАТИСТИКА\n\n"
        "Общая статистика:\n"
        "• Всего курсов: 5\n"
        "• Завершено: 3 (60%)\n"
        "• Всего тестов: 12\n"
        "• Пройдено: 8 (67%)\n\n"
        "Активность за месяц:\n"
        "• Дней обучения: 15\n"
        "• Среднее время: 45 мин/день\n"
        "• Серия: 5 дней подряд\n\n"
        "Достижения: 8 из 15 🏆"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_progress_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "month_stats"))
async def month_stats(callback: types.CallbackQuery) -> None:
    """Monthly statistics."""
    text = _(
        "📅 СТАТИСТИКА ЗА МЕСЯЦ\n\n"
        "Ноябрь 2025:\n"
        "• Курсов завершено: 2\n"
        "• Тестов пройдено: 5\n"
        "• Время обучения: 15ч 30м\n"
        "• Уровень повысился: 10 → 12\n\n"
        "График активности:\n"
        "Пн: ███ 2ч\n"
        "Вт: █████ 4ч\n"
        "Ср: ██ 1.5ч\n"
        "Чт: ██████ 5ч\n"
        "Пт: ███ 2ч\n"
        "Сб: █ 30м\n"
        "Вс: ████ 3ч"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_progress_keyboard())
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "year_stats"))
async def year_stats(callback: types.CallbackQuery) -> None:
    """Yearly statistics."""
    text = _(
        "📅 СТАТИСТИКА ЗА ГОД\n\n"
        "2025 год:\n"
        "• Курсов завершено: 8\n"
        "• Тестов пройдено: 24\n"
        "• Время обучения: 120ч 45м\n"
        "• Уровень повысился: 5 → 12\n\n"
        "Достижения: 15 из 25 🏆"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_progress_keyboard())
    await callback.answer()


# ==================== NEW HANDLERS FOR QUIZ & PROGRESS ====================

@router.callback_query(EducationCallback.filter(F.action == "mark_studied"))
async def mark_studied_handler(
    callback: types.CallbackQuery,
    callback_data: EducationCallback,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Handle 'Mark as Studied' button - start quiz."""
    module_id = callback_data.module_id or 1
    user_id = callback.from_user.id
    
    # Get module details
    module = await EducationService.get_module_detail(module_id, session)
    if not module:
        await callback.answer(_("Модуль не найден."), show_alert=True)
        return
    
    # Get quiz questions for this module
    questions = await EducationService.get_module_quiz_questions(module_id, session, limit=3)
    
    if not questions:
        # If no quiz questions, mark as completed directly
        result = await EducationService.update_user_progress_after_quiz(
            user_id, module_id, quiz_score=100.0, passed=True, session=session
        )
        
        if result["success"]:
            text = _(
                "✅ УРОК ЗАВЕРШЕН\n\n"
                "Поздравляем! Вы успешно изучили урок.\n"
                "Прогресс курса: {progress}%\n\n"
                "Следующий урок разблокирован!"
            ).format(progress=int(result["course_progress"]["progress_percentage"]))
            
            if result.get("next_module"):
                text += f"\n\nСледующий урок: {result['next_module']['title']}"
        else:
            text = _("Произошла ошибка при обновлении прогресса.")
        
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=get_lesson_keyboard(module_id))
        await callback.answer()
        return
    
    # Store quiz data in FSM
    quiz_data = QuizData(
        module_id=module_id,
        questions=questions,
        current_question_index=0,
        score=0,
        user_answers=[],
        passing_score=70
    )
    
    await state.set_state(QuizState.answering_question)
    await state.set_data(quiz_data.to_dict())
    
    # Show first question
    question = questions[0]
    question_text = _(
        "📝 ТЕСТ ПОСЛЕ УРОКА\n\n"
        "Вопрос 1 из {total}:\n\n"
        "{question_text}\n\n"
        "Выберите правильный ответ:"
    ).format(total=len(questions), question_text=question["question_text"])
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            question_text,
            reply_markup=get_quiz_question_keyboard(
                question_id=question["id"],
                options=question["options"],
                question_type=question["question_type"]
            )
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "quiz_answer"))
async def quiz_answer_handler(
    callback: types.CallbackQuery,
    callback_data: EducationCallback,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Handle quiz answer selection."""
    user_id = callback.from_user.id
    selected_option_id = callback_data.option_id
    question_id = callback_data.question_id
    
    # Get current quiz data
    data = await state.get_data()
    quiz_data = QuizData.from_dict(data)
    
    # Find current question
    current_question = quiz_data.questions[quiz_data.current_question_index]
    if current_question["id"] != question_id:
        await callback.answer(_("Вопрос устарел."), show_alert=True)
        return
    
    # Check answer correctness
    selected_ids = [selected_option_id] if selected_option_id else []
    is_correct, points_earned = await EducationService.check_answer_correctness(
        question_id, selected_ids, session
    )
    
    # Store user answer
    quiz_data.user_answers.append({
        "question_id": question_id,
        "selected_option_ids": selected_ids,
        "is_correct": is_correct,
        "points_earned": points_earned
    })
    
    # Update score
    quiz_data.score += points_earned
    
    # Show explanation if available
    option_explanation = None
    for option in current_question["options"]:
        if option["id"] == selected_option_id:
            option_explanation = option.get("explanation")
            break
    
    if option_explanation:
        text = _(
            "📝 РЕЗУЛЬТАТ\n\n"
            "Ваш ответ: {correct}\n\n"
            "Объяснение:\n{explanation}\n\n"
            "Нажмите 'Далее' для продолжения."
        ).format(
            correct=_("Правильно ✅") if is_correct else _("Неправильно ❌"),
            explanation=option_explanation
        )
    else:
        text = _(
            "📝 РЕЗУЛЬТАТ\n\n"
            "Ваш ответ: {correct}\n\n"
            "Нажмите 'Далее' для продолжения."
        ).format(correct=_("Правильно ✅") if is_correct else _("Неправильно ❌"))
    
    await state.set_data(quiz_data.to_dict())
    await state.set_state(QuizState.question_explanation)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_quiz_result_keyboard(is_correct))
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "quiz_next"))
async def quiz_next_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Handle next question in quiz."""
    data = await state.get_data()
    quiz_data = QuizData.from_dict(data)
    
    # Move to next question
    quiz_data.current_question_index += 1
    
    if quiz_data.current_question_index >= len(quiz_data.questions):
        # Quiz completed
        await state.set_state(QuizState.quiz_completed)
        
        # Calculate final score
        total_points = sum(q["points"] for q in quiz_data.questions)
        score_percentage = (quiz_data.score / total_points * 100) if total_points > 0 else 0
        passed = score_percentage >= quiz_data.passing_score
        
        # Update user progress
        user_id = callback.from_user.id
        result = await EducationService.update_user_progress_after_quiz(
            user_id, quiz_data.module_id, score_percentage, passed, session
        )
        
        if result["success"]:
            if passed:
                text = _(
                    "🎉 ТЕСТ ПРОЙДЕН!\n\n"
                    "Ваш результат: {score:.0f}%\n"
                    "Прогресс курса: {progress}%\n\n"
                    "Поздравляем! Урок завершен."
                ).format(score=score_percentage, progress=int(result["course_progress"]["progress_percentage"]))
                
                if result.get("next_module"):
                    text += f"\n\nСледующий урок разблокирован: {result['next_module']['title']}"
            else:
                text = _(
                    "📝 ТЕСТ НЕ ПРОЙДЕН\n\n"
                    "Ваш результат: {score:.0f}%\n"
                    "Требуется: {passing}%\n\n"
                    "Попробуйте еще раз!"
                ).format(score=score_percentage, passing=quiz_data.passing_score)
        else:
            text = _("Произошла ошибка при обновлении прогресса.")
        
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=get_lesson_keyboard(quiz_data.module_id))
        await state.clear()
        
    else:
        # Show next question
        await state.set_state(QuizState.answering_question)
        await state.set_data(quiz_data.to_dict())
        
        question = quiz_data.questions[quiz_data.current_question_index]
        question_text = _(
            "📝 ТЕСТ ПОСЛЕ УРОКА\n\n"
            "Вопрос {current} из {total}:\n\n"
            "{question_text}\n\n"
            "Выберите правильный ответ:"
        ).format(
            current=quiz_data.current_question_index + 1,
            total=len(quiz_data.questions),
            question_text=question["question_text"]
        )
        
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                question_text,
                reply_markup=get_quiz_question_keyboard(
                    question_id=question["id"],
                    options=question["options"],
                    question_type=question["question_type"]
                )
            )
    
    await callback.answer()




@router.message(AIAssistantState.waiting_for_query)
async def assistant_query_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Handle AI assistant query."""
    query = message.text
    user_id = message.from_user.id
    
    if not query or len(query.strip()) < 3:
        await message.answer(_("Пожалуйста, задайте вопрос длиннее 3 символов."))
        return
    
    await state.set_state(AIAssistantState.processing_query)
    
    # Show processing message
    processing_msg = await message.answer(_("🤔 Обрабатываю ваш вопрос..."))
    
    # Get AI response
    response_data = await EducationService.get_ai_response(query, user_id, session)
    
    if response_data["constraints_respected"]:
        text = _(
            "🤖 ОТВЕТ\n\n"
            "{response}\n\n"
            "Источники: {sources}\n\n"
            "Задайте еще вопрос или вернитесь в меню."
        ).format(
            response=response_data["response"],
            sources=", ".join(response_data["sources"])
        )
    else:
        text = _(
            "🤖 ОТВЕТ\n\n"
            "Извините, я не могу ответить на этот вопрос.\n"
            "Пожалуйста, обратитесь к ученым или задайте другой вопрос."
        )
    
    await processing_msg.delete()
    await message.answer(text, reply_markup=get_ai_assistant_keyboard())
    await state.set_state(AIAssistantState.waiting_for_query)


# ==================== NEW NAVIGATION HANDLERS ====================

@router.callback_query(F.data == "education_entry")
async def education_entry_handler(callback: types.CallbackQuery) -> None:
    """
    Main Education Handler (Entry Point).
    Catches the initial "Education" button click from Main Menu.
    """
    logger.info(f"User {callback.from_user.id} entered Education section")
    
    text = _("🎓 Раздел Обучения: Выберите категорию")
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "catalog"))
async def edu_catalog_handler(callback: types.CallbackQuery) -> None:
    """Catalog sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Catalog")
    
    text = _(
        "📚 Каталог курсов\n\n"
        "Здесь вы найдете все доступные курсы по различным темам:\n"
        "• Акыда (Основы веры)\n"
        "• Фикх (Исламское право)\n"
        "• Коран (Чтение и тафсир)\n"
        "• История ислама\n"
        "• Арабский язык\n\n"
        "Выберите категорию для просмотра курсов."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "active"))
async def edu_active_handler(callback: types.CallbackQuery) -> None:
    """Active courses sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Active courses")
    
    text = _(
        "▶️ Активные курсы\n\n"
        "Здесь отображаются курсы, которые вы сейчас проходите.\n"
        "Вы можете продолжить обучение с того места, где остановились,\n"
        "или просмотреть свой прогресс по каждому курсу.\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "tests"))
async def edu_tests_handler(callback: types.CallbackQuery) -> None:
    """Tests sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Tests")
    
    text = _(
        "📝 Тесты\n\n"
        "Проверьте свои знания с помощью интерактивных тестов.\n"
        "Доступны тесты по различным темам и уровням сложности.\n\n"
        "Вы можете:\n"
        "• Пройти новые тесты\n"
        "• Просмотреть результаты\n"
        "• Повторить пройденные тесты\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "progress"))
async def edu_progress_handler(callback: types.CallbackQuery) -> None:
    """Progress sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Progress")
    
    text = _(
        "📈 Прогресс\n\n"
        "Отслеживайте свой прогресс в обучении:\n"
        "• Общий прогресс по всем курсам\n"
        "• Статистика по дням и неделям\n"
        "• Достижения и награды\n"
        "• Графики активности\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "completed"))
async def edu_completed_handler(callback: types.CallbackQuery) -> None:
    """Completed courses sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Completed courses")
    
    text = _(
        "🏆 Завершенные курсы\n\n"
        "Здесь отображаются курсы, которые вы успешно завершили.\n"
        "Вы можете просмотреть сертификаты, повторить материал\n"
        "или поделиться своими достижениями.\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "streams"))
async def edu_streams_handler(callback: types.CallbackQuery) -> None:
    """Streams sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected Streams")
    
    text = _(
        "📡 Эфиры\n\n"
        "Смотрите прямые трансляции и записи эфиров:\n"
        "• Прямые эфиры с преподавателями\n"
        "• Архив прошедших трансляций\n"
        "• Расписание будущих эфиров\n"
        "• Уведомления о начале эфиров\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "assistant"))
async def edu_assistant_handler(callback: types.CallbackQuery) -> None:
    """AI Assistant sub-menu handler."""
    logger.info(f"User {callback.from_user.id} selected AI Assistant")
    
    text = _(
        "🤖 AI Помощник\n\n"
        "Задавайте вопросы об исламе и получайте ответы:\n"
        "• Ответы на вопросы по основам веры\n"
        "• Объяснение аятов Корана и хадисов\n"
        "• Исторические справки\n"
        "• Рекомендации по дальнейшему обучению\n\n"
        "Функция находится в активной разработке."
    )
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_sub_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(EducationCallback.filter(F.action == "menu_back"))
async def edu_menu_back_handler(callback: types.CallbackQuery) -> None:
    """
    Navigation handler for 'Back' button.
    Returns to the Main Education Menu.
    """
    logger.info(f"User {callback.from_user.id} clicked Back to Education Menu")
    
    text = _("🎓 Раздел Обучения: Выберите категорию")
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=get_education_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery) -> None:
    """
    Navigation handler for 'Main Menu' button.
    Returns to the root Main Menu and shows the Reply Keyboard.
    """
    logger.info(f"User {callback.from_user.id} clicked Main Menu from Education")
    
    from bot.keyboards.reply import get_main_menu
    
    text = _("Главное меню")
    
    # Send a new message with the Reply Keyboard instead of editing
    # This ensures the Reply Keyboard appears properly
    await callback.message.answer(
        text,
        reply_markup=get_main_menu()
    )
    
    # Optionally delete the previous inline message for cleaner UI
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    
    await callback.answer()
