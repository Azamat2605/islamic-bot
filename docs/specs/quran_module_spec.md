# Техническая спецификация 003: Модуль "Коран" (Quran Reader)

## Обзор
Модуль "Коран" предоставляет пользователям возможность читать суры Корана с переводом на русский язык, слушать аудио (заглушка), добавлять суры в избранное и настраивать переводчика. Модуль является подразделом раздела "Знания".

## Стек технологий
- Python 3.11
- Aiogram 3.x
- Static mock data (Python dictionaries) - без базы данных для MVP

## 1. Архитектура модуля

### 1.1 Интеграция с существующей структурой
Модуль "Коран" является подмодулем раздела "Знания". Существующая структура:
```
bot/handlers/sections/knowledge/
├── __init__.py
├── menu.py (главное меню раздела "Знания")
└── quran/ (новый подмодуль)
    ├── __init__.py
    ├── catalog.py (каталог сур)
    └── reading.py (чтение суры)
```

### 1.2 Точка входа
Пользователь проходит путь:
1. Главное меню → "Знания" → "📖 Коран"
2. Открывается **Screen 1.1: Surah Catalog (Grid View)**

## 2. Структура файлов

### 2.1 Новые файлы

#### Обработчики
```
bot/handlers/sections/knowledge/quran/
├── __init__.py              # Роутер модуля Коран
├── catalog.py               # Обработчики каталога сур
├── reading.py               # Обработчики чтения суры
└── __pycache__/
```

#### Клавиатуры
```
bot/keyboards/inline/knowledge/
├── __init__.py
├── main_kb.py (существующий)
└── quran_kb.py (новый)      # Клавиатуры модуля Коран
```

#### Данные
```
bot/data/
├── __init__.py
└── mock_knowledge.py (новый) # Мок-данные для Корана
```

#### Состояния (если потребуется)
```
bot/states/knowledge/
├── __init__.py
└── quran.py (новый)         # FSM состояния для настроек
```

### 2.2 Роутеры и иерархия
```python
# bot/handlers/sections/knowledge/quran/__init__.py
from aiogram import Router

quran_router = Router(name="quran")

# Импорт обработчиков
from . import catalog, reading

# Включение подроутеров
quran_router.include_router(catalog.router)
quran_router.include_router(reading.router)

# bot/handlers/sections/knowledge/__init__.py (обновить)
from .quran import quran_router
knowledge_router.include_router(quran_router)
```

## 3. Структура данных

