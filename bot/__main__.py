from __future__ import annotations
import asyncio

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.loguru import LoggingLevels, LoguruIntegration

from bot.core.config import settings
from bot.core.loader import app, bot, dp
from bot.services.scheduler import setup_scheduler, start_scheduler, stop_scheduler, set_bot_instance
from bot.handlers import get_handlers_router
from bot.handlers.metrics import MetricsView
from bot.keyboards.default_commands import remove_default_commands, set_default_commands
from bot.middlewares import register_middlewares
from bot.middlewares.prometheus import prometheus_middleware_factory
from database.engine import engine
from database.base import Base
from database.migration import migrate_telegram_id_to_bigint


async def on_startup() -> None:
    logger.info("bot starting...")

    register_middlewares(dp)

    dp.include_router(get_handlers_router())

    if settings.USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())
        app.router.add_route("GET", "/metrics", MetricsView)

    # Миграция: изменение типа столбцов на BIGINT
    try:
        await migrate_telegram_id_to_bigint(engine)
        logger.info("Миграция типов столбцов завершена")
    except Exception as e:
        logger.error(f"Миграция не удалась: {e}")
        logger.warning("Продолжаем без миграции")

    # Инициализация базы данных: создание таблиц
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (if not exist)")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Bot will continue without database")

    # Устанавливаем экземпляр бота в планировщике
    set_bot_instance(bot)
    
    # Настройка и запуск планировщика уведомлений о намазах
    try:
        setup_scheduler()
        start_scheduler()
        logger.info("Планировщик уведомлений запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {e}")
        logger.warning("Бот будет работать без уведомлений о намазах")

    await set_default_commands(bot)

    bot_info = await bot.get_me()

    logger.info(f"Name     - {bot_info.full_name}")
    logger.info(f"Username - @{bot_info.username}")
    logger.info(f"ID       - {bot_info.id}")

    states: dict[bool | None, str] = {
        True: "Enabled",
        False: "Disabled",
        None: "Unknown (This's not a bot)",
    }

    logger.info(f"Groups Mode  - {states[bot_info.can_join_groups]}")
    logger.info(f"Privacy Mode - {states[not bot_info.can_read_all_group_messages]}")
    logger.info(f"Inline Mode  - {states[bot_info.supports_inline_queries]}")

    logger.info("bot started")


async def on_shutdown() -> None:
    logger.info("bot stopping...")

    await remove_default_commands(bot)

    await dp.storage.close()
    await dp.fsm.storage.close()

    await bot.delete_webhook()
    await bot.session.close()

    # Остановка планировщика уведомлений
    try:
        stop_scheduler()
        logger.info("Планировщик уведомлений остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки планировщика: {e}")

    # Закрытие пула соединений базы данных
    await engine.dispose()
    logger.info("Database connection pool closed")

    logger.info("bot stopped")


async def setup_webhook() -> None:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application  # noqa: PLC0415
    from aiohttp.web import AppRunner, TCPSite  # noqa: PLC0415

    await bot.set_webhook(
        settings.webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=settings.WEBHOOK_SECRET,
    )

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host=settings.WEBHOOK_HOST, port=settings.WEBHOOK_PORT)
    await site.start()

    await asyncio.Event().wait()


async def main() -> None:
    if settings.SENTRY_DSN:
        sentry_loguru = LoguruIntegration(
            level=LoggingLevels.INFO.value,
            event_level=LoggingLevels.INFO.value,
        )
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[sentry_loguru],
        )

    logger.add(
        "logs/telegram_bot.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="100 KB",
        compression="zip",
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if settings.USE_WEBHOOK:
        await setup_webhook()
    else:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
