"""
Finite State Machine (FSM) states for education module.
"""
from aiogram.fsm.state import State, StatesGroup


class EducationStates(StatesGroup):
    """FSM states for education module."""
    pass


class CourseLearningState(StatesGroup):
    """FSM states for course learning flow."""
    selecting_course = State()        # Выбор курса
    viewing_module = State()          # Просмотр модуля
    watching_video = State()          # Просмотр видео
    listening_audio = State()         # Прослушивание аудио
    reading_telegraph = State()       # Чтение Telegraph статьи
    answering_quiz = State()          # Ответ на тест после урока
    taking_notes = State()            # Создание заметок
    module_completed = State()        # Модуль завершен


class QuizState(StatesGroup):
    """FSM states for post-lesson quiz."""
    starting_quiz = State()           # Начало теста после урока
    answering_question = State()      # Ответ на вопрос
    question_explanation = State()    # Объяснение ответа
    reviewing_results = State()       # Просмотр результатов
    quiz_completed = State()          # Тест завершен


class AIAssistantState(StatesGroup):
    """FSM states for AI assistant."""
    waiting_for_query = State()       # Ожидание запроса
    processing_query = State()        # Обработка запроса
    showing_answer = State()          # Показ ответа


class StreamState(StatesGroup):
    """FSM states for streams."""
    browsing_streams = State()        # Просмотр списка эфиров
    viewing_stream = State()          # Просмотр деталей эфира
    setting_reminder = State()        # Установка напоминания
    watching_recording = State()      # Просмотр записи


# Data classes for FSM storage
class CourseLearningData:
    """Data class to store course learning session data."""
    def __init__(
        self,
        course_id: int,
        module_id: int,
        module_index: int,
        total_modules: int,
        has_quiz: bool = True
    ):
        self.course_id = course_id
        self.module_id = module_id
        self.module_index = module_index
        self.total_modules = total_modules
        self.has_quiz = has_quiz
        self.quiz_passed = False
        self.quiz_score = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for FSM storage."""
        return {
            "course_id": self.course_id,
            "module_id": self.module_id,
            "module_index": self.module_index,
            "total_modules": self.total_modules,
            "has_quiz": self.has_quiz,
            "quiz_passed": self.quiz_passed,
            "quiz_score": self.quiz_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CourseLearningData":
        """Create instance from dictionary."""
        instance = cls(
            course_id=data["course_id"],
            module_id=data["module_id"],
            module_index=data["module_index"],
            total_modules=data["total_modules"],
            has_quiz=data.get("has_quiz", True)
        )
        instance.quiz_passed = data.get("quiz_passed", False)
        instance.quiz_score = data.get("quiz_score", 0)
        return instance


class QuizData:
    """Data class to store quiz session data."""
    def __init__(
        self,
        module_id: int,
        questions: list,
        current_question_index: int = 0,
        score: int = 0,
        user_answers: list = None,
        passing_score: int = 70
    ):
        self.module_id = module_id
        self.questions = questions  # список словарей с вопросами и вариантами
        self.current_question_index = current_question_index
        self.score = score
        self.user_answers = user_answers or []
        self.passing_score = passing_score

    def to_dict(self) -> dict:
        """Convert to dictionary for FSM storage."""
        return {
            "module_id": self.module_id,
            "questions": self.questions,
            "current_question_index": self.current_question_index,
            "score": self.score,
            "user_answers": self.user_answers,
            "passing_score": self.passing_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QuizData":
        """Create instance from dictionary."""
        return cls(
            module_id=data["module_id"],
            questions=data["questions"],
            current_question_index=data["current_question_index"],
            score=data["score"],
            user_answers=data["user_answers"],
            passing_score=data.get("passing_score", 70)
        )
