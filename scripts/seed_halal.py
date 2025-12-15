#!/usr/bin/env python3
"""
Скрипт для заполнения таблицы halal_places тестовыми данными.
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bot.core.config import settings
from bot.database.models.halal import HalalPlace, PlaceType


async def seed_halal_places(session: AsyncSession) -> None:
    """Добавляем тестовые халяль места."""
    # Проверяем, есть ли уже записи
    from sqlalchemy import select
    result = await session.execute(select(HalalPlace).limit(1))
    existing = result.scalar_one_or_none()
    if existing:
        print("Таблица halal_places уже содержит данные. Пропускаем seeding.")
        return

    # Тестовые данные: места в Москве
    test_places = [
        {
            "place_type": PlaceType.MOSQUE,
            "title": "Московская Соборная Мечеть",
            "description": "Главная мечеть Москвы, одна из крупнейших в Европе.",
            "address": "Выползов пер., 7, Москва, Россия",
            "latitude": 55.775,
            "longitude": 37.632,
            "working_hours": "05:00-23:00",
            "phone": "+7 495 681-49-04",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.MOSQUE,
            "title": "Мечеть 'Ярдям'",
            "description": "Мечеть в Отрадном, одна из крупнейших в Москве.",
            "address": "ул. Хачатуряна, 8, Москва, Россия",
            "latitude": 55.863,
            "longitude": 37.603,
            "working_hours": "05:00-22:00",
            "phone": "+7 499 202-45-45",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.RESTAURANT,
            "title": "Ресторан 'Ан-Noor'",
            "description": "Халяль ресторан с восточной кухней.",
            "address": "ул. Тверская, 12, Москва, Россия",
            "latitude": 55.761,
            "longitude": 37.608,
            "working_hours": "10:00-23:00",
            "phone": "+7 495 123-45-67",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.RESTAURANT,
            "title": "Кафе 'Halal Food'",
            "description": "Бюджетное кафе с халяль едой.",
            "address": "ул. Арбат, 25, Москва, Россия",
            "latitude": 55.749,
            "longitude": 37.591,
            "working_hours": "09:00-22:00",
            "phone": "+7 495 987-65-43",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.SHOP,
            "title": "Магазин 'Halal Market'",
            "description": "Продуктовый магазин с халяль продуктами.",
            "address": "ул. Профсоюзная, 102, Москва, Россия",
            "latitude": 55.642,
            "longitude": 37.526,
            "working_hours": "08:00-21:00",
            "phone": "+7 495 555-12-34",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.CLOTHES,
            "title": "Магазин 'Islamic Clothing'",
            "description": "Магазин мусульманской одежды.",
            "address": "ул. Покровка, 31, Москва, Россия",
            "latitude": 55.760,
            "longitude": 37.648,
            "working_hours": "10:00-20:00",
            "phone": "+7 495 777-88-99",
            "photo_id": None,
            "is_verified": True,
        },
    ]

    for place_data in test_places:
        place = HalalPlace(**place_data)
        session.add(place)
        print(f"Добавлено место: {place.title}")

    await session.commit()
    print("Seeding завершен успешно.")


async def main() -> None:
    """Основная асинхронная функция."""
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            await seed_halal_places(session)
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при seeding: {e}")
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
