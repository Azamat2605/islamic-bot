import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import AsyncSessionLocal
from database.crud import ensure_user

async def test_transaction():
    # Создаём сессию без активной транзакции
    async with AsyncSessionLocal() as session:
        # Начинаем транзакцию вручную, имитируя middleware
        async with session.begin():
            telegram_id = 123456789012345
            username = "testuser"
            full_name = "Test User"
            try:
                user = await ensure_user(session, telegram_id, username, full_name)
                print(f"Пользователь создан: id={user.id}, telegram_id={user.telegram_id}")
                # Пробуем обновить
                user2 = await ensure_user(session, telegram_id, "updateduser", "Updated User")
                print(f"Пользователь обновлён: username={user2.username}")
                # Если не было исключения, значит транзакция работает
                print("Тест пройден: нет ошибки InvalidRequestError")
            except Exception as e:
                print(f"Ошибка: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        # Транзакция коммитится здесь (если не было исключения)
    print("Сессия закрыта")

if __name__ == "__main__":
    asyncio.run(test_transaction())
