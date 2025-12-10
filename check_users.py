"""
Проверка пользователей в базе данных.
"""
import asyncio
from sqlalchemy import select
from database.engine import AsyncSessionLocal
from database.models import User


async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(5))
        users = result.scalars().all()
        
        print(f'Всего пользователей: {len(users)}')
        for u in users:
            print(f'ID: {u.id}, Telegram ID: {u.telegram_id}, Name: {u.full_name}')


if __name__ == "__main__":
    asyncio.run(main())
