"""
Test taking handlers using Finite State Machine (FSM).
"""
import time
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from bot.states.test import TestTakingStateGroup, TestTakingData
from bot.keyboards.inline.test import (
    TestSelectionCallback, TestAnswerCallback,
    get_test_selection_keyboard, get_answer_options_keyboard,
    get_test_progress_keyboard, get_test_finished_keyboard
)
from bot.services.education_service import EducationService
from bot.keyboards.inline.education import get_tests_keyboard

router = Router(name="test_taking")


@router.callback_query(F.data == "start_selection")
async def start_test_selection(
    callback: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Start test selection: show list of available tests."""
    tests = await EducationService.get_all_tests(session, limit=10)
    if not tests:
        await callback.answer(_("Нет доступных тестов."), show_alert=True)
        return

    text = _(
        "📝 ВЫБОР ТЕСТА\n\n"
        "Выберите тест для прохождения:\n\n"
        "После выбора вы начнёте проходить тест. "
        "У вас будет ограниченное время на каждый вопрос."
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_test_selection_keyboard(tests)
    )
    await state.set_state(TestTakingStateGroup.choosing_test)
    await callback.answer()


@router.callback_query(TestSelectionCallback.filter(), TestTakingStateGroup.choosing_test)
async def select_test(
    callback: types.CallbackQuery,
    callback_data: TestSelectionCallback,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """User selects a specific test."""
    test_id = callback_data.test_id
    test_detail = await EducationService.get_test_detail(test_id, session)
    if not test_detail:
        await callback.answer(_("Тест не найден."), show_alert=True)
        return

    # Fetch all questions with options
    questions = await EducationService.get_test_questions_with_options(test_id, session)
    if not questions:
        await callback.answer(_("В тесте нет вопросов."), show_alert=True)
        return

    # Initialize test session data
    test_data = TestTakingData(
        test_id=test_id,
        test_title=test_detail["title"],
        questions=questions,
        current_question_index=0,
        score=0,
        user_answers=[],
        start_time=time.time()
    )
    await state.update_data(test_data=test_data.to_dict())

    # Send first question
    await send_question(callback.message, test_data, session)
    await state.set_state(TestTakingStateGroup.in_progress)
    await callback.answer()


async def send_question(
    message: types.Message,
    test_data: TestTakingData,
    session: AsyncSession
) -> None:
    """Send a question to the user."""
    question = test_data.questions[test_data.current_question_index]
    question_number = test_data.current_question_index + 1
    total_questions = len(test_data.questions)

    text = _(
        "📝 Вопрос {current}/{total}\n\n"
        "{question_text}\n\n"
        "Выберите правильный ответ:"
    ).format(
        current=question_number,
        total=total_questions,
        question_text=question["question_text"]
    )

    # Prepare keyboard with answer options
    keyboard = get_answer_options_keyboard(question["id"], question["options"])
    # Add progress indicator
    progress_keyboard = get_test_progress_keyboard(question_number, total_questions)

    # Send message with question
    await message.edit_text(
        text,
        reply_markup=keyboard
    )
    # We could also send progress as a separate message, but for simplicity we'll just update the same message.


@router.callback_query(TestAnswerCallback.filter(), TestTakingStateGroup.in_progress)
async def process_answer(
    callback: types.CallbackQuery,
    callback_data: TestAnswerCallback,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Process user's answer and move to next question or finish."""
    user_id = callback.from_user.id
    data = await state.get_data()
    test_data = TestTakingData.from_dict(data["test_data"])

    current_question = test_data.questions[test_data.current_question_index]
    question_id = current_question["id"]

    # Check answer correctness
    is_correct, points_earned = await EducationService.check_answer_correctness(
        question_id=question_id,
        selected_option_ids=[callback_data.option_id],
        session=session
    )

    # Record answer
    test_data.user_answers.append({
        "question_id": question_id,
        "selected_option_ids": [callback_data.option_id],
        "is_correct": is_correct,
        "points_earned": points_earned
    })

    if is_correct:
        test_data.score += points_earned

    # Move to next question
    test_data.current_question_index += 1

    # Check if test is finished
    if test_data.current_question_index >= len(test_data.questions):
        # Calculate final score
        total_points = sum(q["points"] for q in test_data.questions)
        score_percentage = (test_data.score / total_points * 100) if total_points > 0 else 0
        correct_answers = sum(1 for ans in test_data.user_answers if ans["is_correct"])
        time_spent = int(time.time() - test_data.start_time)

        # Save result to database
        test_result = await EducationService.save_test_result(
            user_id=user_id,
            test_id=test_data.test_id,
            score=score_percentage,
            correct_answers=correct_answers,
            total_questions=len(test_data.questions),
            time_spent_seconds=time_spent,
            user_answers=test_data.user_answers,
            session=session
        )

        # Send completion message
        passed_text = _("✅ Тест пройден!") if test_result.passed else _("❌ Тест не пройден.")
        text = _(
            "{passed_text}\n\n"
            "📊 Результаты теста \"{test_title}\":\n"
            "• Правильных ответов: {correct}/{total}\n"
            "• Набрано баллов: {score:.1f}%\n"
            "• Время: {time_spent} сек\n"
            "• Попытка: {attempt}\n\n"
            "{message}"
        ).format(
            passed_text=passed_text,
            test_title=test_data.test_title,
            correct=correct_answers,
            total=len(test_data.questions),
            score=score_percentage,
            time_spent=time_spent,
            attempt=test_result.attempt_number,
            message=_("Поздравляем! 🎉") if test_result.passed else _("Попробуйте ещё раз!")
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_test_finished_keyboard(test_data.test_id)
        )
        await state.clear()
    else:
        # Update state and send next question
        await state.update_data(test_data=test_data.to_dict())
        await send_question(callback.message, test_data, session)

    await callback.answer()


@router.callback_query(F.data == "test_cancel")
async def cancel_test(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Cancel test and return to tests menu."""
    await state.clear()
    text = _(
        "❌ Тест отменён.\n\n"
        "Вы можете начать новый тест в любое время."
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_tests_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("test_results:"))
async def view_test_results(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """View detailed results of a specific test."""
    try:
        test_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer(_("Неверный идентификатор теста."), show_alert=True)
        return

    user_id = callback.from_user.id
    # Fetch latest result for this test
    from database.models import UserTestResult
    stmt = select(UserTestResult).where(
        UserTestResult.user_id == user_id,
        UserTestResult.test_id == test_id
    ).order_by(UserTestResult.completed_at.desc()).limit(1)
    result = await session.execute(stmt)
    test_result = result.scalar_one_or_none()

    if not test_result:
        await callback.answer(_("Результаты не найдены."), show_alert=True)
        return

    # Fetch test title
    test_detail = await EducationService.get_test_detail(test_id, session)
    title = test_detail["title"] if test_detail else f"Тест {test_id}"

    text = _(
        "📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ\n\n"
        "Тест: {title}\n"
        "Дата: {date}\n"
        "Правильных ответов: {correct}/{total}\n"
        "Результат: {score:.1f}%\n"
        "Время: {time} сек\n"
        "Попытка: {attempt}\n"
        "Статус: {status}"
    ).format(
        title=title,
        date=test_result.completed_at.strftime("%d.%m.%Y %H:%M"),
        correct=test_result.correct_answers,
        total=test_result.total_questions,
        score=test_result.score,
        time=test_result.time_spent_seconds,
        attempt=test_result.attempt_number,
        status=_("Пройден") if test_result.passed else _("Не пройден")
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_test_finished_keyboard(test_id)
    )
    await callback.answer()


# Import needed for select
from sqlalchemy import select
