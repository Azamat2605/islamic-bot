import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import AsyncSessionLocal
from database.crud import get_user_with_settings, ensure_user
from bot.handlers.sections.profile_handlers import profile_command_handler
from aiogram.types import Message, User as TgUser
from unittest.mock import AsyncMock

async def test_profile_auto_create():
    async with AsyncSessionLocal() as session:
        # Удаляем тестового пользователя, если он существует
        telegram_id = 111222333444555
        user, settings = await get_user_with_settings(session, telegram_id)
        if user:
            await session.delete(settings)
            await session.delete(user)
            await session.commit()
            print("Удалён существующий тестовый пользователь")

        # Создаём mock message
        mock_message = AsyncMock(spec=Message)
        mock_message.from_user = AsyncMock(spec=TgUser)
        mock_message.from_user.id = telegram_id
        mock_message.from_user.username = "testprofile"
        mock_message.from_user.full_name = "Test Profile"
        mock_message.answer = AsyncMock()

        # Вызываем хэндлер
        try:
            await profile_command_handler(mock_message, session)
        except Exception as e:
            print(f"Ошибка в хэндлере: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Проверяем, что пользователь создан
        user, settings = await get_user_with_settings(session, telegram_id)
        if user is None:
            print("ОШИБКА: Пользователь не создан")
            sys.exit(1)
        print(f"Пользователь создан: {user.full_name}")

        # Проверяем, что message.answer был вызван
        if mock_message.answer.called:
            print("Хэндлер отправил сообщение с профилем (успех)")
        else:
            print("ОШИБКА: Хэндлер не отправил сообщение")
            sys.exit(1)

        # Очистка
        await session.delete(settings)
        await session.delete(user)
        await session.commit()
        print("Тестовые данные удалены")

if __name__ == "__main__":
    asyncio.run(test_profile_auto_create())
