# Анализ проекта: Islamic Telegram Bot

## Название и суть проекта

**Islamic Telegram Bot** - это многофункциональный Telegram-бот для мусульман, предоставляющий комплексный набор инструментов для религиозной практики. Основная цель проекта - помочь пользователям соблюдать религиозные обязанности через автоматизированные напоминания и информационную поддержку.

**Ключевая суть**: Бот выступает как цифровой помощник мусульманина, объединяя расписание намазов, исламские знания, календарь событий и сообщество в одном интерфейсе Telegram.

## Технический стек

### Основные технологии:
- **Язык программирования**: Python 3.10+
- **Фреймворк бота**: Aiogram 3.x (асинхронный)
- **База данных**: PostgreSQL (основная), SQLite (для разработки)
- **ORM**: SQLAlchemy 2.0
- **Миграции**: Alembic
- **Планировщик задач**: APScheduler
- **Валидация**: Pydantic 2.x
- **Логирование**: Loguru

### Вспомогательные технологии:
- **Веб-админка**: Flask + Flask-Admin + Flask-Security
- **Кэширование**: Redis (опционально)
- **Мониторинг**: Prometheus + Grafana
- **Контейнеризация**: Docker + Docker Compose
- **Аналитика**: Amplitude/PostHog/Google Analytics (интеграция)
- **Обработка ошибок**: Sentry

### Ключевые библиотеки (из requirements.txt):
- aiogram==3.23.0 - асинхронный фреймворк Telegram Bot API
- asyncpg==0.31.0 - асинхронный драйвер PostgreSQL
- sqlalchemy==2.0.44 - ORM для работы с БД
- pydantic==2.12.5 - валидация данных
- aiohttp==3.13.2 - асинхронные HTTP-запросы
- alembic==1.17.2 - система миграций БД
- redis==7.1.0 - клиент Redis для кэширования
- babel==2.17.0 - интернационализация (i18n)

## Структура проекта

```
Telegrambot_test/
├── bot/                          # Основной код Telegram-бота
│   ├── __main__.py              # Точка входа, инициализация бота
│   ├── core/                    # Ядро приложения
│   │   ├── config.py            # Конфигурация через Pydantic Settings
│   │   └── loader.py            # Инициализация компонентов
│   ├── handlers/                # Обработчики сообщений и команд
│   │   ├── start.py             # /start команда
│   │   ├── menu.py              # Главное меню
│   │   ├── admins/              # Админские команды
│   │   └── sections/            # Функциональные разделы
│   │       ├── prayer_schedule_handlers.py  # Расписание намазов
│   │       ├── settings_handlers.py         # Настройки пользователя
│   │       ├── profile_handlers.py          # Профиль пользователя
│   │       ├── events_calendar_handlers.py  # Календарь событий
│   │       └── education_handlers.py        # Исламские знания
│   ├── services/                # Бизнес-логика
│   │   ├── prayer_service.py    # Сервис расчета времени намазов (API Aladhan)
│   │   ├── scheduler.py         # Планировщик уведомлений
│   │   ├── calendar_service.py  # Работа с календарем событий
│   │   └── event_service.py     # Управление событиями
│   ├── middlewares/             # Мидлвари (порядок выполнения)
│   │   ├── database.py          # Управление сессиями БД
│   │   ├── i18n.py              # Локализация (поддержка 5 языков)
│   │   ├── auth.py              # Аутентификация
│   │   ├── throttling.py        # Ограничение запросов
│   │   └── prometheus.py        # Сбор метрик для мониторинга
│   ├── keyboards/               # Клавиатуры (inline и reply)
│   │   ├── inline/              # Inline-кнопки
│   │   │   ├── prayers.py       # Клавиатуры для раздела намазов
│   │   │   ├── settings.py      # Настройки
│   │   │   └── events.py        # События
│   │   └── reply/               # Reply-клавиатуры
│   ├── states/                  # Состояния FSM (Finite State Machine)
│   │   ├── prayer.py            # Состояния для работы с намазами
│   │   ├── settings.py          # Состояния настроек
│   │   ├── profile.py           # Состояния профиля
│   │   └── events.py            # Состояния событий
│   ├── locales/                 # Локализация (gettext)
│   │   ├── ru/LC_MESSAGES/      # Русский
│   │   ├── en/LC_MESSAGES/      # Английский
│   │   ├── ar/LC_MESSAGES/      # Арабский
│   │   ├── tt/LC_MESSAGES/      # Татарский
│   │   └── ba/LC_MESSAGES/      # Башкирский
│   └── filters/                 # Фильтры для обработчиков
│       ├── admin.py             # Фильтр администраторов
│       └── number.py            # Фильтр числовых значений
├── database/                    # Работа с базой данных
│   ├── models.py               # SQLAlchemy модели (User, Settings, CommunityEvent и др.)
│   ├── crud.py                 # CRUD операции
│   ├── engine.py               # Создание асинхронного движка
│   └── migration.py            # Кастомные миграции
├── migrations/                  # Alembic миграции (версионирование БД)
│   └── versions/               # Файлы миграций
├── admin/                       # Веб-админка на Flask
│   ├── app.py                  # Flask приложение
│   ├── views/                  # Представления (Users view)
│   └── templates/              # HTML шаблоны
├── configs/                     # Конфигурации для мониторинга
│   ├── prometheus/             # Prometheus конфигурация
│   └── grafana/                # Grafana дашборды
├── scripts/                     # Вспомогательные скрипты
├── docs/                       # Документация
└── logs/                       # Логи приложения
```

