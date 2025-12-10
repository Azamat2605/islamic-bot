"""
Тестирование обработчика текстового сообщения "Календарь событий".
"""
import asyncio
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command
from bot.handlers.sections.events_calendar_handlers import router
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

# Создаём минимальный диспетчер для теста
dp = Dispatcher()
dp.include_router(router)

# Создаём фиктивный бот
class MockBot:
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        print(f"📨 Отправлено сообщение в чат {chat_id}:")
        print(f"   Текст: {text}")
        print(f"   Parse mode: {parse_mode}")
        if reply_markup:
            print(f"   Клавиатура: {reply_markup}")
        return True

async def test_text_handler():
    """Тестируем обработчик текстового сообщения."""
    bot = MockBot()
    
    # Создаём фиктивное сообщение
    message = Message(
        message_id=1,
        date=None,
        chat=None,
        text="Календарь событий",
        from_user=None
    )
    
    # Вызываем обработчик
    await dp.feed_update(bot, message)
    
    print("\n✅ Тест завершён. Если выше нет ошибок, обработчик работает корректно.")

if __name__ == "__main__":
    asyncio.run(test_text_handler())
