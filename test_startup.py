import asyncio
import logging
from bot.__main__ import on_startup
from database.engine import engine

logging.basicConfig(level=logging.INFO)

async def test():
    try:
        await on_startup()
        print("on_startup выполнен успешно")
    except Exception as e:
        print(f"Ошибка в on_startup: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
