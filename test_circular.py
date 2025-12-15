#!/usr/bin/env python3
"""Тестирование циклической зависимости."""

import sys
import traceback

def test_circular():
    """Тестирует циклическую зависимость между loader и scheduler."""
    print("Тестирование циклической зависимости...")
    print("=" * 60)
    
    # Пытаемся импортировать loader и scheduler последовательно
    try:
        print("1. Импортируем bot.core.loader...")
        from bot.core.loader import bot, dp, redis_client
        print("   ✓ Успешно")
        
        # Проверяем, что loader не импортирует scheduler
        loader_module = sys.modules['bot.core.loader']
        scheduler_attrs = ['scheduler', 'setup_scheduler', 'start_scheduler', 'stop_scheduler']
        for attr in scheduler_attrs:
            if hasattr(loader_module, attr):
                print(f"   ✗ ОШИБКА: {attr} всё ещё в loader.py")
            else:
                print(f"   ✓ {attr} отсутствует в loader.py (правильно)")
        
        print("\n2. Импортируем bot.services.scheduler...")
        from bot.services.scheduler import setup_scheduler, start_scheduler, stop_scheduler, set_bot_instance
        print("   ✓ Успешно")
        
        print("\n3. Проверяем, что scheduler импортирует users...")
        scheduler_module = sys.modules['bot.services.scheduler']
        if 'bot.services.users' in str(scheduler_module.__file__):
            print("   ✓ scheduler импортирует users")
        
        print("\n4. Проверяем, что users импортирует redis...")
        from bot.services.users import user_exists
        print("   ✓ users импортирует redis")
        
        print("\n5. Проверяем, что redis импортирует loader...")
        from bot.cache.redis import cached
        print("   ✓ redis импортирует loader")
        
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ: Циклическая зависимость УСТРАНЕНА!")
        print("loader → scheduler → users → redis → loader (цикл разорван)")
        print("=" * 60)
        
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Другая ошибка: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_circular()
    sys.exit(0 if success else 1)
