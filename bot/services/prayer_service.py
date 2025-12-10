from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from loguru import logger

from bot.core.config import settings


class PrayerService:
    """Сервис для получения времени намазов через API Aladhan.com"""
    
    BASE_URL = "http://api.aladhan.com/v1"
    
    # Маппинг мазхабов на метод расчета (API parameter)
    MADHAB_METHODS = {
        "Hanafi": 1,      # University of Islamic Sciences, Karachi
        "Shafi": 2,       # Islamic Society of North America
        "Maliki": 3,      # Muslim World League
        "Hanbali": 4,     # Umm al-Qura University, Makkah
    }
    
    # Порядок намазов для отображения
    PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    
    @classmethod
    def _get_method_from_madhab(cls, madhab: str) -> int:
        """Получить метод расчета по мазхабу"""
        return cls.MADHAB_METHODS.get(madhab, 1)  # По умолчанию Hanafi
    
    @classmethod
    async def _make_request(cls, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Выполнить HTTP-запрос к API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API error: {response.status} - {await response.text()}")
                        return None
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return None
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    @classmethod
    async def get_today_timings(
        cls, 
        city: str, 
        madhab: str = "Hanafi",
        country: str = "Russia"
    ) -> Optional[Dict[str, Any]]:
        """
        Получить время намазов на сегодня
        
        Args:
            city: Название города (например, "Moscow")
            madhab: Мазхаб (Hanafi, Shafi, Maliki, Hanbali)
            country: Страна (по умолчанию "Russia")
            
        Returns:
            Словарь с данными или None в случае ошибки
        """
        today = date.today()
        method = cls._get_method_from_madhab(madhab)
        
        params = {
            "city": city,
            "country": country,
            "method": method,
            "date": today.isoformat(),
        }
        
        url = f"{cls.BASE_URL}/timingsByCity"
        data = await cls._make_request(url, params)
        
        if not data or "data" not in data:
            return None
        
        return {
            "date": today,
            "city": city,
            "madhab": madhab,
            "timings": data["data"]["timings"],
            "meta": data["data"]["meta"],
        }
    
    @classmethod
    async def get_week_timings(
        cls,
        city: str,
        madhab: str = "Hanafi",
        start_date: Optional[date] = None,
        country: str = "Russia"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Получить время намазов на неделю (7 дней)
        
        Args:
            city: Название города
            madhab: Мазхаб
            start_date: Дата начала (по умолчанию сегодня)
            country: Страна
            
        Returns:
            Список словарей с данными за каждый день или None в случае ошибки
        """
        if start_date is None:
            start_date = date.today()
        
        method = cls._get_method_from_madhab(madhab)
        results = []
        
        # Запрашиваем данные для каждого дня недели
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            
            params = {
                "city": city,
                "country": country,
                "method": method,
                "date": current_date.isoformat(),
            }
            
            url = f"{cls.BASE_URL}/timingsByCity"
            data = await cls._make_request(url, params)
            
            if not data or "data" not in data:
                logger.warning(f"Failed to get data for {current_date}")
                continue
            
            results.append({
                "date": current_date,
                "city": city,
                "madhab": madhab,
                "timings": data["data"]["timings"],
                "meta": data["data"]["meta"],
            })
            
            # Небольшая задержка чтобы не перегружать API
            await asyncio.sleep(0.1)
        
        return results if results else None
    
    @classmethod
    def format_timing_for_display(
        cls, 
        timings: Dict[str, str], 
        prayer_name: str
    ) -> str:
        """Форматировать время для отображения"""
        time_str = timings.get(prayer_name, "N/A")
        if time_str == "N/A":
            return time_str
        
        # Конвертируем "HH:MM" в более читаемый формат
        try:
            dt = datetime.strptime(time_str, "%H:%M")
            return dt.strftime("%H:%M")
        except ValueError:
            return time_str
    
    @classmethod
    def get_prayer_display_name(cls, prayer_key: str) -> str:
        """Получить отображаемое название намаза"""
        names = {
            "Fajr": "Фаджр",
            "Sunrise": "Восход",
            "Dhuhr": "Зухр",
            "Asr": "Аср",
            "Maghrib": "Магриб",
            "Isha": "Иша",
        }
        return names.get(prayer_key, prayer_key)


# Синглтон экземпляр для использования в приложении
prayer_service = PrayerService()