### 3.1 Мок-данные Корана
```python
# bot/data/mock_knowledge.py
"""
Мок-данные для модуля Знаний.
Для MVP используем только первые 10 и последние 10 сур.
"""

QURAN_DATA = {
    "surahs": [
        # Первые 10 сур
        {
            "id": 1,
            "name_arabic": "الفاتحة",
            "name_transliteration": "Al-Fatiha",
            "name_translation": "Открывающая",
            "verse_count": 7,
            "revelation_type": "Meccan",
            "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ الرَّحْمَٰنِ الرَّحِيمِ مَالِكِ يَوْمِ الدِّينِ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
            "translations": {
                "kuliev": "Во имя Аллаха, Милостивого, Милосердного! Хвала Аллаху, Господу миров, Милостивому, Милосердному, Властелину Дня воздаяния! Тебе одному мы поклоняемся и Тебя одного молим о помощи. Веди нас прямым путем, путем тех, кого Ты облагодетельствовал, не тех, на кого пал гнев, и не заблудших.",
                "osmanov": "Во имя Аллаха, Милостивого, Милосердного! Хвала Аллаху, Господу миров, Милостивому, Милосердному, Царю в День суда! Тебе мы поклоняемся и у Тебя просим помощи. Веди нас по дороге прямой, по дороге тех, которых Ты облагодетельствовал, не тех, что под гневом, и не заблудших."
            }
        },
        {
            "id": 2,
            "name_arabic": "البقرة",
            "name_transliteration": "Al-Baqarah",
            "name_translation": "Корова",
            "verse_count": 286,
            "revelation_type": "Medinan",
            "arabic_text": "الم ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ",
            "translations": {
                "kuliev": "Алиф. Лам. Мим. Это Писание, в котором нет сомнения, является верным руководством для богобоязненных.",
                "osmanov": "Алиф, лам, мим. Это - Писание, в котором нет сомнения, - руководство для богобоязненных."
            }
        },
        # ... суры 3-10 ...
        {
            "id": 10,
            "name_arabic": "يونس",
            "name_transliteration": "Yunus",
            "name_translation": "Юнус",
            "verse_count": 109,
            "revelation_type": "Meccan",
            "arabic_text": "الر ۚ تِلْكَ آيَاتُ الْكِتَابِ الْحَكِيمِ",
            "translations": {
                "kuliev": "Алиф. Лам. Ра. Это - аяты мудрого Писания.",
                "osmanov": "Алиф, лам, ра. Это - знамения книги мудрой."
            }
        },
        # Последние 10 сур (105-114)
        {
            "id": 105,
            "name_arabic": "الفيل",
            "name_transliteration": "Al-Fil",
            "name_translation": "Слон",
            "verse_count": 5,
            "revelation_type": "Meccan",
            "arabic_text": "أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ",
            "translations": {
                "kuliev": "Разве ты не видел, как поступил твой Господь с владельцами слона?",
                "osmanov": "Разве ты не знаешь, как поступил Господь твой с владельцами слона?"
            }
        },
        # ... суры 106-113 ...
        {
            "id": 114,
            "name_arabic": "الناس",
            "name_transliteration": "An-Nas",
            "name_translation": "Люди",
            "verse_count": 6,
            "revelation_type": "Meccan",
            "arabic_text": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ مَلِكِ النَّاسِ إِلَٰهِ النَّاسِ",
            "translations": {
                "kuliev": "Скажи: «Прибегаю к защите Господа людей, Царя людей, Бога людей»",
                "osmanov": "Скажи: «Прибегаю к Господу людей, царю людей, Богу людей»"
            }
        }
    ],
    "translators": [
        {"id": "kuliev", "name": "Эльмир Кулиев"},
        {"id": "osmanov", "name": "Магомед-Нури Османов"}
    ]
}

# Вспомогательные функции
def get_surah_by_id(surah_id: int) -> dict | None:
    """Получить суру по ID"""
    for surah in QURAN_DATA["surahs"]:
        if surah["id"] == surah_id:
            return surah
    return None

def get_surahs_page(page: int, items_per_page: int = 8) -> list[dict]:
    """Получить страницу сур для пагинации"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    return QURAN_DATA["surahs"][start_idx:end_idx]

def get_total_pages(items_per_page: int = 8) -> int:
    """Получить общее количество страниц"""
    total = len(QURAN_DATA["surahs"])
    return (total + items_per_page - 1) // items_per_page
```

## 4. Схема callback данных

### 4.1 Форматы строк callback_data
Для MVP используем простые строковые форматы вместо CallbackData классов:

```
# Каталог сур
quran:page:{page_number}           # Пагинация каталога
quran:read:{surah_id}              # Чтение суры

# Чтение суры
quran:listen:{surah_id}            # Аудио (заглушка)
quran:favorite:{surah_id}          # Избранное (toggle)
quran:settings:{surah_id}          # Настройки перевода
quran:prev:{surah_id}              # Предыдущая сура
quran:next:{surah_id}              # Следующая сура
quran:back_to_list:{current_page}  # Назад к каталогу

# Настройки перевода
quran:translator:{translator_id}   # Выбор переводчика
quran:back_to_reading:{surah_id}   # Назад к чтению
```

### 4.2 Парсинг callback данных
```python
def parse_callback_data(callback_data: str) -> tuple[str, dict]:
    """
    Парсит callback данные формата 'prefix:key1:value1:key2:value2...'
    Возвращает (action, params)
    """
    parts = callback_data.split(":")
    if len(parts) < 2:
        return callback_data, {}
    
    action = parts[0]
    params = {}
    
    # Обработка простых форматов
    if action == "quran":
        if len(parts) >= 3:
            sub_action = parts[1]
            if sub_action in ["page", "read", "listen", "favorite", "settings", "prev", "next"]:
                params = {"surah_id": int(parts[2])} if parts[2].isdigit() else {}
            elif sub_action == "translator":
                params = {"translator_id": parts[2]}
            elif sub_action == "back_to_list":
                params = {"page": int(parts[2])} if parts[2].isdigit() else {"page": 0}
            elif sub_action == "back_to_reading":
                params = {"surah_id": int(parts[2])} if parts[2].isdigit() else {}
    
    return action, params
```

## 5. Клавиатуры

