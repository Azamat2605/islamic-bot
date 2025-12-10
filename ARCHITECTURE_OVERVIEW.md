# Технический Отчет об Архитектуре (Architecture Overview)

**Проект:** Islamic Telegram Bot  
**Дата анализа:** 10.12.2025  
**Цель:** Полное понимание архитектуры проекта для разработки нового функционала

---

## 1. СТРУКТУРА ПРОЕКТА (File Tree)

```
Telegrambot_test/
├── admin/                    # Админ-панель Flask-Admin
├── bot/                     # Основная логика бота
│   ├── analytics/           # Интеграции аналитики (Amplitude, PostHog, Google)
│   ├── cache/               # Redis-кэширование и сериализация
│   ├── core/                # Ядро: конфигурация и загрузчик
│   ├── database/            # Модели БД (SQLAlchemy)
│   ├── filters/             # Кастомные фильтры (admin, number)
│   ├── handlers/            # Обработчики сообщений
│   │   ├── admins/          # Админские команды
│   │   ├── sections/        # Секционные обработчики (профиль, настройки и т.д.)
│   │   └── __init__.py     # Центральный роутер всех хендлеров
│   ├── keyboards/           # Клавиатуры
│   │   ├── inline/          # Inline-кнопки (профиль, настройки, меню)
│   │   └── reply/           # Reply-кнопки
│   ├── locales/             # Локализация (ru, en, ar, tt, ba)
│   ├── middlewares/         # Мидлвари (цепочка обработки)
│   ├── services/            # Бизнес-логика (аналитика, статистика, пользователи)
│   ├── states/              # Состояния FSM (профиль, настройки)
│   └── utils/               # Вспомогательные утилиты
├── configs/                 # Конфигурации мониторинга (Prometheus, Grafana)
├── database/                # Работа с БД (CRUD, миграции, движок)
├── logs/                    # Логи приложения
├── migrations/              # Alembic миграции
├── scripts/                 # Скрипты для администрирования
└── tests/                   # Тесты
```

### Назначение основных директорий:

- **`handlers/`** – Обработчики команд и сообщений, организованные по функциональным блокам.
- **`keyboards/`** – Генерация клавиатур (inline и reply) для взаимодействия с пользователем.
- **`middlewares/`** – Промежуточное ПО для обработки входящих updates (логирование, троттлинг, i18n, БД).
- **`database/`** – Модели данных, CRUD-операции, подключение к БД.
- **`locales/`** – Файлы локализации (gettext .po) для поддержки многоязычности.
- **`states/`** – Машины состояний (FSM) для многошаговых диалогов.

---

## 2. ТЕХНОЛОГИЧЕСКИЙ СТЕК

### Основные технологии:
- **Фреймворк бота:** Aiogram 3.23.0 (асинхронный)
- **База данных:** PostgreSQL + asyncpg
- **ORM:** SQLAlchemy 2.0.44 (асинхронный)
- **Миграции:** Alembic 1.17.2
- **Локализация:** Babel 2.17.0 + кастомный ACLMiddleware
- **Кэширование:** Redis 7.1.0
- **Конфигурация:** Pydantic Settings 2.12.0
- **Логирование:** Loguru 0.7.3
- **Мониторинг:** 
  - Sentry SDK 2.47.0 (трейсинг ошибок)
  - Prometheus Client 0.23.1 (метрики)
  - Grafana (визуализация)
- **Аналитика:** Amplitude / PostHog (конфигурируется через `AMPLITUDE_API_KEY`)
- **Веб-сервер:** AioHTTP 3.13.2 (для webhook режима)
- **Контейнеризация:** Docker + Docker Compose

### Поддерживаемые языки:
- Русский (ru), Английский (en), Арабский (ar), Татарский (tt), Башкирский (ba)

---

## 3. СХЕМА БАЗЫ ДАННЫХ

### Таблицы:

#### 1. **`users`** – Основная информация о пользователях
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR NULL,
    full_name VARCHAR NOT NULL,
    gender VARCHAR NULL,
    city VARCHAR NULL,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **`settings`** – Настройки пользователей (отношение 1:1)
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT REFERENCES users(id) UNIQUE NOT NULL,
    language VARCHAR DEFAULT 'ru',
    notification_on BOOLEAN DEFAULT TRUE,
    timezone VARCHAR DEFAULT 'Europe/Moscow',
    date_format VARCHAR DEFAULT 'DD.MM.YYYY',
    time_format BOOLEAN DEFAULT TRUE,  -- True=24h, False=12h
    prayer_notifications_on BOOLEAN DEFAULT TRUE,
    event_notifications_on BOOLEAN DEFAULT TRUE,
    data_export_requested BOOLEAN DEFAULT FALSE,
    account_deletion_requested BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ключевые поля модели User:
- `telegram_id` – уникальный идентификатор Telegram
- `username` – @username (опционально)
- `full_name` – полное имя пользователя
- `gender` – пол (для персонализации)
- `city` – город (для локационных функций)
- `streak_days` – счетчик дней активности (геймификация)
- `created_at` – дата регистрации

### Связи:
- `User.settings` → `Settings` (One-to-One)
- `Settings.user` → `User` (One-to-One)

---

## 4. МЕХАНИЗМЫ (Core Logic)

### Middleware Chain (Порядок ВАЖЕН!):

1. **`ThrottlingMiddleware`** – Ограничение частоты запросов (rate limit)
   - Применяется к `dp.message.outer_middleware`
   - Контролируется `settings.RATE_LIMIT` (по умолчанию 0.5 сек)

