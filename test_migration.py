import asyncio
import logging
from database.engine import engine
from database.migration import migrate_telegram_id_to_bigint

logging.basicConfig(level=logging.INFO)

async def test_migration():
    try:
        await migrate_telegram_id_to_bigint(engine)
        print("Миграция выполнена успешно")
    except Exception as e:
        print(f"Ошибка миграции: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_migration())
