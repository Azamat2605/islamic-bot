from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from .i18n import ACLMiddleware
from .logging import LoggingMiddleware
from .throttling import ThrottlingMiddleware
from .database import DatabaseMiddleware
from bot.core.loader import i18n as _i18n


def register_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    # i18n должен быть ДО DatabaseMiddleware, потому что он использует сессию
    ACLMiddleware(i18n=_i18n).setup(dp)

    dp.update.outer_middleware(DatabaseMiddleware())

    # dp.message.middleware(AuthMiddleware())  # Temporarily disabled due to missing DB

    dp.callback_query.middleware(CallbackAnswerMiddleware())