2. **`LoggingMiddleware`** – Логирование входящих updates
   - Применяется к `dp.update.outer_middleware`

3. **`ACLMiddleware`** – Интернационализация (i18n)
   - Использует `bot.core.loader.i18n`
   - Должен быть ДО DatabaseMiddleware (использует сессию)

4. **`DatabaseMiddleware`** – Инъекция сессии БД в контекст
   - Применяется к `dp.update.outer_middleware`
   - Обеспечивает доступ к БД в хендлерах

5. **`CallbackAnswerMiddleware`** – Автоматический ответ на callback-запросы
   - Применяется к `dp.callback_query.middleware`

**Примечание:** AuthMiddleware временно отключен из-за проблем с БД.

### FSM (Машина состояний):
- **Хранение состояний:** Используется встроенный `aiogram.fsm.storage`
- **Локация состояний:** Вероятно Redis (настроен в проекте) или память
- **Файлы состояний:** `bot/states/profile.py`, `bot/states/settings.py`
- **Использование:** Для многошаговых диалогов (настройка профиля, изменение параметров)

### Регистрация хендлеров:
- **Роутеры:** Используются `Router` из aiogram
- **Централизация:** Все роутеры собираются в `bot/handlers/__init__.py` через функцию `get_handlers_router()`
- **Подключение:** В `bot/__main__.py`:
  ```python
  dp.include_router(get_handlers_router())
  ```
- **Организация:** Хендлеры сгруппированы по функциональности:
  - Основные команды (`start.py`, `menu.py`, `info.py`, `support.py`)
  - Секционные обработчики (`sections/`)
  - Админ-панель (`admins/`)

---

## 5. КЛЮЧЕВЫЕ ФАЙЛЫ

### `bot/core/config.py` (Конфигурация приложения)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Бот
    BOT_TOKEN: str
    USE_WEBHOOK: bool = False
    WEBHOOK_BASE_URL: str = "https://xxx.ngrok-free.app"
    RATE_LIMIT: float = 0.5
    
    # База данных
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str | None = None
    DB_NAME: str = "postgres"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None = None
    
    # Аналитика и мониторинг
    AMPLITUDE_API_KEY: str
    SENTRY_DSN: str | None = None
    
    # Администраторы
    ADMINS: list[int] = []
    
    # Локализация
    DEFAULT_LOCALE: str = "en"
    SUPPORTED_LOCALES: list[str] = ["ru", "en", "ar", "tt", "ba"]

settings = Settings()
```

### `bot/__main__.py` (Точка входа)

```python
async def main():
    # Инициализация Sentry (если настроен)
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN)
    
    # Регистрация middleware
    register_middlewares(dp)
    
    # Подключение роутеров
    dp.include_router(get_handlers_router())
    
    # Инициализация БД (создание таблиц)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Установка команд бота
    await set_default_commands(bot)
    
    # Запуск в режиме polling или webhook
    if settings.USE_WEBHOOK:
        await setup_webhook()
    else:
        await dp.start_polling(bot)
```

### `bot/handlers/__init__.py` (Центральный роутер)

```python
def get_handlers_router() -> Router:
    router = Router()
    
    # Основные команды
    router.include_router(start_router)
    router.include_router(menu_router)
    router.include_router(info_router)
    router.include_router(support_router)
    
    # Секционные обработчики
    router.include_router(profile_handlers_router)
    router.include_router(settings_handlers_router)
    router.include_router(education_handlers_router)
    # ... другие секции
    
    # Админ-панель
    router.include_router(admin_panel_router)
    
    return router
```

---

## 6. РЕКОМЕНДАЦИИ ДЛЯ РАЗРАБОТКИ НОВОГО ФУНКЦИОНАЛА

### Добавление новой кнопки/команды:

1. **Определите тип кнопки:**
   - Inline-кнопка → `bot/keyboards/inline/`
   - Reply-кнопка → `bot/keyboards/reply/`

2. **Создайте обработчик:**
   - Основная команда → `bot/handlers/`
   - Секционный функционал → `bot/handlers/sections/`

3. **Зарегистрируйте роутер:**
   - Добавьте импорт в `bot/handlers/__init__.py`
   - Включите роутер в `get_handlers_router()`

4. **Учтите локализацию:**
   - Добавьте переводы во все `.po` файлы в `bot/locales/`
   - Используйте `i18n.gettext` в обработчиках

5. **Работа с БД:**
   - Используйте `DatabaseMiddleware` для доступа к сессии
   - CRUD-операции через `database/crud.py`

6. **Состояния (FSM):**
   - Для многошаговых диалогов создайте состояние в `bot/states/`
   - Используйте `@router.message(StateFilter(...))`

### Важные аспекты архитектуры:

- **Мидлвари обрабатываются в строгом порядке** – учитывайте это при добавлении нового middleware
- **Все строки должны быть локализованы** – не используйте хардкод
- **Работа с БД только через асинхронные сессии** – не блокируйте event loop
- **Конфигурация только через `settings`** – не используйте хардкод значений
- **Логирование через `loguru`** – для отслеживания работы

---

## 7. ЗАПУСК И РАЗВЕРТЫВАНИЕ

### Локальный запуск:
```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка .env (скопировать из .env.example)
cp .env.example .env

# Запуск бота
python -m bot
```

### Docker-развертывание:
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

### Миграции базы данных:
```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

---

**Автор отчета:** Lead Software Architect  
**Статус:** Актуально для версии коммита `6f6c43122c2689a2976767fe38103d0624b121ec`  
**Дата следующего ревью:** 10.01.2026
