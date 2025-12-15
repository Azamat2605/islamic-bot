#!/usr/bin/env python3
"""
Тестирование логики модуля Halal Places.
Проверяем, почему списки могут быть пустыми.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bot.core.config import settings
from bot.services.halal_service import HalalService


async def test_halal_logic() -> None:
    """Тестируем логику получения мест."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЛОГИКИ HALAL SERVICE")
    print("=" * 60)
    
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 1. Тест получения мест по категории
            print("\n1. Тест получения мест по категории 'mosque':")
            mosques = await HalalService.get_places_by_category(
                category="mosque",
                session=session,
                limit=10
            )
            print(f"   Найдено мечетей: {len(mosques)}")
            for i, mosque in enumerate(mosques, 1):
                print(f"   {i}. {mosque['title']} (ID: {mosque['id']})")
            
            # 2. Тест получения ближайших мест (координаты Москвы)
            print("\n2. Тест получения ближайших мест (координаты Москвы):")
            moscow_lat, moscow_lon = 55.7558, 37.6173
            nearby = await HalalService.get_nearby_places(
                latitude=moscow_lat,
                longitude=moscow_lon,
                session=session,
                limit=5,
                radius_km=50.0  # Большой радиус, чтобы точно найти
            )
            print(f"   Найдено ближайших мест (радиус 50 км): {len(nearby)}")
            for i, place in enumerate(nearby, 1):
                print(f"   {i}. {place['title']} - {place['distance']} км")
            
            # 3. Тест с маленьким радиусом (должен быть пустым)
            print("\n3. Тест с маленьким радиусом (0.1 км):")
            nearby_small = await HalalService.get_nearby_places(
                latitude=moscow_lat,
                longitude=moscow_lon,
                session=session,
                limit=5,
                radius_km=0.1
            )
            print(f"   Найдено ближайших мест (радиус 0.1 км): {len(nearby_small)}")
            if not nearby_small:
                print("   Ожидаемо: нет мест в таком маленьком радиусе")
            
            # 4. Тест статистики
            print("\n4. Тест статистики по категориям:")
            counts = await HalalService.get_counts_by_category(session)
            for category, count in counts.items():
                print(f"   {category}: {count}")
            
            # 5. Тест деталей места
            print("\n5. Тест получения деталей места (ID: 1):")
            place_details = await HalalService.get_place_details(1, session)
            if place_details:
                print(f"   Название: {place_details['title']}")
                print(f"   Координаты: {place_details['latitude']}, {place_details['longitude']}")
                print(f"   Тип: {place_details['place_type']}")
            else:
                print("   Место не найдено!")
                
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


async def main() -> None:
    await test_halal_logic()


if __name__ == "__main__":
    asyncio.run(main())
