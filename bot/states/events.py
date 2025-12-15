"""
Состояния FSM для работы с мероприятиями.
"""
from aiogram.fsm.state import State, StatesGroup


class EventStates(StatesGroup):
    """Состояния FSM для модуля мероприятий."""
    pass


class EventProposalState(StatesGroup):
    """Состояния для предложения мероприятия."""
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_description = State()


class EventRegistrationState(StatesGroup):
    """Состояния для регистрации на мероприятия."""
    waiting_for_confirmation = State()


class EventManagementState(StatesGroup):
    """Состояния для управления мероприятиями (админ)."""
    waiting_for_event_selection = State()
    waiting_for_action = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()
