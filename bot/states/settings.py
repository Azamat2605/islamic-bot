from aiogram.fsm.state import State, StatesGroup


class TimezoneStates(StatesGroup):
    """Состояния FSM для настройки часового пояса."""
    entering_timezone = State()


class AccountStates(StatesGroup):
    """Состояния FSM для управления аккаунтом."""
    confirming_deletion = State()
    confirming_export = State()
