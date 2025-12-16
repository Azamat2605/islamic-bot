#!/usr/bin/env python3
"""
Быстрое исправление обработчиков входа в подразделы.
"""
import os

# Файлы для исправления
files = [
    "bot/handlers/sections/prayer_schedule_handlers.py",
    "bot/handlers/sections/halal_places_handlers.py",
    "bot/handlers/sections/events_calendar_handlers.py",
    "bot/handlers/sections/ai_assistant.py",
]

for file_path in files:
    if not os.path.exists(file_path):
        print(f"Файл не существует: {file_path}")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем обработчик с callback_data, соответствующим кнопке главного меню
    # и заменяем edit_text на delete() + answer()
    
    # Для prayer_schedule_handlers.py
    if "prayer_schedule_handlers.py" in file_path:
        # Ищем строку с await callback.message.edit_text в обработчике handle_prayer_main
        # для callback_data == "prayer_schedule"
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Ищем начало обработчика handle_prayer_main
            if '@router.callback_query(F.data == "prayer_schedule")' in line:
                # Пропускаем декоратор и async def
                i += 1
                while i < len(lines) and lines[i].strip() == '':
                    new_lines.append(lines[i])
                    i += 1
                
                # Нашли async def handle_prayer_main
                if i < len(lines) and 'async def handle_prayer_main' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                    
                    # Ищем await callback.message.edit_text
                    while i < len(lines):
                        if 'await callback.message.edit_text' in lines[i]:
                            # Заменяем эту строку и следующие, пока не найдем закрывающую скобку
                            indent = len(lines[i]) - len(lines[i].lstrip())
                            indent_str = ' ' * indent
                            
                            # Удаляем старый edit_text и добавляем новый код
                            new_lines.pop()  # Удаляем последнюю добавленную строку (которая была началом edit_text)
                            
                            # Добавляем новый код
                            new_lines.append(f'{indent_str}    # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение')
                            new_lines.append(f'{indent_str}    # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст')
                            new_lines.append(f'{indent_str}    try:')
                            new_lines.append(f'{indent_str}        await callback.message.delete()')
                            new_lines.append(f'{indent_str}    except Exception as e:')
                            new_lines.append(f'{indent_str}        logger.warning(f"Could not delete previous message: {{e}}")')
                            new_lines.append(f'{indent_str}    ')
                            new_lines.append(f'{indent_str}    # Отправляем новое сообщение')
                            new_lines.append(f'{indent_str}    await callback.message.answer(')
                            
                            # Копируем аргументы из edit_text
                            edit_text_line = lines[i]
                            # Извлекаем аргументы из edit_text
                            args_start = edit_text_line.find('(') + 1
                            args_end = edit_text_line.rfind(')')
                            args = edit_text_line[args_start:args_end].strip()
                            
                            # Разделяем аргументы по запятой, но нужно быть осторожным с вложенными скобками
                            # Просто используем исходные аргументы
                            new_lines.append(f'{indent_str}        {args}')
                            
                            # Пропускаем все строки, связанные с этим edit_text
                            while i < len(lines) and ')' not in lines[i]:
                                i += 1
                            i += 1  # Пропускаем строку с закрывающей скобкой
                            continue
                        elif 'async def' in lines[i] and i > 0 and 'async def handle_prayer_main' not in lines[i]:
                            # Другой обработчик - выходим
                            break
                        else:
                            new_lines.append(lines[i])
                            i += 1
                    continue
            
            i += 1
        
        content = '\n'.join(new_lines)
    
    # Для остальных файлов - упрощенный подход
    else:
        # Простая замена edit_text на delete() + answer() для обработчиков входа
        # Это не идеально, но для быстрого исправления сойдет
        import re
        
        # Шаблон для поиска обработчиков входа
        entry_patterns = {
            "halal_places_handlers.py": r'(@router\.callback_query\(F\.data == "halal_places"\)[\s\S]*?)await callback\.message\.edit_text\s*\(([\s\S]*?)\)',
            "events_calendar_handlers.py": r'(@router\.callback_query\(F\.data == "events_calendar"\)[\s\S]*?)await callback\.message\.edit_text\s*\(([\s\S]*?)\)',
            "ai_assistant.py": r'(@router\.callback_query\(F\.data == "islamic_assistant"\)[\s\S]*?)await callback\.message\.edit_text\s*\(([\s\S]*?)\)',
        }
        
        for filename, pattern in entry_patterns.items():
            if filename in file_path:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    handler_start = match.group(1)
                    edit_text_args = match.group(2)
                    
                    # Создаем новую версию
                    new_handler = f'{handler_start}    # Удаляем предыдущее сообщение (фото-меню) и отправляем новое текстовое сообщение\n'
                    new_handler += '    # Это предотвращает TelegramBadRequest при попытке edit_text фото в текст\n'
                    new_handler += '    try:\n'
                    new_handler += '        await callback.message.delete()\n'
                    new_handler += '    except Exception as e:\n'
                    new_handler += '        logger.warning(f"Could not delete previous message: {{e}}")\n'
                    new_handler += '    \n'
                    new_handler += '    # Отправляем новое сообщение\n'
                    new_handler += f'    await callback.message.answer({edit_text_args})'
                    
                    content = content.replace(match.group(0), new_handler)
                    print(f"Исправлен обработчик в {file_path}")
                break
    
    # Сохраняем изменения
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Обновлен {file_path}")

print("Готово!")
