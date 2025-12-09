from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.users import is_admin
from bot.core.config import settings


class AdminFilter(BaseFilter):
    """Allows only administrators (either from ADMINS config or database column is_admin=True)."""

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        
        # Check config ADMINS list
        if user_id in settings.ADMINS:
            return True
        
        # Fallback to database check
        return await is_admin(session=session, user_id=user_id)