### 5.1 Функции в `bot/keyboards/inline/knowledge/quran_kb.py`

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.data.mock_knowledge import get_surahs_page, get_total_pages, get_surah_by_id

def get_surah_catalog_kb(page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура каталога сур (Grid View 2x4)
    
    Args:
        page: Номер страницы (0-based)
    
    Returns:
        InlineKeyboardMarkup с кнопками сур и пагинацией
    """
    builder = InlineKeyboardBuilder()
    
    # Получаем суры для текущей страницы
    surahs = get_surahs_page(page, items_per_page=8)
    
    # Создаем сетку 2x4 (2 строки по 4 кнопки)
    for surah in surahs:
        # Формат: "1. Аль-Фатиха (7)"
        button_text = f"{surah['id']}. {surah['name_transliteration']} ({surah['verse_count']})"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"quran:read:{surah['id']}"
        ))
    
    # Устанавливаем сетку 2x4
    builder.adjust(4, 4)
    
    # Пагинация (если нужно)
    total_pages = get_total_pages(items_per_page=8)
    pagination_buttons = []
    
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"quran:page:{page-1}"
        ))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️ Вперед",
            callback_data=f"quran:page:{page+1}"
        ))
    
    if pagination_buttons:
        builder.row(*pagination_buttons)
    
    # Кнопка назад в меню Знаний
    builder.row(InlineKeyboardButton(
        text="🔙 Назад в Знания",
        callback_data="know:quran_back"
    ))
    
    return builder.as_markup()


def get_surah_reading_kb(surah_id: int, is_favorite: bool = False, 
                         current_translator: str = "kuliev") -> InlineKeyboardMarkup:
    """
    Клавиатура чтения суры
    
    Args:
        surah_id: ID суры
        is_favorite: Добавлена ли в избранное
        current_translator: Текущий переводчик
    
    Returns:
        InlineKeyboardMarkup с контролами чтения
    """
    builder = InlineKeyboardBuilder()
    
    # Первая строка: Аудио и Избранное
    favorite_icon = "❤️" if is_favorite else "🤍"
    builder.row(
        InlineKeyboardButton(
            text="▶️ Слушать",
            callback_data=f"quran:listen:{surah_id}"
        ),
        InlineKeyboardButton(
            text=f"{favorite_icon} Избранное",
            callback_data=f"quran:favorite:{surah_id}"
        )
    )
    
    # Вторая строка: Настройки
    builder.row(
        InlineKeyboardButton(
            text="⚙️ Настройки",
            callback_data=f"quran:settings:{surah_id}"
        )
    )
    
    # Третья строка: Навигация по сурам
    surah = get_surah_by_id(surah_id)
    nav_buttons = []
    
    if surah_id > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data=f"quran:prev:{surah_id-1}"
        ))
    
    nav_buttons.append(InlineKeyboardButton(
        text="📋 К каталогу",
        callback_data=f"quran:back_to_list:0"
    ))
    
    if surah_id < 114:
        nav_buttons.append(InlineKeyboardButton(
            text="Следующая ➡️",
            callback_data=f"quran:next:{surah_id+1}"
        ))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    return builder.as_markup()


def get_translator_settings_kb(surah_id: int, current_translator: str = "kuliev") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора переводчика
    
    Args:
        surah_id: ID суры (для возврата)
        current_translator: Текущий выбранный переводчик
    
    Returns:
        InlineKeyboardMarkup с выбором переводчика
    """
    builder = InlineKeyboardBuilder()
    
    # Переводчики
    translators = [
        ("kuliev", "Эльмир Кулиев"),
        ("osmanov", "Магомед-Нури Османов")
    ]
    
    for translator_id, translator_name in translators:
        prefix = "✅" if translator_id == current_translator else "⚪"
        builder.row(InlineKeyboardButton(
            text=f"{prefix} {translator_name}",
            callback_data=f"quran:translator:{translator_id}"
        ))
    
    # Кнопка назад к чтению
    builder.row(InlineKeyboardButton(
        text="🔙 Назад к чтению",
        callback_data=f"quran:back_to_reading:{surah_id}"
    ))
    
    return builder.as_markup()
```

## 6. Логика обработчиков

### 6.1 Обработчики каталога (`bot/handlers/sections/knowledge/quran/catalog.py`)

#### 6.1.1 Вход в модуль Коран
```python
@router.callback_query(F.data == "know:quran")
async def quran_entry(callback: CallbackQuery):
    """
    Обработчик входа в модуль Коран из меню Знаний.
    Показывает первую страницу каталога сур.
    """
    try:
        # Получаем клавиатуру каталога (страница 0)
        keyboard = get_surah_catalog_kb(page=0)
        
        # Формируем сообщение
        message_text = (
            "📖 **Коран**\n\n"
            "Выберите суру для чтения:\n"
            "_(Для навигации используйте кнопки ниже)_"
        )
        
        # Отправляем или редактируем сообщение
        if callback.message.text != message_text:
            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in quran_entry: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)
