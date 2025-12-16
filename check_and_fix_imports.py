#!/usr/bin/env python3
"""
Скрипт для проверки и исправления импортов show_main_menu в обработчиках.
"""
import os
import re
from pathlib import Path

# Файлы, которые нужно проверить
FILES_TO_CHECK = [
    "bot/handlers/sections/prayer_schedule_handlers.py",
    "bot/handlers/sections/halal_places_handlers.py",
    "bot/handlers/sections/events_calendar_handlers.py",
    "bot/handlers/sections/ai_assistant.py",
]

# Регулярное выражение для поиска импортов
IMPORT_PATTERN = r'^from\s+bot\.handlers\.common\.show_main_menu\s+import\s+show_main_menu'
IMPORT_PATTERN2 = r'^import\s+bot\.handlers\.common\.show_main_menu'

def check_file(file_path):
    """Проверить файл на наличие импорта show_main_menu."""
    if not os.path.exists(file_path):
        print(f"Файл не существует: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие импорта
    if re.search(IMPORT_PATTERN, content, re.MULTILINE) or re.search(IMPORT_PATTERN2, content, re.MULTILINE):
        print(f"✓ Импорт уже есть в {file_path}")
        return True
    else:
        print(f"✗ Импорт отсутствует в {file_path}")
        return False

def add_import(file_path):
    """Добавить импорт show_main_menu в файл."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Находим строку с импортами aiogram
    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('from aiogram') or line.strip().startswith('import aiogram'):
            insert_index = i
            break
    
    # Добавляем импорт после импортов aiogram
    lines.insert(insert_index + 1, 'from bot.handlers.common.show_main_menu import show_main_menu\n')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✓ Добавлен импорт в {file_path}")

def main():
    print("Проверка импортов show_main_menu...")
    
    for file_path in FILES_TO_CHECK:
        if not check_file(file_path):
            add_import(file_path)

if __name__ == "__main__":
    main()
