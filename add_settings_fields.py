import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.engine import AsyncSessionLocal
from sqlalchemy import text


async def add_settings_fields():
    """Добавляет новые поля в таблицу settings если они не существуют."""
    async with AsyncSessionLocal() as session:
        try:
            # Проверяем существование каждого поля и добавляем если нет
            fields_to_add = [
                ("timezone", "VARCHAR DEFAULT 'Europe/Moscow' NOT NULL"),
                ("date_format", "VARCHAR DEFAULT 'DD.MM.YYYY' NOT NULL"),
                ("time_format", "BOOLEAN DEFAULT true NOT NULL"),
                ("prayer_notifications_on", "BOOLEAN DEFAULT true NOT NULL"),
                ("event_notifications_on", "BOOLEAN DEFAULT true NOT NULL"),
                ("data_export_requested", "BOOLEAN DEFAULT false NOT NULL"),
                ("account_deletion_requested", "BOOLEAN DEFAULT false NOT NULL"),
                ("created_at", "TIMESTAMP DEFAULT TIMEZONE('utc', now()) NOT NULL"),
                ("updated_at", "TIMESTAMP DEFAULT TIMEZONE('utc', now()) NOT NULL"),
            ]
            
            for field_name, field_type in fields_to_add:
                # Проверяем существует ли поле
                check_query = f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'settings' AND column_name = '{field_name}'
                """
                result = await session.execute(text(check_query))
                exists = result.scalar() is not None
                
                if not exists:
                    print(f"Добавляем поле {field_name}...")
                    alter_query = f"ALTER TABLE settings ADD COLUMN {field_name} {field_type}"
                    await session.execute(text(alter_query))
                    print(f"Поле {field_name} добавлено.")
                else:
                    print(f"Поле {field_name} уже существует.")
            
            await session.commit()
            print("Все поля успешно добавлены в таблицу settings.")
            
        except Exception as e:
            await session.rollback()
            print(f"Ошибка: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(add_settings_fields())
