#!/usr/bin/env python3
"""
Скрипт диагностики данных для модуля "Халяль места".
Проверяет наличие данных в БД, тестирует функцию расчета расстояния.
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from bot.core.config import settings
from bot.database.models.halal import HalalPlace, PlaceType
from bot.services.halal_service import haversine_distance


async def debug_halal_data() -> None:
    """Основная функция диагностики."""
    print("=" * 60)
    print("ДИАГНОСТИКА МОДУЛЯ 'ХАЛЯЛЬ МЕСТА'")
    print("=" * 60)
    
    # Создаем подключение к БД
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 1. Количество записей в таблице halal_places
            stmt = select(func.count(HalalPlace.id))
            result = await session.execute(stmt)
            total_count = result.scalar() or 0
            
            print(f"\n1. Количество записей в таблице halal_places: {total_count}")
            
            # 2. Первые 3 записи
            if total_count > 0:
                stmt = select(HalalPlace).order_by(HalalPlace.id).limit(3)
                result = await session.execute(stmt)
                places = result.scalars().all()
                
                print("\n2. Первые 3 записи:")
                for i, place in enumerate(places, 1):
                    print(f"   {i}. ID: {place.id}")
                    print(f"      Название: {place.title}")
                    print(f"      Тип: {place.place_type.value}")
                    print(f"      Координаты: {place.latitude}, {place.longitude}")
                    print(f"      Адрес: {place.address}")
                    print(f"      Проверено: {place.is_verified}")
                    print()
            else:
                print("\n2. Записей нет - таблица пуста!")
            
            # 3. Статистика по категориям
            print("\n3. Статистика по категориям:")
            for place_type in PlaceType:
                stmt = select(func.count(HalalPlace.id)).where(
                    HalalPlace.place_type == place_type
                )
                result = await session.execute(stmt)
                count = result.scalar() or 0
                print(f"   {place_type.value}: {count} записей")
            
            # 4. Тестирование функции haversine_distance
            print("\n4. Тестирование функции haversine_distance:")
            
            if total_count > 0:
                # Берем первую запись для теста
                stmt = select(HalalPlace).order_by(HalalPlace.id).limit(1)
                result = await session.execute(stmt)
                test_place = result.scalar_one_or_none()
                
                if test_place:
                    lat1, lon1 = test_place.latitude, test_place.longitude
                    
                    # Тест 1: Расстояние от точки до себя самой
                    distance_self = haversine_distance(lat1, lon1, lat1, lon1)
                    print(f"   Тест 1 - Расстояние до себя самой:")
                    print(f"      Координаты: ({lat1}, {lon1})")
                    print(f"      Результат: {distance_self} км (ожидается: 0.0 км)")
                    print(f"      Статус: {'✅ OK' if distance_self == 0.0 else '❌ ОШИБКА'}")
                    
                    # Тест 2: Расстояние до точки со смещением 0.01 градуса
                    lat2 = lat1 + 0.01
                    lon2 = lon1 + 0.01
                    distance_offset = haversine_distance(lat1, lon1, lat2, lon2)
                    print(f"\n   Тест 2 - Расстояние до точки со смещением 0.01 градуса:")
                    print(f"      Исходные координаты: ({lat1}, {lon1})")
                    print(f"      Смещенные координаты: ({lat2}, {lon2})")
                    print(f"      Результат: {distance_offset} км")
                    print(f"      Ожидается: ~1.1-1.4 км (приблизительно)")
                    
                    # Тест 3: Проверка нескольких известных расстояний
                    print(f"\n   Тест 3 - Известные расстояния:")
                    # Москва - Санкт-Петербург (примерно)
                    moscow_lat, moscow_lon = 55.7558, 37.6173
                    spb_lat, spb_lon = 59.9343, 30.3351
                    distance_msk_spb = haversine_distance(moscow_lat, moscow_lon, spb_lat, spb_lon)
                    print(f"      Москва - СПб: {distance_msk_spb} км (ожидается ~634 км)")
            else:
                print("   Невозможно протестировать haversine_distance - нет данных в БД")
                
                # Тест с фиктивными координатами
                print("\n   Тест с фиктивными координатами:")
                lat1, lon1 = 55.7558, 37.6173  # Москва
                lat2, lon2 = 55.7658, 37.6273  # Москва + 0.01 градуса
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                print(f"      Координаты 1: ({lat1}, {lon1})")
                print(f"      Координаты 2: ({lat2}, {lon2})")
                print(f"      Расстояние: {distance} км")
            
            # 5. Проверка структуры данных
            print("\n5. Проверка структуры данных:")
            if total_count > 0:
                stmt = select(HalalPlace).limit(1)
                result = await session.execute(stmt)
                sample = result.scalar_one()
                
                print(f"   Пример структуры записи:")
                print(f"      ID: {sample.id}")
                print(f"      Тип: {sample.place_type} ({type(sample.place_type)})")
                print(f"      Название: {sample.title}")
                print(f"      Широта: {sample.latitude} ({type(sample.latitude)})")
                print(f"      Долгота: {sample.longitude} ({type(sample.longitude)})")
                print(f"      Адрес: {sample.address}")
                print(f"      Время работы: {sample.working_hours}")
                print(f"      Телефон: {sample.phone}")
                print(f"      Проверено: {sample.is_verified}")
            else:
                print("   Нет данных для проверки структуры")
                
        except Exception as e:
            print(f"\n❌ ОШИБКА при выполнении диагностики: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 60)


async def main() -> None:
    """Точка входа."""
    try:
        await debug_halal_data()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
