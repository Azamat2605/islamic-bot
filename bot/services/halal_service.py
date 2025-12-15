"""
Сервис для работы с халяль местами.
"""
import math
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from bot.database.models.halal import HalalPlace, PlaceType


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Вычисляет расстояние между двумя точками на Земле (в км)
    используя формулу гаверсинуса.
    """
    R = 6371.0  # Радиус Земли в километрах
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)  # Округляем до 2 знаков после запятой


class HalalService:
    """Сервис для работы с халяль местами."""
    
    @staticmethod
    async def get_nearby_places(
        latitude: float,
        longitude: float,
        session: AsyncSession,
        limit: int = 5,
        radius_km: float = 10.0
    ) -> List[Dict]:
        """
        Получить ближайшие места в радиусе radius_km.
        """
        # Получаем все места из БД
        stmt = select(HalalPlace)
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        # Вычисляем расстояние и фильтруем
        nearby_places = []
        for place in places:
            distance = haversine_distance(latitude, longitude, place.latitude, place.longitude)
            if distance <= radius_km:
                place_dict = {
                    "id": place.id,
                    "title": place.title,
                    "place_type": place.place_type.value,
                    "address": place.address,
                    "distance": distance,
                    "working_hours": place.working_hours,
                    "phone": place.phone,
                    "is_verified": place.is_verified
                }
                nearby_places.append(place_dict)
        
        # Сортируем по расстоянию
        nearby_places.sort(key=lambda x: x["distance"])
        
        return nearby_places[:limit]
    
    @staticmethod
    async def get_places_by_category(
        category: str,
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict]:
        """
        Получить места по категории.
        """
        # Защита от None
        if not category:
            return []
        
        # Преобразуем строку в значение enum PlaceType
        try:
            # Пытаемся найти соответствующий enum по значению
            place_type_enum = None
            for pt in PlaceType:
                if pt.value == category:
                    place_type_enum = pt
                    break
            
            if place_type_enum is None:
                # Если не нашли по значению, пробуем по имени
                place_type_enum = PlaceType[category.upper()]
        except (KeyError, ValueError):
            # Если категория не найдена, возвращаем пустой список
            return []
        
        stmt = select(HalalPlace).where(
            HalalPlace.place_type == place_type_enum
        ).order_by(HalalPlace.title).limit(limit)
        
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        return [
            {
                "id": place.id,
                "title": place.title,
                "address": place.address,
                "working_hours": place.working_hours,
                "phone": place.phone,
                "is_verified": place.is_verified
            }
            for place in places
        ]
    
    @staticmethod
    async def get_place_details(
        place_id: int,
        session: AsyncSession
    ) -> Optional[Dict]:
        """
        Получить детальную информацию о месте.
        """
        stmt = select(HalalPlace).where(HalalPlace.id == place_id)
        result = await session.execute(stmt)
        place = result.scalar_one_or_none()
        
        if not place:
            return None
        
        return {
            "id": place.id,
            "title": place.title,
            "place_type": place.place_type.value,
            "description": place.description,
            "address": place.address,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "working_hours": place.working_hours,
            "phone": place.phone,
            "photo_id": place.photo_id,
            "is_verified": place.is_verified,
            "created_at": place.created_at
        }
    
    @staticmethod
    async def get_counts_by_category(
        session: AsyncSession
    ) -> Dict[str, int]:
        """
        Получить статистику по категориям для главного экрана.
        """
        counts = {}
        for place_type in PlaceType:
            stmt = select(func.count(HalalPlace.id)).where(
                HalalPlace.place_type == place_type
            )
            result = await session.execute(stmt)
            count = result.scalar() or 0
            counts[place_type.value] = count
        
        return counts
    
    @staticmethod
    async def search_places(
        query: str,
        session: AsyncSession,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Поиск мест по названию или адресу.
        """
        stmt = select(HalalPlace).where(
            HalalPlace.title.ilike(f"%{query}%") |
            HalalPlace.address.ilike(f"%{query}%")
        )
        
        if category:
            # Защита от пустой категории
            if not category:
                # Если category пустой, просто игнорируем фильтрацию по категории
                pass
            else:
                # Преобразуем строку в значение enum PlaceType
                try:
                    # Пытаемся найти соответствующий enum по значению
                    place_type_enum = None
                    for pt in PlaceType:
                        if pt.value == category:
                            place_type_enum = pt
                            break
                    
                    if place_type_enum is None:
                        # Если не нашли по значению, пробуем по имени
                        place_type_enum = PlaceType[category.upper()]
                except (KeyError, ValueError):
                    # Если категория не найдена, возвращаем пустой список
                    return []
                
                stmt = stmt.where(HalalPlace.place_type == place_type_enum)
        
        stmt = stmt.order_by(HalalPlace.title).limit(limit)
        
        result = await session.execute(stmt)
        places = result.scalars().all()
        
        return [
            {
                "id": place.id,
                "title": place.title,
                "address": place.address,
                "place_type": place.place_type.value,
                "working_hours": place.working_hours
            }
            for place in places
        ]
