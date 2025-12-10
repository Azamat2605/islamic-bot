"""
Тестирование функциональности мероприятий.
"""
import asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import AsyncSessionLocal
from database.models import CommunityEvent, EventType, EventStatus
from bot.services.event_service import EventService


async def test_event_creation():
    """Тестирование создания мероприятия."""
    async with AsyncSessionLocal() as session:
        # Создаём тестовое мероприятие
        success, event, message = await EventService.create_event(
            session=session,
            title="Тестовое мероприятие",
            start_time=datetime.datetime.now() + datetime.timedelta(days=1),
            created_by=1,  # ID пользователя (админа)
            description="Это тестовое мероприятие для проверки функциональности",
            location="Онлайн",
            event_type=EventType.LECTURE,
            max_participants=10
        )
        
        if success:
            print(f"✅ Мероприятие создано: {event.title} (ID: {event.id})")
            print(f"Сообщение: {message}")
            
            # Получаем список мероприятий
            events = await EventService.get_upcoming_events(session, limit=5)
            print(f"\n📋 Всего предстоящих мероприятий: {len(events)}")
            for e in events:
                print(f"  - {e.title} ({e.start_time})")
        else:
            print(f"❌ Ошибка создания мероприятия: {message}")


async def test_event_registration():
    """Тестирование регистрации на мероприятие."""
    async with AsyncSessionLocal() as session:
        # Получаем первое мероприятие
        events = await EventService.get_upcoming_events(session, limit=1)
        if not events:
            print("❌ Нет мероприятий для тестирования регистрации")
            return
        
        event = events[0]
        user_id = 1  # Используем существующего пользователя (ID из таблицы users)
        
        # Регистрируем пользователя
        success, message = await EventService.register_for_event(session, user_id, event.id)
        
        if success:
            print(f"✅ Регистрация успешна: {message}")
            
            # Проверяем регистрации пользователя
            registrations = await EventService.get_user_registrations(session, user_id)
            print(f"📝 У пользователя {user_id} регистраций: {len(registrations)}")
            for reg in registrations:
                print(f"  - Мероприятие: {reg.event.title}, Статус: {reg.status.value}")
        else:
            print(f"❌ Ошибка регистрации: {message}")


async def main():
    """Основная функция тестирования."""
    print("🧪 Тестирование функциональности мероприятий")
    print("=" * 50)
    
    await test_event_creation()
    print("\n" + "=" * 50)
    await test_event_registration()


if __name__ == "__main__":
    asyncio.run(main())
