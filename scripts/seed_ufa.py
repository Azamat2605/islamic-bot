#!/usr/bin/env python3
"""
Скрипт для заполнения таблицы halal_places данными для Уфы.
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


async def seed_ufa_places(session: AsyncSession) -> None:
    """Добавляем халяль места для Уфы."""
    # Проверяем, есть ли уже записи для Уфы (по координатам)
    from sqlalchemy import select
    result = await session.execute(
        select(HalalPlace).where(HalalPlace.latitude.between(54.7, 54.9))
    )
    existing = result.scalars().all()
    if existing:
        print(f"Найдено {len(existing)} мест в Уфе. Пропускаем seeding.")
        return

    # Данные: места в Уфе
    ufa_places = [
        {
            "place_type": PlaceType.MOSQUE,
            "title": "Мечеть 'Ляля-Тюльпан'",
            "description": "Одна из самых красивых мечетей России, символ Уфы. Построена в форме тюльпана.",
            "address": "ул. Комарова, 5, Уфа, Республика Башкортостан, Россия",
            "latitude": 54.82,
            "longitude": 56.05,
            "working_hours": "05:00-23:00",
            "phone": "+7 347 250-00-00",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.MOSQUE,
            "title": "Первая соборная мечеть Уфы",
            "description": "Старейшая мечеть Уфы, построенная в 1830 году. Исторический памятник.",
            "address": "ул. Тукаева, 52, Уфа, Республика Башкортостан, Россия",
            "latitude": 54.73,
            "longitude": 55.95,
            "working_hours": "05:00-22:00",
            "phone": "+7 347 272-22-11",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.RESTAURANT,
            "title": "Кафе 'Халяль Дуслык'",
            "description": "Уютное кафе с традиционной башкирской и татарской кухней. Все блюда халяль.",
            "address": "ул. Ленина, 42, Уфа, Республика Башкортостан, Россия",
            "latitude": 54.73,
            "longitude": 55.96,
            "working_hours": "10:00-22:00",
            "phone": "+7 347 291-11-22",
            "photo_id": None,
            "is_verified": True,
        },
        {
            "place_type": PlaceType.SHOP,
            "title": "Магазин 'Халяль Продукты'",
            "description": "Продуктовый магазин с широким ассортиментом халяль продуктов: мясо, колбасы, полуфабрикаты.",
            "address": "ул. Революционная, 33, Уфа, Республика Башкортостан, Россия",
            "latitude": 54.74,
            "longitude": 55.97,
            "working_hours": "08:00-21:00",
            "phone": "+7 347 255-55-55",
            "photo_id": None,
            "is_verified": True,
        },
    ]

    for place_data in ufa_places:
        place = HalalPlace(**place_data)
        session.add(place)
        print(f"Добавлено место в Уфе: {place.title}")

    await session.commit()
    print("Seeding данных для Уфы завершен успешно.")


async def main() -> None:
    """Основная асинхронная функция."""
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            await seed_ufa_places(session)
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при seeding: {e}")
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
