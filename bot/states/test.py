"""
Finite State Machine (FSM) states for test taking flow.
"""
from aiogram.fsm.state import State, StatesGroup


class TestStates(StatesGroup):
    """Состояния FSM для модуля тестов."""
    pass


class TestTakingStateGroup(StatesGroup):
    """FSM states for test taking."""
    choosing_test = State()      # Выбор теста из списка
    in_progress = State()        # Нахождение внутри теста (вопрос-ответ)
    finished = State()           # Тест завершен, ожидание сохранения результата


class TestTakingData:
    """Data class to store test session data."""
    def __init__(
        self,
        test_id: int,
        test_title: str,
        questions: list,
        current_question_index: int = 0,
        score: int = 0,
        user_answers: list = None,
        start_time: float = None
    ):
        self.test_id = test_id
        self.test_title = test_title
        self.questions = questions  # список словарей с вопросами и вариантами
        self.current_question_index = current_question_index
        self.score = score
        self.user_answers = user_answers or []
        self.start_time = start_time

    def to_dict(self) -> dict:
        """Convert to dictionary for FSM storage."""
        return {
            "test_id": self.test_id,
            "test_title": self.test_title,
            "questions": self.questions,
            "current_question_index": self.current_question_index,
            "score": self.score,
            "user_answers": self.user_answers,
            "start_time": self.start_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TestTakingData":
        """Create instance from dictionary."""
        return cls(
            test_id=data["test_id"],
            test_title=data["test_title"],
            questions=data["questions"],
            current_question_index=data["current_question_index"],
            score=data["score"],
            user_answers=data["user_answers"],
            start_time=data["start_time"],
        )
