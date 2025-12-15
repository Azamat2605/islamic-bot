"""
Inline keyboards for test taking flow.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _


class TestAnswerCallback(CallbackData, prefix="test_ans"):
    """Callback data for selecting an answer option."""
    question_id: int
    option_id: int


class TestSelectionCallback(CallbackData, prefix="test_sel"):
    """Callback data for selecting a test."""
    test_id: int


def get_test_selection_keyboard(tests: list) -> InlineKeyboardMarkup:
    """
    Create keyboard for selecting a test from a list.

    Args:
        tests: List of dicts with keys 'id', 'title', 'question_count'
    """
    buttons = []
    for test in tests:
        button_text = f"{test['title']} ({test['question_count']} вопросов)"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=TestSelectionCallback(test_id=test["id"]).pack()
            )
        ])
    # Add back button
    buttons.append([
        InlineKeyboardButton(
            text=_("🔙 Назад"),
            callback_data="education:main"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_answer_options_keyboard(question_id: int, options: list) -> InlineKeyboardMarkup:
    """
    Create keyboard with answer options (A, B, C, D).

    Args:
        question_id: ID of the current question
        options: List of dicts with keys 'id', 'option_text'
    """
    buttons = []
    letters = ["A", "B", "C", "D", "E", "F"]
    for idx, option in enumerate(options):
        if idx >= len(letters):
            break
        button_text = f"{letters[idx]}. {option['option_text']}"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=TestAnswerCallback(
                    question_id=question_id,
                    option_id=option["id"]
                ).pack()
            )
        ])
    # Add cancel button
    buttons.append([
        InlineKeyboardButton(
            text=_("❌ Отменить тест"),
            callback_data="test_cancel"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_test_progress_keyboard(current: int, total: int) -> InlineKeyboardMarkup:
    """
    Create keyboard showing test progress (e.g., "Вопрос 3 из 10").

    Args:
        current: Current question index (1-based)
        total: Total number of questions
    """
    progress_text = _("Вопрос {current} из {total}").format(
        current=current, total=total
    )
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=progress_text, callback_data="noop")
    ]])


def get_test_finished_keyboard(test_id: int) -> InlineKeyboardMarkup:
    """
    Create keyboard after test completion.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=_("📊 Посмотреть результаты"),
                callback_data=f"test_results:{test_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=_("📝 Пройти ещё раз"),
                callback_data=TestSelectionCallback(test_id=test_id).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text=_("🔙 В раздел тестов"),
                callback_data="education:tests"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
