#!/usr/bin/env python3
"""
Тестирование callback данных для модуля Halal Places.
Проверяем, правильно ли формируются callback данные для кнопок.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.callbacks.halal import HalalCallback, HalalAction
from bot.keyboards.inline.halal import (
    get_place_details_keyboard,
    get_places_list_keyboard,
    get_categories_keyboard,
    get_halal_main_keyboard
)


def test_callbacks() -> None:
    """Тестируем формирование callback данных."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ CALLBACK ДАННЫХ HALAL")
    print("=" * 60)
    
    # 1. Тест callback данных для кнопки "Назад"
    print("\n1. Тест callback данных для кнопки 'Назад':")
    
    # Кнопка "Назад" из главного меню
    callback_main = HalalCallback(action=HalalAction.BACK, from_state="main")
    print(f"   Из главного меню: {callback_main.pack()}")
    print(f"   Действие: {callback_main.action}")
    print(f"   From state: {callback_main.from_state}")
    
    # Кнопка "Назад" из деталей места
    callback_details = HalalCallback(action=HalalAction.BACK, from_state="details")
    print(f"\n   Из деталей места: {callback_details.pack()}")
    print(f"   Действие: {callback_details.action}")
    print(f"   From state: {callback_details.from_state}")
    
    # 2. Тест callback данных для кнопки "Показать на карте"
    print("\n2. Тест callback данных для кнопки 'Показать на карте':")
    
    callback_map = HalalCallback(action=HalalAction.MAP, place_id=1)
    print(f"   Для места ID=1: {callback_map.pack()}")
    print(f"   Действие: {callback_map.action}")
    print(f"   Place ID: {callback_map.place_id}")
    
    # 3. Тест формирования клавиатур
    print("\n3. Тест формирования клавиатур:")
    
    # Клавиатура деталей места
    print("\n   Клавиатура деталей места (ID=1):")
    keyboard_details = get_place_details_keyboard(place_id=1, is_favorite=False)
    for row in keyboard_details.inline_keyboard:
        for button in row:
            print(f"     Кнопка: '{button.text}'")
            print(f"     Callback: {button.callback_data}")
    
    # Клавиатура списка мест (заглушка)
    print("\n   Клавиатура списка мест:")
    mock_places = [
        {"id": 1, "title": "Тестовое место 1"},
        {"id": 2, "title": "Тестовое место 2"}
    ]
    keyboard_list = get_places_list_keyboard(mock_places)
    for row in keyboard_list.inline_keyboard:
        for button in row:
            print(f"     Кнопка: '{button.text}'")
            if button.callback_data:
                print(f"     Callback: {button.callback_data}")
    
    # 4. Проверка unpack callback данных
    print("\n4. Проверка распаковки callback данных:")
    
    # Используем корректную строку, сгенерированную самим callback
    test_data = "halal:back:::0:::main"
    try:
        unpacked = HalalCallback.unpack(test_data)
        print(f"   Данные: {test_data}")
        print(f"   Распаковано: action={unpacked.action}, from_state={unpacked.from_state}")
    except Exception as e:
        print(f"   Ошибка распаковки: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    test_callbacks()
