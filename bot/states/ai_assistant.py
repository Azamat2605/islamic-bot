from aiogram.fsm.state import State, StatesGroup


class AIAssistantState(StatesGroup):
    """Состояния для ИИ-помощника."""
    main_menu = State()          # Главное меню ИИ-помощника
    chat_mode = State()          # Режим общения
    image_mode = State()         # Режим генерации изображений
    waiting_for_question = State()  # Ожидание вопроса (оставить для обратной совместимости)
