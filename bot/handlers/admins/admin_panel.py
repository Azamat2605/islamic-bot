from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from bot.services.stats_service import StatsService

router = Router(name="admin_panel")


@router.message(Command("admin"), AdminFilter())
async def admin_command_handler(message: types.Message, session: AsyncSession) -> None:
    """Handle /admin command for administrators."""
    stats = await StatsService.get_all_stats(session)
    
    text = (
        "📊 <b>Statistics</b>\n\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"🆕 New Today: <b>{stats['users_today']}</b>\n"
        f"🌍 Languages: <b>{stats['languages']}</b>\n"
    )
    
    await message.answer(text, parse_mode="HTML")
