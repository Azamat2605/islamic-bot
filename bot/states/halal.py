from aiogram.fsm.state import State, StatesGroup


class HalalStates(StatesGroup):
    """
    Состояния FSM для модуля Halal Places.
    """
    waiting_for_location = State()      # Ожидание геолокации
    waiting_for_search_query = State()  # Ожидание поискового запроса
    viewing_place_details = State()     # Просмотр деталей места
