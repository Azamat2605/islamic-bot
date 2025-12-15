from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    """Состояния FSM для модуля настроек."""
    pass


class TimezoneStates(StatesGroup):
    """Состояния FSM для настройки часового пояса."""
    entering_timezone = State()


class AccountStates(StatesGroup):
    """Состояния FSM для управления аккаунтом."""
    confirming_deletion = State()
    confirming_export = State()
