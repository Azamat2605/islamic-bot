#!/usr/bin/env python3
"""
Автоматическое заполнение переводов в .po файлах с помощью Google Translate.
Использует библиотеку deep-translator.
"""
import os
import sys
import time
import polib
from deep_translator import GoogleTranslator


# Маппинг кодов папок на коды Google Translate
LANG_MAPPING = {
    'tt': 'tt',          # Tatar
    'ba': None,          # Bashkir - не поддерживается Google Translate, пропускаем
    'ar': 'ar',          # Arabic
}

# Языки, которые пропускаем (исходные языки)
SKIP_LANGS = {'ru', 'en'}

def translate_po_files(locales_dir='bot/locales'):
    """Переводит пустые строки в .po файлах."""
    if not os.path.exists(locales_dir):
        print(f"Директория {locales_dir} не найдена.")
        return

    # Получаем список папок языков
    lang_folders = [d for d in os.listdir(locales_dir)
                    if os.path.isdir(os.path.join(locales_dir, d))]
    
    for lang in lang_folders:
        if lang in SKIP_LANGS:
            print(f"Пропускаем язык {lang} (исходный).")
            continue
        
        target_lang = LANG_MAPPING.get(lang)
        if target_lang is None:
            print(f"Язык {lang} не поддерживается Google Translate, пропускаем.")
            continue
        if not target_lang:
            print(f"Нет маппинга для языка {lang}, пропускаем.")
            continue
        
        po_path = os.path.join(locales_dir, lang, 'LC_MESSAGES', 'messages.po')
        if not os.path.exists(po_path):
            print(f"Файл {po_path} не найден, пропускаем.")
            continue
        
        print(f"Обработка языка {lang} ({target_lang})...")
        po = polib.pofile(po_path)
        updated = 0
        total = len(po)
        
        # Инициализируем переводчик для данного языка
        try:
            translator = GoogleTranslator(source='ru', target=target_lang)
        except Exception as e:
            print(f"Ошибка инициализации переводчика для {lang}: {e}, пропускаем.")
            continue
        
        for i, entry in enumerate(po):
            # Пропускаем записи без msgid
            if not entry.msgid:
                continue
            
            # Если перевод уже есть, пропускаем
            if entry.msgstr:
                continue
            
            # Если msgid содержит переменные, переводим, но оставляем переменные
            # (deep-translator сохранит переменные как есть)
            try:
                translated = translator.translate(entry.msgid)
                entry.msgstr = translated
                updated += 1
                # Задержка между запросами (0.5 секунд для избежания бана)
                time.sleep(0.5)
            except Exception as e:
                print(f"Ошибка перевода записи {i} для языка {lang}: {e}")
                continue
            
            # Прогресс
            if (i + 1) % 10 == 0:
                print(f"  Обработано {i + 1}/{total} записей...")
        
        po.save(po_path)
        print(f"  Язык {lang}: обновлено {updated} из {total} записей.")
    
    print("Перевод завершён.")


if __name__ == '__main__':
    translate_po_files()
    print("Запуск компиляции переводов...")
    os.system('pybabel compile -d bot/locales -D messages')
    print("Готово.")
