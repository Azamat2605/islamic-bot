"""
Миграция для изменения типа столбцов telegram_id и user_id на BIGINT.
"""
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def migrate_telegram_id_to_bigint(engine: AsyncEngine) -> None:
    """
    Выполняет ALTER TABLE для изменения типа столбцов:
    - users.telegram_id -> BIGINT
    - settings.user_id -> BIGINT
    """
    # SQL-запросы для PostgreSQL
    alter_users = """
        ALTER TABLE users 
        ALTER COLUMN telegram_id TYPE BIGINT;
    """
    alter_settings = """
        ALTER TABLE settings 
        ALTER COLUMN user_id TYPE BIGINT;
    """
    
    async with engine.begin() as conn:
        try:
            # Проверяем существование таблиц
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            users_exists = result.scalar()
            if not users_exists:
                logger.info("Таблица users не существует, пропускаем миграцию.")
                return

            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'settings')")
            )
            settings_exists = result.scalar()
            if not settings_exists:
                logger.info("Таблица settings не существует, пропускаем миграцию.")
                return

            # Проверяем текущий тип столбца telegram_id
            result = await conn.execute(
                text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'telegram_id'
                """)
            )
            row = result.fetchone()
            if row and row[0] != 'bigint':
                logger.info("Изменяем тип столбца users.telegram_id на BIGINT...")
                await conn.execute(text(alter_users))
                logger.info("Столбец users.telegram_id успешно изменён на BIGINT.")
            else:
                logger.info("Столбец users.telegram_id уже имеет тип BIGINT.")

            # Проверяем текущий тип столбца user_id в settings
            result = await conn.execute(
                text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'settings' AND column_name = 'user_id'
                """)
            )
            row = result.fetchone()
            if row and row[0] != 'bigint':
                logger.info("Изменяем тип столбца settings.user_id на BIGINT...")
                await conn.execute(text(alter_settings))
                logger.info("Столбец settings.user_id успешно изменён на BIGINT.")
            else:
                logger.info("Столбец settings.user_id уже имеет тип BIGINT.")

        except Exception as e:
            logger.error(f"Ошибка при выполнении миграции: {e}")
            raise
