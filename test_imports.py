#!/usr/bin/env python3
"""Тестирование импортов для проверки циклических зависимостей."""

import sys
import traceback

def test_imports():
    """Тестирует основные импорты проекта."""
    modules_to_test = [
        "bot.core.loader",
        "bot.services.scheduler",
        "bot.services.users",
        "bot.cache.redis",
        "bot.__main__",
    ]
    
    for module_name in modules_to_test:
        print(f"\nТестируем импорт {module_name}...")
        try:
            __import__(module_name)
            print(f"✓ {module_name} успешно импортирован")
        except ImportError as e:
            print(f"✗ Ошибка импорта {module_name}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"✗ Другая ошибка при импорте {module_name}: {e}")
            traceback.print_exc()
    
    # Проверяем конкретные импорты из loader
    print("\n\nПроверяем конкретные импорты из loader.py...")
    try:
        from bot.core.loader import bot, dp, redis_client
        print("✓ Импорт bot, dp, redis_client из loader.py успешен")
        
        # Проверяем, что scheduler не импортируется из loader
        loader_module = sys.modules['bot.core.loader']
        if hasattr(loader_module, 'setup_scheduler'):
            print("✗ ОШИБКА: setup_scheduler всё ещё в loader.py")
        else:
            print("✓ setup_scheduler удалён из loader.py")
            
        if hasattr(loader_module, 'start_scheduler'):
            print("✗ ОШИБКА: start_scheduler всё ещё в loader.py")
        else:
            print("✓ start_scheduler удалён из loader.py")
            
    except ImportError as e:
        print(f"✗ Ошибка импорта из loader.py: {e}")
        traceback.print_exc()
    
    # Проверяем импорты из __main__
    print("\n\nПроверяем импорты из __main__.py...")
    try:
        from bot.__main__ import on_startup, on_shutdown
        print("✓ Импорт on_startup, on_shutdown из __main__.py успешен")
        
        # Проверяем, что scheduler импортируется из services
        main_module = sys.modules['bot.__main__']
        if hasattr(main_module, 'setup_scheduler'):
            print("✓ setup_scheduler импортирован в __main__.py")
        else:
            print("✗ ОШИБКА: setup_scheduler не импортирован в __main__.py")
            
    except ImportError as e:
        print(f"✗ Ошибка импорта из __main__.py: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование импортов для проверки циклических зависимостей")
    print("=" * 60)
    test_imports()
    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)
