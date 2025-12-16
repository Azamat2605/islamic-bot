#!/usr/bin/env python3
"""
Скрипт для исправления обработчиков входа в подразделы.
Заменяет edit_text на delete() + answer() для точек входа из главного меню.
"""
import os
import re

# Файлы и обработчики для исправления
FILES_TO_FIX = {
    "bot/handlers/sections/prayer_schedule_handlers.py": [
        r'@router\.callback_query\(F\.data == "prayer_schedule"\)[\s\S]*?async def handle_prayer_main[\s\S]*?await callback\.message\.edit_text'
    ],
    "bot/handlers/sections/halal_places_handlers.py": [
        r'@router\.callback_query\(F\.data == "halal_places"\)[\s\S]*?async def halal_places_main_handler[\s\S]*?await callback\.message\.edit_text'
    ],
    "bot/handlers/sections/events_calendar_handlers.py": [
        r'@router\.callback_query\(F\.data == "events_calendar"\)[\s\S]*?async def events_calendar_main_handler[\s\S]*?await callback\.message\.edit_text'
    ],
    "bot/handlers/sections/ai_assistant.py": [
        r'@router\.callback_query\(F\.data == "islamic_assistant"\)[\s\S]*?async def on_ai_assistant_entry[\s\S]*?await callback\.message\.edit_text'
    ],
}

def fix_handler(file_path, pattern):
    """Исправить обработчик в файле."""
    if not os.path.exists(file_path):
        print(f"Файл не существует: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем обработчик
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"✗ Обработчик не найден в {file_path}")
        return False
    
    handler_text = match.group(0)
    
    # Проверяем, уже ли исправлен обработчик (есть delete() и answer())
    if 'await callback.message.delete()' in handler_text and 'await callback.message.answer(' in handler_text:
        print(f"✓ Обработчик уже исправлен в {file_path}")
        return True
    
    # Заменяем edit_text на delete() + answer()
    # Сначала находим текст, который передается в edit_text
    edit_text_match = re.search(r'await callback\.message\.edit_text\s*\(\s*(.*?)\s*,\s*reply_markup\s*=\s*(.*?)\s*\)', handler_text, re.DOTALL)
    if not edit_text_match:
        print(f"✗ Не удалось найти edit_text в обработчике {file_path}")
        return False
    
    text_arg = edit_text_match.group(1).strip()
    reply_markup_arg = edit_text_match.group(2).strip()
    
    # Создаем новую версию обработчика
    new_handler = handler_text.replace(
        edit_text_match.group(0),
        f'''    # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение
    # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete previous message: {{e}}")
    
    # Отправляем новое сообщение
    await callback.message.answer(
        {text_arg},
        reply_markup={reply_markup_arg}
    )'''
    )
    
    # Заменяем в исходном содержимом
    new_content = content.replace(handler_text, new_handler)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Обработчик исправлен в {file_path}")
    return True

def main():
    print("Исправление обработчиков входа в подразделы...")
    
    for file_path, patterns in FILES_TO_FIX.items():
        for pattern in patterns:
            fix_handler(file_path, pattern)

if __name__ == "__main__":
    main()
