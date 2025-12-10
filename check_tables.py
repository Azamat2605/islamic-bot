import asyncio
from database.engine import AsyncSessionLocal
from sqlalchemy import text

async def check_tables():
    async with AsyncSessionLocal() as session:
        # Check if community_events table exists
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'community_events'
            );
        """))
        exists = result.scalar()
        print(f'community_events exists: {exists}')
        
        # Check if event_registrations table exists
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'event_registrations'
            );
        """))
        exists = result.scalar()
        print(f'event_registrations exists: {exists}')
        
        # Check if event_proposals table exists
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'event_proposals'
            );
        """))
        exists = result.scalar()
        print(f'event_proposals exists: {exists}')

asyncio.run(check_tables())
