from aiogram.fsm.state import State, StatesGroup


class PrayerStates(StatesGroup):
    """Состояния FSM для модуля намазов."""
    pass


class PrayerSettingsState(StatesGroup):
    """Состояния FSM для настроек намазов"""
    waiting_for_city = State()