```

#### 6.1.2 Пагинация каталога
```python
@router.callback_query(F.data.startswith("quran:page:"))
async def quran_page_handler(callback: CallbackQuery):
    """
    Обработчик пагинации каталога сур.
    Формат callback_data: quran:page:{page_number}
    """
    try:
        # Парсим номер страницы
        page_str = callback.data.split(":")[2]
        page = int(page_str) if page_str.isdigit() else 0
        
        # Получаем клавиатуру для запрошенной страницы
        keyboard = get_surah_catalog_kb(page=page)
        
        # Обновляем сообщение
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in quran_page_handler: {e}")
        await callback.answer("Ошибка пагинации", show_alert=True)
```

### 6.2 Обработчики чтения (`bot/handlers/sections/knowledge/quran/reading.py`)

#### 6.2.1 Чтение суры
```python
@router.callback_query(F.data.startswith("quran:read:"))
async def quran_read_handler(callback: CallbackQuery):
    """
    Обработчик чтения суры.
    Формат callback_data: quran:read:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1
        
        # Получаем данные суры
        surah = get_surah_by_id(surah_id)
        if not surah:
            await callback.answer("Сура не найдена", show_alert=True)
            return
        
        # Получаем сохраненные настройки пользователя (из сессии или заглушки)
        user_id = callback.from_user.id
        is_favorite = False  # Заглушка - в MVP нет БД
        current_translator = "kuliev"  # Переводчик по умолчанию
        
        # Формируем текст суры
        translation = surah["translations"].get(current_translator, "")
        message_text = (
            f"**{surah['name_transliteration']} ({surah['name_translation']})**\n"
            f"_{surah['name_arabic']}_\n\n"
            f"**Арабский текст:**\n"
            f"`{surah['arabic_text'][:200]}...`\n\n"
            f"**Перевод ({current_translator}):**\n"
            f"{translation[:300]}..."
        )
        
        # Получаем клавиатуру чтения
        keyboard = get_surah_reading_kb(
            surah_id=surah_id,
            is_favorite=is_favorite,
            current_translator=current_translator
        )
        
        # Отправляем сообщение
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in quran_read_handler: {e}")
        await callback.answer("Ошибка загрузки суры", show_alert=True)
```

#### 6.2.2 Аудио (заглушка)
```python
@router.callback_query(F.data.startswith("quran:listen:"))
async def quran_listen_handler(callback: CallbackQuery):
    """
    Обработчик аудио (заглушка).
    Формат callback_data: quran:listen:{surah_id}
    """
    await callback.answer("🎧 Аудио функция в разработке", show_alert=False)
```

#### 6.2.3 Избранное (toggle)
```python
@router.callback_query(F.data.startswith("quran:favorite:"))
async def quran_favorite_handler(callback: CallbackQuery):
    """
    Обработчик избранного (toggle UI).
    Формат callback_data: quran:favorite:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1
        
        # В MVP просто меняем иконку без сохранения в БД
        # Получаем текущее состояние из текста кнопки
        message = callback.message
        keyboard = message.reply_markup
        
        # Ищем кнопку "Избранное" и меняем иконку
        new_rows = []
        for row in keyboard.inline_keyboard:
            new_buttons = []
            for button in row:
                if "Избранное" in button.text:
                    # Меняем иконку
                    if "❤️" in button.text:
                        new_text = button.text.replace("❤️", "🤍")
                    else:
                        new_text = button.text.replace("🤍", "❤️")
                    new_buttons.append(InlineKeyboardButton(
                        text=new_text,
                        callback_data=button.callback_data
                    ))
                else:
                    new_buttons.append(button)
            new_rows.append(new_buttons)
        
        # Создаем новую клавиатуру
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=new_rows)
        
        # Обновляем сообщение
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
        
        # Показываем уведомление
        if "❤️" in callback.message.reply_markup.inline_keyboard[0][1].text:
            await callback.answer("✅ Добавлено в избранное")
        else:
            await callback.answer("❌ Удалено из избранного")
        
    except Exception as e:
        logger.error(f"Error in quran_favorite_handler: {e}")
        await callback.answer("Ошибка обновления избранного", show_alert=True)