## Функционал

### Основные функции бота:

1. **Расписание намазов**:
   - Расчет времени 5 ежедневных намазов (Фаджр, Зухр, Аср, Магриб, Иша)
   - Поддержка 4 мазхабов (Ханафи, Шафии, Малики, Ханбали)
   - Географическая привязка к городам (особенно городам Башкирии)
   - Отображение расписания на сегодня и на неделю
   - API интеграция с Aladhan.com

2. **Уведомления о намазах**:
   - Автоматические напоминания за 15 минут до каждого намаза
   - Индивидуальные настройки (какие намазы уведомлять)
   - Учет часового пояса пользователя
   - Планировщик на основе APScheduler

3. **Календарь исламских событий**:
   - Создание и управление событиями (лекции, встречи, курсы)
   - Регистрация на события
   - Предложение событий пользователями
   - Уведомления о предстоящих событиях

4. **Профиль пользователя**:
   - Регистрация при первом использовании /start
   - Настройки языка (5 языков)
   - Выбор города для расчета намазов
   - Настройки уведомлений
   - Статистика (дней подряд использования)

5. **Исламские знания**:
   - Хадисы
   - Цитаты из Корана
   - Образовательные материалы
   - Информация о халальных местах (рестораны, магазины)

6. **Административные функции**:
   - Панель администратора в Telegram (/admin)
   - Веб-админка на Flask (управление пользователями)
   - Экспорт пользователей в CSV/Excel
   - Статистика использования бота

7. **Многоязычная поддержка**:
   - Автоматическое определение языка
   - Ручной выбор языка в настройках
   - Полная локализация интерфейса

### API эндпоинты и модули:

- **Prayer API**: Интеграция с Aladhan.com для получения времени намазов
- **Calendar API**: Управление событиями и регистрациями
- **User API**: CRUD операции с пользователями и настройками
- **Notification API**: Система уведомлений через Telegram
- **Admin API**: Административные функции и статистика

## Ключевой код

### Точка входа (`bot/__main__.py`):
```python
async def main() -> None:
    # Инициализация Sentry для мониторинга ошибок
    if settings.SENTRY_DSN:
        sentry_sdk.init(...)
    
    # Настройка логирования в файл
    logger.add("logs/telegram_bot.log", ...)
    
    # Регистрация обработчиков startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск в режиме polling или webhook
    if settings.USE_WEBHOOK:
        await setup_webhook()
    else:
        await dp.start_polling(bot)
```

