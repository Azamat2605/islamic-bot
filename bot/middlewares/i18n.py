"""1. Get all texts
pybabel extract --input-dirs=. -o bot/locales/messages.pot --project=messages.

2. Init translations
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l en
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l ru
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l ar
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l tt
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l ba

3. Compile translations
pybabel compile -d bot/locales -D messages --statistics

pybabel update -i bot/locales/messages.pot -d bot/locales -D messages

"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import logging

from aiogram.utils.i18n.middleware import I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import DEFAULT_LOCALE
from database.crud import get_user_language

if TYPE_CHECKING:
    from aiogram.types import TelegramObject, User

logger = logging.getLogger(__name__)


class ACLMiddleware(I18nMiddleware):
    DEFAULT_LANGUAGE_CODE = DEFAULT_LOCALE

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        # Отладочный вывод: проверяем наличие сессии и пользователя в data
        logger.debug(f"DEBUG i18n: data keys = {list(data.keys())}")
        logger.debug(f"DEBUG i18n: 'session' in data? {'session' in data}")
        logger.debug(f"DEBUG i18n: 'user' in data? {'user' in data}")
        
        # Получаем сессию из data (добавляется DatabaseMiddleware)
        session: AsyncSession | None = data.get("session")
        if session is None:
            logger.debug("DEBUG i18n: No session, returning default locale")
            # Приоритет 2: язык из Telegram (event.from_user.language_code)
            user: User | None = getattr(event, "from_user", None)
            if user:
                telegram_lang = getattr(user, "language_code", None)
                if telegram_lang:
                    logger.debug(f"DEBUG i18n: No session, using Telegram language for user {user.id}: {telegram_lang}")
                    return telegram_lang
            logger.debug("DEBUG i18n: No session and no Telegram language, returning default locale")
            return self.DEFAULT_LANGUAGE_CODE

        if hasattr(event, "chat_member"):
            logger.debug("DEBUG i18n: Chat member event, returning default locale")
            return self.DEFAULT_LANGUAGE_CODE

        user: User | None = getattr(event, "from_user", None)
        if not user:
            logger.debug("DEBUG i18n: No user, returning default locale")
            return self.DEFAULT_LANGUAGE_CODE

        # Приоритет 1: язык из базы данных
        language_code: str = await get_user_language(session=session, telegram_id=user.id)
        logger.debug(f"DEBUG i18n: Loaded locale from DB for user {user.id}: {language_code}")
        # Всегда возвращаем язык из БД, если сессия есть (даже если он равен дефолтному)
        locale = language_code or self.DEFAULT_LANGUAGE_CODE
        logger.debug(f"DEBUG i18n: Locale decided: {locale}")
        return locale
