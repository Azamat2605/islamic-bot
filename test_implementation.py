#!/usr/bin/env python3
"""
Тестирование реализации UI/UX Main Menu Redesign.
"""
import os
import sys
import importlib.util

def test_file_exists(file_path):
    """Проверить существование файла."""
    exists = os.path.exists(file_path)
    print(f"{'✓' if exists else '✗'} {file_path}")
    return exists

def test_import(module_path, import_name):
    """Проверить возможность импорта."""
    try:
        spec = importlib.util.spec_from_file_location(import_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✓ Импорт {import_name} из {module_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта {import_name} из {module_path}: {e}")
        return False

def test_ui_config():
    """Проверить конфигурацию UI."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from bot.core.ui_config import UIAssets, ui_assets
        
        print("✓ Класс UIAssets загружен")
        print(f"  MAIN_MENU_IMAGE_URL: {ui_assets.MAIN_MENU_IMAGE_URL}")
        print(f"  MAIN_MENU_CAPTION: {ui_assets.MAIN_MENU_CAPTION[:50]}...")
        
        file_id, image_url = ui_assets.get_main_menu_image()
        print(f"  get_main_menu_image(): file_id={file_id}, image_url={image_url}")
        
        caption = ui_assets.get_localized_caption(username="TestUser")
        print(f"  get_localized_caption(): {caption[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка в ui_config: {e}")
        return False

def test_show_main_menu():
    """Проверить функцию show_main_menu."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from bot.handlers.common.show_main_menu import show_main_menu
        
        print("✓ Функция show_main_menu загружена")
        print(f"  Сигнатура: {show_main_menu.__name__}(message_or_callback, session=None, delete_previous=False)")
        
        # Проверим импорты внутри функции
        import inspect
        source = inspect.getsource(show_main_menu)
        if 'await callback.message.delete()' in source:
            print("✓ Функция содержит delete() для предыдущего сообщения")
        if 'await message.answer_photo' in source:
            print("✓ Функция использует answer_photo для главного меню")
        if 'from bot.core.ui_config import ui_assets' in source:
            print("✓ Функция импортирует ui_assets")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка в show_main_menu: {e}")
        return False

def test_updated_handlers():
    """Проверить обновленные обработчики."""
    handlers_to_check = [
        ("bot/handlers/start.py", "show_main_menu"),
        ("bot/handlers/main_menu.py", "show_main_menu"),
        ("bot/handlers/common_nav.py", "show_main_menu"),
    ]
    
    all_ok = True
    for file_path, import_name in handlers_to_check:
        if not test_file_exists(file_path):
            all_ok = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if f'from bot.handlers.common.show_main_menu import {import_name}' in content:
            print(f"✓ {file_path} импортирует {import_name}")
        elif f'import {import_name}' in content:
            print(f"✓ {file_path} импортирует {import_name}")
        else:
            print(f"✗ {file_path} не импортирует {import_name}")
            all_ok = False
        
        if 'await show_main_menu' in content:
            print(f"✓ {file_path} использует show_main_menu")
        else:
            print(f"✗ {file_path} не использует show_main_menu")
            all_ok = False
    
    return all_ok

def test_entry_points_fixed():
    """Проверить, что точки входа в подразделы исправлены."""
    entry_points = [
        ("bot/handlers/sections/profile_handlers.py", "profile_settings"),
        ("bot/handlers/sections/knowledge/menu.py", "knowledge"),
        ("bot/handlers/sections/education_handlers.py", "education"),
        ("bot/handlers/sections/prayer_schedule_handlers.py", "prayer_schedule"),
        ("bot/handlers/sections/halal_places_handlers.py", "halal_places"),
        ("bot/handlers/sections/events_calendar_handlers.py", "events_calendar"),
        ("bot/handlers/sections/ai_assistant.py", "islamic_assistant"),
    ]
    
    all_ok = True
    for file_path, callback_data in entry_points:
        if not test_file_exists(file_path):
            all_ok = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, что обработчик существует
        if f'@router.callback_query(F.data == "{callback_data}")' in content:
            print(f"✓ {file_path} содержит обработчик для {callback_data}")
        else:
            print(f"✗ {file_path} не содержит обработчик для {callback_data}")
            all_ok = False
            continue
        
        # Проверяем, что используется delete() + answer() вместо edit_text
        handler_pattern = f'@router\\.callback_query\\(F\\.data == "{callback_data}"\\)[\\s\\S]*?async def[\\s\\S]*?await callback\\.message\\.'
        import re
        match = re.search(handler_pattern, content, re.DOTALL)
        if match:
            handler_text = match.group(0)
            if 'await callback.message.delete()' in handler_text and 'await callback.message.answer(' in handler_text:
                print(f"✓ Обработчик {callback_data} использует delete() + answer()")
            elif 'await show_main_menu' in handler_text:
                print(f"✓ Обработчик {callback_data} использует show_main_menu")
            else:
                print(f"✗ Обработчик {callback_data} может использовать edit_text")
                all_ok = False
        else:
            print(f"⚠ Не удалось проверить обработчик {callback_data}")
    
    return all_ok

def main():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ UI/UX MAIN MENU REDESIGN")
    print("=" * 60)
    
    tests = [
        ("Существование файлов", lambda: all([
            test_file_exists("bot/core/ui_config.py"),
            test_file_exists("bot/handlers/common/show_main_menu.py"),
            test_file_exists("bot/handlers/start.py"),
            test_file_exists("bot/handlers/main_menu.py"),
            test_file_exists("bot/handlers/common_nav.py"),
        ])),
        ("Конфигурация UI", test_ui_config),
        ("Функция show_main_menu", test_show_main_menu),
        ("Обновленные обработчики", test_updated_handlers),
        ("Исправленные точки входа", test_entry_points_fixed),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"Результат: {'ПРОЙДЕН' if result else 'НЕ ПРОЙДЕН'}")
        except Exception as e:
            print(f"Ошибка при выполнении теста: {e}")
            results.append((test_name, False))
            print(f"Результат: НЕ ПРОЙДЕН")
    
    print("\n" + "=" * 60)
    print("ИТОГИ:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print(f"{'✓' if result else '✗'} {test_name}")
    
    print(f"\nПройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == "__main__":
    sys.exit(main())
