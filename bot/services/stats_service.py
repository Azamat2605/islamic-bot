from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Settings


class StatsService:
    """Service for retrieving bot statistics."""

    @staticmethod
    async def get_total_users(session: AsyncSession) -> int:
        """Get total number of users."""
        stmt = select(func.count(User.id))
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_users_today(session: AsyncSession) -> int:
        """Get number of users registered today."""
        today = date.today()
        stmt = select(func.count(User.id)).where(func.date(User.created_at) == today)
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_languages_stats(session: AsyncSession) -> str:
        """Get language distribution summary."""
        stmt = (
            select(Settings.language, func.count(Settings.id))
            .group_by(Settings.language)
            .order_by(func.count(Settings.id).desc())
        )
        result = await session.execute(stmt)
        rows = result.all()
        if not rows:
            return "No data"
        parts = [f"{lang}: {count}" for lang, count in rows]
        return ", ".join(parts)

    @classmethod
    async def get_all_stats(cls, session: AsyncSession) -> dict:
        """Get all statistics in a dict."""
        total = await cls.get_total_users(session)
        today = await cls.get_users_today(session)
        languages = await cls.get_languages_stats(session)
        return {
            "total_users": total,
            "users_today": today,
            "languages": languages,
        }
