"""
Исправление CHECK constraints для поддержки значений в верхнем регистре.
"""
import asyncio
from sqlalchemy import text
from database.engine import AsyncSessionLocal


async def fix_constraints():
    """Исправляет CHECK constraints для поддержки значений в верхнем регистре."""
    async with AsyncSessionLocal() as session:
        try:
            # 1. Удаляем старые constraints
            await session.execute(text("""
                ALTER TABLE community_events 
                DROP CONSTRAINT IF EXISTS community_events_event_type_check
            """))
            
            await session.execute(text("""
                ALTER TABLE community_events 
                DROP CONSTRAINT IF EXISTS community_events_status_check
            """))
            
            await session.execute(text("""
                ALTER TABLE event_registrations 
                DROP CONSTRAINT IF EXISTS event_registrations_status_check
            """))
            
            await session.execute(text("""
                ALTER TABLE event_proposals 
                DROP CONSTRAINT IF EXISTS event_proposals_status_check
            """))
            
            # 2. Создаём новые constraints, которые принимают значения в верхнем и нижнем регистре
            await session.execute(text("""
                ALTER TABLE community_events 
                ADD CONSTRAINT community_events_event_type_check 
                CHECK (event_type IN ('lecture', 'meeting', 'course', 'other', 'LECTURE', 'MEETING', 'COURSE', 'OTHER'))
            """))
            
            await session.execute(text("""
                ALTER TABLE community_events 
                ADD CONSTRAINT community_events_status_check 
                CHECK (status IN ('active', 'cancelled', 'finished', 'ACTIVE', 'CANCELLED', 'FINISHED'))
            """))
            
            await session.execute(text("""
                ALTER TABLE event_registrations 
                ADD CONSTRAINT event_registrations_status_check 
                CHECK (status IN ('confirmed', 'cancelled', 'waiting', 'CONFIRMED', 'CANCELLED', 'WAITING'))
            """))
            
            await session.execute(text("""
                ALTER TABLE event_proposals 
                ADD CONSTRAINT event_proposals_status_check 
                CHECK (status IN ('pending', 'approved', 'rejected', 'PENDING', 'APPROVED', 'REJECTED'))
            """))
            
            await session.commit()
            print("✅ CHECK constraints успешно обновлены для поддержки верхнего регистра")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка обновления constraints: {e}")
            raise


async def main():
    """Основная функция."""
    print("🛠️ Исправление CHECK constraints для enum значений")
    print("=" * 50)
    await fix_constraints()


if __name__ == "__main__":
    asyncio.run(main())