```

#### 6.2.4 Настройки перевода
```python
@router.callback_query(F.data.startswith("quran:settings:"))
async def quran_settings_handler(callback: CallbackQuery):
    """
    Обработчик настроек перевода.
    Формат callback_data: quran:settings:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1
        
        # Получаем клавиатуру настроек
        keyboard = get_translator_settings_kb(
            surah_id=surah_id,
            current_translator="kuliev"  # Заглушка
        )
        
        # Формируем сообщение
        message_text = (
            f"**Настройки перевода**\n\n"
            f"Выберите переводчика для суры {surah_id}:\n"
            f"_(Изменения применяются сразу)_"
        )
        
        # Обновляем сообщение
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in quran_settings_handler: {e}")
        await callback.answer("Ошибка открытия настроек", show_alert=True)
```

#### 6.2.5 Выбор переводчика
```python
@router.callback_query(F.data.startswith("quran:translator:"))
async def quran_translator_handler(callback: CallbackQuery):
    """
    Обработчик выбора переводчика.
    Формат callback_data: quran:translator:{translator_id}
    """
    try:
        # Парсим ID переводчика
        translator_id = callback.data.split(":")[2]
        
        # Получаем ID суры из предыдущего сообщения
        # В реальной реализации нужно хранить состояние
        # Для MVP используем заглушку - возвращаем к суре 1
        surah_id = 1
        
        # Обновляем сообщение с выбранным переводчиком
        surah = get_surah_by_id(surah_id)
        translation = surah["translations"].get(translator_id, "")
        
        message_text = (
            f"**{surah['name_transliteration']} ({surah['name_translation']})**\n"
            f"_{surah['name_arabic']}_\n\n"
            f"**Арабский текст:**\n"
            f"`{surah['arabic_text'][:200]}...`\n\n"
            f"**Перевод ({translator_id}):**\n"
            f"{translation[:300]}..."
        )
        
        # Получаем клавиатуру чтения с обновленным переводчиком
        keyboard = get_surah_reading_kb(
            surah_id=surah_id,
            is_favorite=False,
            current_translator=translator_id
        )
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer(f"Переводчик изменен")
        
    except Exception as e:
        logger.error(f"Error in quran_translator_handler: {e}")
        await callback.answer("Ошибка выбора переводчика", show_alert=True)
```

#### 6.2.6 Навигация по сурам
```python
@router.callback_query(F.data.startswith("quran:prev:"))
@router.callback_query(F.data.startswith("quran:next:"))
async def quran_navigation_handler(callback: CallbackQuery):
    """
    Обработчик навигации по сурам (предыдущая/следующая).
    Форматы: quran:prev:{surah_id}, quran:next:{surah_id}
    """
    try:
        # Определяем направление и получаем ID суры
        parts = callback.data.split(":")
        direction = parts[1]  # "prev" или "next"
        current_surah_id = int(parts[2]) if parts[2].isdigit() else 1
        
        # Вычисляем новую суру
        if direction == "prev":
            new_surah_id = max(1, current_surah_id - 1)
        else:  # "next"
            new_surah_id = min(114, current_surah_id + 1)
        
        # Если сура не изменилась (границы достигнуты)
        if new_surah_id == current_surah_id:
            await callback.answer(
                "Это первая/последняя сура" if direction == "prev" else "Это последняя сура",
                show_alert=False
            )
            return
        
        # Вызываем обработчик чтения суры с новым ID
        # Создаем искусственный callback_data
        callback.data = f"quran:read:{new_surah_id}"
        await quran_read_handler(callback)
        
    except Exception as e:
        logger.error(f"Error in quran_navigation_handler: {e}")
        await callback.answer("Ошибка навигации", show_alert=True)
```

#### 6.2.7 Возврат к каталогу
```python
@router.callback_query(F.data.startswith("quran:back_to_list:"))
async def quran_back_to_list_handler(callback: CallbackQuery):
    """
    Обработчик возврата к каталогу сур.
    Формат: quran:back_to_list:{page_number}
    """
    try:
        # Парсим номер страницы
        page_str = callback.data.split(":")[2]
        page = int(page_str) if page_str.isdigit() else 0
        
        # Вызываем обработчик страницы каталога
        callback.data = f"quran:page:{page}"
        await quran_page_handler(callback)
        
    except Exception as e:
        logger.error(f"Error in quran_back_to_list_handler: {e}")
        await callback.answer("Ошибка возврата к каталогу", show_alert=True)
```

#### 6.2.8 Возврат к чтению
```python
@router.callback_query(F.data.startswith("quran:back_to_reading:"))
async def quran_back_to_reading_handler(callback: CallbackQuery):
    """
    Обработчик возврата к чтению суры из настроек.
    Формат: quran:back_to_reading:{surah_id}
    """
    try:
        # Парсим ID суры
        surah_id_str = callback.data.split(":")[2]
        surah_id = int(surah_id_str) if surah_id_str.isdigit() else 1
        
        # Вызываем обработчик чтения суры
        callback.data = f"quran:read:{surah_id}"
        await quran_read_handler(callback)
        
    except Exception as e:
        logger.error(f"Error in quran_back_to_reading_handler: {e}")
        await callback.answer("Ошибка возврата к чтению", show_alert=True)
```

## 7. Интеграция с меню Знаний

### 7.1 Обновление главного меню Знаний
В `bot/keyboards/inline/knowledge/main_kb.py` кнопка "📖 Коран" уже существует с callback `know:quran`. 
Нужно убедиться, что обработчик `quran_entry` зарегистрирован и реагирует на этот callback.

### 7.2 Обновление роутеров
```python
# bot/handlers/sections/knowledge/__init__.py
from .quran import quran_router

# Включить quran_router в knowledge_router
knowledge_router.include_router(quran_router)

# bot/handlers/sections/__init__.py
from .knowledge import knowledge_router

# knowledge_router уже включен в главный роутер
```

## 8. Состояния пользователя (сессии)

### 8.1 Хранение настроек
Для MVP используем простой in-memory словарь:
```python
# bot/handlers/sections/knowledge/quran/session.py
user_sessions = {}

def get_user_session(user_id: int) -> dict:
    """Получить сессию пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "current_translator": "kuliev",
            "favorites": set(),  # ID избранных сур
            "last_page": 0,      # Последняя страница каталога
            "last_surah": 1      # Последняя просмотренная сура
        }
    return user_sessions[user_id]

