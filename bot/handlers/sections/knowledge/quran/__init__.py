"""
Роутер модуля Коран.
"""

from aiogram import Router

quran_router = Router(name="quran")

# Импорт обработчиков
from . import catalog, reading

# Включение подроутеров
quran_router.include_router(catalog.router)
quran_router.include_router(reading.router)
