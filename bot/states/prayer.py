from aiogram.fsm.state import State, StatesGroup


class PrayerSettingsState(StatesGroup):
    """Состояния FSM для настроек намазов"""
    waiting_for_city = State()
