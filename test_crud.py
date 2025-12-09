import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import AsyncSessionLocal
from database.crud import ensure_user, get_user_language, set_user_language

async def test_crud():
    async with AsyncSessionLocal() as session:
        # Создаём пользователя с большим telegram_id (имитация реального Telegram ID)
        telegram_id = 123456789012345  # Большое число, которое может вызвать переполнение INT
        username = "testuser"
        full_name = "Test User"
        
        try:
            user = await ensure_user(session, telegram_id, username, full_name)
            print(f"Пользователь создан: id={user.id}, telegram_id={user.telegram_id}")
            
            # Проверяем язык
            language = await get_user_language(session, user.id)
            print(f"Язык пользователя: {language}")
            
            # Меняем язык
            await set_user_language(session, user.id, "en")
            language = await get_user_language(session, user.id)
            print(f"Язык после изменения: {language}")
            
            # Пробуем получить того же пользователя снова
            user2 = await ensure_user(session, telegram_id, "updateduser", "Updated User")
            print(f"Пользователь обновлён: username={user2.username}")
            
            print("Все CRUD операции прошли успешно")
            
        except Exception as e:
            print(f"Ошибка CRUD: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_crud())