def update_user_translator(user_id: int, translator_id: str):
    """Обновить переводчик пользователя"""
    session = get_user_session(user_id)
    session["current_translator"] = translator_id

def toggle_favorite(user_id: int, surah_id: int) -> bool:
    """Переключить избранное"""
    session = get_user_session(user_id)
    if surah_id in session["favorites"]:
        session["favorites"].remove(surah_id)
        return False
    else:
        session["favorites"].add(surah_id)
        return True

def is_favorite(user_id: int, surah_id: int) -> bool:
    """Проверить, в избранном ли сура"""
    session = get_user_session(user_id)
    return surah_id in session["favorites"]
```

## 9. Текстовое содержимое (русский язык)

### 9.1 Сообщения каталога
```
📖 Коран

Выберите суру для чтения:
_(Для навигации используйте кнопки ниже)_
```

### 9.2 Сообщение чтения суры
```
**Al-Fatiha (Открывающая)**
_الفاتحة_

**Арабский текст:**
`بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ...`

**Перевод (kuliev):**
Во имя Аллаха, Милостивого, Милосердного! Хвала Аллаху, Господу миров...
```

### 9.3 Сообщение настроек перевода
```
**Настройки перевода**

Выберите переводчика для суры 1:
_(Изменения применяются сразу)_
```

### 9.4 Уведомления (callback.answer)
- "🎧 Аудио функция в разработке"
- "✅ Добавлено в избранное"
- "❌ Удалено из избранного"
- "Переводчик изменен"
- "Ошибка загрузки суры"
- "Произошла ошибка. Попробуйте позже."

## 10. Пошаговый план реализации

### Этап 1: Подготовка данных (0.5 дня)
1. Создать `bot/data/__init__.py`
2. Создать `bot/data/mock_knowledge.py` с мок-данными Корана
3. Протестировать вспомогательные функции

### Этап 2: Клавиатуры (0.5 дня)
1. Создать `bot/keyboards/inline/knowledge/quran_kb.py`
2. Реализовать `get_surah_catalog_kb`, `get_surah_reading_kb`, `get_translator_settings_kb`
3. Протестировать генерацию клавиатур

### Этап 3: Обработчики каталога (1 день)
1. Создать структуру `bot/handlers/sections/knowledge/quran/`
2. Создать `__init__.py` с роутером
3. Создать `catalog.py` с обработчиками `quran_entry` и `quran_page_handler`
4. Интегрировать с существующим меню Знаний

### Этап 4: Обработчики чтения (1 день)
1. Создать `reading.py` с обработчиками чтения суры
2. Реализовать `quran_read_handler`, `quran_listen_handler`, `quran_favorite_handler`
3. Реализовать `quran_settings_handler`, `quran_translator_handler`
4. Реализовать навигационные обработчики

### Этап 5: Сессии пользователя (0.5 дня)
1. Создать `session.py` для хранения in-memory состояний
2. Интегрировать с обработчиками
3. Протестировать сохранение настроек

### Этап 6: Интеграция и тестирование (1 день)
1. Обновить `bot/handlers/sections/knowledge/__init__.py` для включения quran_router
2. Протестировать полный поток: Знания → Коран → Каталог → Чтение → Настройки
3. Исправить баги и улучшить UX

### Этап 7: Документация и финализация (0.5 дня)
1. Обновить документацию модуля
2. Проверить соответствие спецификации
3. Подготовить релизные заметки

## 11. Угловые случаи и обработка ошибок

### 11.1 Несуществующая сура
- **Проблема:** Пользователь пытается открыть суру с ID вне диапазона 1-114
- **Решение:** Валидация ID, показ сообщения "Сура не найдена"

### 11.2 Пустые данные перевода
- **Проблема:** Переводчик не найден в данных суры
- **Решение:** Использовать переводчик по умолчанию (kuliev), логировать ошибку

### 11.3 Проблемы с пагинацией
- **Проблема:** Пользователь пытается перейти на несуществующую страницу
- **Решение:** Нормализация номера страницы в диапазоне [0, total_pages-1]

### 11.4 Ошибки редактирования сообщений
- **Проблема:** Сообщение уже было отредактировано или удалено
- **Решение:** Обработка исключений MessageNotModified, MessageToEditNotFound

### 11.5 Проблемы с памятью сессий
- **Проблема:** In-memory сессии теряются при перезапуске бота
- **Решение:** Для MVP это приемлемо. В будущем - перенос в Redis/БД

## 12. Будущие улучшения (post-MVP)

### 12.1 Постоянное хранение
- Миграция с in-memory сессий на Redis
- Сохранение избранного в БД
- История чтения пользователей

### 12.2 Расширенные функции
- Реальное аудио воспроизведение
- Поиск по сурам и аятам
- Заметки пользователей к аятам
- Совместное чтение (групповые сессии)

### 12.3 Улучшения UI/UX
- Прогресс чтения (сколько % сур прочитано)
- Ежедневные напоминания о чтении
- Рекомендации сур на основе истории
- Темная/светлая тема

### 12.4 Локализация
- Поддержка дополнительных языков перевода
- Локализация интерфейса на языки пользователей
- Автоматическое определение языка

## 13. Заключение

Данная спецификация предоставляет полное техническое описание модуля "Коран" для Islamic Telegram Bot. Реализация включает:

1. **Каталог сур** с пагинацией и grid view (2x4)
2. **Чтение сур** с арабским текстом и переводами
3. **Интерактивные элементы:** аудио (заглушка), избранное, настройки перевода
4. **Навигацию** между сурами и возврат к каталогу
5. **In-memory сессии** для хранения пользовательских предпочтений

Модуль спроектирован как MVP с использованием статических мок-данных, что позволяет быстро реализовать и протестировать основную функциональность без зависимости от базы данных.

Архитектура модуля следует существующим паттернам проекта (роутеры, обработчики, клавиатуры) и легко интегрируется с разделом "Знания".

---

*Документ подготовлен: 12.12.2025*  
*Версия спецификации: 1.0*  
*Статус: Готов к реализации*  
*Сложность реализации: Средняя (3-4 дня для опытного разработчика)*
