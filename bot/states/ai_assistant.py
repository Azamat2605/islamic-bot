from aiogram.fsm.state import State, StatesGroup


class AIAssistantState(StatesGroup):
    """Состояния для ИИ-помощника."""
    waiting_for_question = State()
