from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from .i18n import ACLMiddleware
from .logging import LoggingMiddleware
from .throttling import ThrottlingMiddleware
from bot.core.loader import i18n as _i18n


def register_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    # dp.update.outer_middleware(DatabaseMiddleware())  # Temporarily disabled due to missing DB

    # dp.message.middleware(AuthMiddleware())  # Temporarily disabled due to missing DB

    ACLMiddleware(i18n=_i18n).setup(dp)

    dp.callback_query.middleware(CallbackAnswerMiddleware())