### Сервис расчета намазов (`bot/services/prayer_service.py`):
```python
class PrayerService:
    BASE_URL = "http://api.aladhan.com/v1"
    
    @classmethod
    async def get_today_timings(cls, city: str, madhab: str = "Hanafi") -> Optional[Dict]:
        """Получить время намазов на сегодня через внешний API"""
        params = {
            "city": city,
            "country": "Russia",
            "method": cls.MADHAB_METHODS.get(madhab, 1),
            "date": date.today().isoformat(),
        }
        # Асинхронный HTTP-запрос к API
        data = await cls._make_request(f"{cls.BASE_URL}/timingsByCity", params)
        return data
```

### Модели базы данных (`database/models.py`):
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

class Settings(Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    language: Mapped[str] = mapped_column(String, default="ru")
    notification_on: Mapped[bool] = mapped_column(Boolean, default=True)
    madhab: Mapped[str] = mapped_column(String, default="Hanafi")
    # Настройки уведомлений для каждого намаза
    notify_fajr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_dhuhr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_asr: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_maghrib: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_isha: Mapped[bool] = mapped_column(Boolean, default=True)
```

### Обработчик расписания намазов (`bot/handlers/sections/prayer_schedule_handlers.py`):
```python
@router.message(F.text == __("Расписание намазов"))
async def handle_prayer_text(message: Message, session: AsyncSession) -> None:
    """Обработка запроса расписания намазов"""
    user = await get_user_by_telegram_id(session, message.from_user.id)
    settings = await get_user_settings(session, user.id)
    
    # Получение времени намазов через сервис
    timings_data = await PrayerService.get_today_timings(
        city=user.city or "Moscow",
        madhab=settings.madhab or "Hanafi"
    )
    
    # Форматирование и отправка ответа
    message_text = format_prayer_times(timings_data, user.city, settings.madhab)
    await message.answer(message_text, reply_markup=get_prayer_main_kb())
```

### Конфигурация приложения (`bot/core/config.py`):
```python
class Settings(BotSettings, DBSettings, CacheSettings):
    DEBUG: bool = False
    SENTRY_DSN: str | None = None
    AMPLITUDE_API_KEY: str
    ADMINS: list[int] = []  # Список ID администраторов
    
    @property
    def database_url(self) -> URL | str:
        """Формирование URL для подключения к PostgreSQL"""
        if self.DB_PASS:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

## Архитектурные особенности

1. **Асинхронная архитектура**: Все операции I/O выполняются асинхронно через async/await.
2. **Модульная структура**: Четкое разделение на handlers, services, middlewares.
3. **Многоязычность**: Полная поддержка i18n через gettext/Babel.
4. **Мониторинг**: Встроенная интеграция с Prometheus для сбора метрик.
5. **Контейнеризация**: Готовые Dockerfile и docker-compose.yml для развертывания.
6. **Масштабируемость**: Поддержка Redis для кэширования и горизонтального масштабирования.
7. **Безопасность**: Валидация через Pydantic, защита от флуда через throttling middleware.

## Состояние проекта

Проект находится в активной разработке с акцентом на:
- Улучшение точности расчета времени намазов
- Расширение географии поддерживаемых городов
- Добавление новых образовательных материалов
- Улучшение пользовательского интерфейса
- Оптимизация производительности

Проект имеет хорошую документацию (README.md, PROJECT_OVERVIEW.md, ARCHITECTURE_OVERVIEW.md) и готов к промышленному использованию.

---
*Отчет подготовлен для передачи контекста AI-ассистенту Gemini*
*Дата анализа: 11.12.2025*
*Версия проекта: 2.4.0 (на основе pyproject.toml)*
