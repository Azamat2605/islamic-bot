import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import AsyncSessionLocal
from database.crud import get_user_with_settings, ensure_user

async def test_get_user_with_settings():
    async with AsyncSessionLocal() as session:
        # Создаём пользователя для теста
        telegram_id = 987654321012345
        username = "profiletest"
        full_name = "Profile Test"
        user = await ensure_user(session, telegram_id, username, full_name)
        await session.commit()  # коммитим, чтобы данные сохранились
        print(f"Создан пользователь: id={user.id}")

        # Тестируем get_user_with_settings
        user_found, settings_found = await get_user_with_settings(session, telegram_id)
        if user_found is None:
            print("ОШИБКА: Пользователь не найден")
            sys.exit(1)
        if settings_found is None:
            print("ОШИБКА: Настройки не найдены")
            sys.exit(1)
        print(f"Найден пользователь: {user_found.full_name}, настройки языка: {settings_found.language}")
        # Проверяем, что настройки принадлежат пользователю
        assert settings_found.user_id == user_found.id
        print("Тест пройден: get_user_with_settings работает корректно")

        # Тестируем случай, когда пользователь не существует
        user_not_found, settings_not_found = await get_user_with_settings(session, 999999999999999)
        if user_not_found is not None or settings_not_found is not None:
            print("ОШИБКА: Ожидалось (None, None) для несуществующего пользователя")
            sys.exit(1)
        print("Тест пройден: несуществующий пользователь возвращает (None, None)")

        # Очистка (опционально)
        await session.delete(settings_found)
        await session.delete(user_found)
        await session.commit()
        print("Тестовые данные удалены")

if __name__ == "__main__":
    asyncio.run(test_get_user_with_settings())
