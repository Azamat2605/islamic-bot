from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import BotCommand, BotCommandScopeDefault

if TYPE_CHECKING:
    from aiogram import Bot

users_commands: dict[str, dict[str, str]] = {
    "en": {
        "help": "help",
        "info": "Information about project",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "support": "Support contacts",
        "supports": "support contacts",
    },
    "uk": {
        "help": "help",
        "info": "Інформація про проект",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "support": "Контакти служби підтримки",
        "supports": "support contacts",
    },
    "ru": {
        "help": "help",
        "info": "Информация о проекте",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "support": "Контакты службы поддержки",
        "supports": "support contacts",
    },
}

admins_commands: dict[str, dict[str, str]] = {
    "en": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
    "uk": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
    "ru": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
}


async def set_default_commands(bot: Bot) -> None:
    await remove_default_commands(bot)

    for language_code, commands in users_commands.items():
        await bot.set_my_commands(
            [BotCommand(command=command, description=description) for command, description in commands.items()],
            scope=BotCommandScopeDefault(),
            language_code=language_code,
        )

        """ Commands for admins
        for admin_id in await admin_ids():
            await bot.set_my_commands(
                [
                    BotCommand(command=command, description=description)
                    for command, description in admins_commands[language_code].items()
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        """


async def remove_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
