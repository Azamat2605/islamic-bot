import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import AsyncSessionLocal
from database.crud import ensure_user, get_user_with_settings

async def test_ensure_user_update():
    async with AsyncSessionLocal() as session:
        telegram_id = 777888999000111
        # Создаём пользователя
        user1 = await ensure_user(session, telegram_id, "oldusername", "Old Name")
        await session.commit()
        print(f"Создан пользователь: {user1.full_name}, username: {user1.username}")

        # Пробуем ensure_user с новыми данными (username изменился, full_name тоже)
        user2 = await ensure_user(session, telegram_id, "newusername", "New Name")
        # ensure_user должен вернуть того же пользователя с обновлёнными полями
        if user2.id != user1.id:
            print("ОШИБКА: Вернулся другой пользователь")
            sys.exit(1)
        if user2.username != "newusername":
            print(f"ОШИБКА: username не обновился, ожидалось newusername, получил {user2.username}")
            sys.exit(1)
        if user2.full_name != "New Name":
            print(f"ОШИБКА: full_name не обновился, ожидалось New Name, получил {user2.full_name}")
            sys.exit(1)
        print("Пользователь успешно обновлён")

        # Проверяем через get_user_with_settings
        user_db, settings_db = await get_user_with_settings(session, telegram_id)
        if user_db.username != "newusername":
            print("ОШИБКА: get_user_with_settings не вернул обновлённые данные")
            sys.exit(1)
        print("get_user_with_settings возвращает актуальные данные")

        # Очистка
        await session.delete(settings_db)
        await session.delete(user_db)
        await session.commit()
        print("Тестовые данные удалены")

if __name__ == "__main__":
    asyncio.run(test_ensure_user_update())
