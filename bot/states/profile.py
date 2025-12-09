from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    """Состояния FSM для редактирования профиля."""
    entering_gender = State()
    entering_city = State()
    waiting_for_name = State()
