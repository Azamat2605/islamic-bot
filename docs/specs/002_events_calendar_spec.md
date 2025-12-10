# Техническая спецификация 002: Календарь событий

## Обзор
Функция "Календарь событий" предоставляет пользователям возможность просматривать мероприятия общины и религиозные события, записываться на мероприятия, предлагать новые события и настраивать уведомления.

## Стек технологий
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.0
- PostgreSQL
- Alembic (миграции)
- APScheduler (уведомления)
- hijri-converter (для исламского календаря)

## 1. Дизайн базы данных

### 1.1 Новые модели SQLAlchemy

#### Модель CommunityEvent
```python
from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Boolean, func, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

class EventType(enum.Enum):
    LECTURE = "lecture"
    MEETING = "meeting"
    COURSE = "course"
    OTHER = "other"

class EventStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FINISHED = "finished"

class CommunityEvent(Base):
    __tablename__ = "community_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), default=EventType.LECTURE)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.ACTIVE)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="event", cascade="all, delete-orphan"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
```

#### Модель EventRegistration
```python
class RegistrationStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITING = "waiting"  # для листа ожидания, если превышен max_participants

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_events.id"), nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus), default=RegistrationStatus.CONFIRMED)
    registered_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    event: Mapped["CommunityEvent"] = relationship("CommunityEvent", back_populates="registrations")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='uq_user_event'),)
```

#### Модель EventProposal
```python
class ProposalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EventProposal(Base):
    __tablename__ = "event_proposals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewed_by])
```

#### Обновление модели Settings
```python
# Добавить в существующую модель Settings следующие поля:
class Settings(Base):
    __tablename__ = "settings"
    # ... существующие поля ...
    
    # Новые поля для уведомлений о религиозных событиях
    notify_1day_before: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_day: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_juma: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Поля для уведомлений о мероприятиях
    notify_event_reminder: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_event_changes: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 1.2 Миграции
```bash
# Создать миграцию
alembic revision --autogenerate -m "add_events_calendar_tables"

# Применить миграцию
alembic upgrade head
```

## 2. Состояния FSM

### 2.1 EventProposalState
```python
from aiogram.fsm.state import State, StatesGroup

class EventProposalState(StatesGroup):
    """Состояния FSM для предложения события"""
    entering_title = State()
    entering_date = State()
    entering_description = State()
    confirming = State()
```

### 2.2 EventRegistrationState
```python
class EventRegistrationState(StatesGroup):
    """Состояния FSM для регистрации на событие"""
    confirming_registration = State()
    entering_notes = State()  # для дополнительной информации
```

## 3. Клавиатуры и интерфейс

### 3.1 Основное меню календаря
```python
def get_events_calendar_main_kb() -> InlineKeyboardMarkup:
    """Главное меню календаря событий"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🎪 Мероприятия общины",
            callback_data="events_community"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📅 Религиозные события",
            callback_data="events_religious"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 В главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()
```

### 3.2 Меню мероприятий общины
```python
def get_community_events_kb(events: list[CommunityEvent], page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура списка мероприятий с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки мероприятий (максимум 5 на страницу)
    for event in events[page*5:(page+1)*5]:
        event_date = event.start_time.strftime("%d.%m %H:%M")
        builder.row(
            InlineKeyboardButton(
                text=f"{event_date} - {event.title[:20]}...",
                callback_data=f"event_details:{event.id}"
            )
        )
    
    # Пагинация
    if page > 0:
        builder.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"events_page:{page-1}"
            )
        )
    
    if len(events) > (page + 1) * 5:
        builder.row(
            InlineKeyboardButton(
                text="➡️ Вперед",
                callback_data=f"events_page:{page+1}"
            )
        )
    
    # Дополнительные опции
    builder.row(
        InlineKeyboardButton(
            text="📝 Мои записи",
            callback_data="my_registrations"
        ),
        InlineKeyboardButton(
            text="➕ Предложить",
            callback_data="propose_event"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="events_calendar"
        )
    )
    
    return builder.as_markup()
```

### 3.3 Меню религиозных событий
```python
def get_religious_events_kb(current_month: int, current_year: int) -> InlineKeyboardMarkup:
    """Клавиатура религиозных событий с навигацией по месяцам"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⏩ Ближайшие",
            callback_data="upcoming_events"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔔 Напоминания",
            callback_data="event_reminders"
        ),
        InlineKeyboardButton(
            text="📜 Праздники на год",
            callback_data="yearly_events"
        )
    )
    
    # Навигация по месяцам
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Пред. месяц",
            callback_data=f"prev_month:{current_month}:{current_year}"
        ),
        InlineKeyboardButton(
            text="След. месяц ➡️",
            callback_data=f"next_month:{current_month}:{current_year}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="events_calendar"
        )
    )
    
    return builder.as_markup()
```

### 3.4 Клавиатура настроек напоминаний
```python
def get_event_reminders_kb(settings: Settings) -> InlineKeyboardMarkup:
    """Клавиатура настроек напоминаний (чекбокс стиль)"""
    builder = InlineKeyboardBuilder()
    
    # Тогглы уведомлений
    reminders = [
        ("notify_1day_before", "За 1 день", settings.notify_1day_before),
        ("notify_on_day", "В день события", settings.notify_on_day),
        ("notify_juma", "Напоминания о Джуме", settings.notify_juma),
    ]
    
    for field, display_name, is_enabled in reminders:
        status = "✅" if is_enabled else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {display_name}",
                callback_data=f"toggle_reminder:{field}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="events_religious"
        )
    )
    
    return builder.as_markup()
```

## 4. Функциональные требования

### 4.1 Точка входа
- Пользователь нажимает "Календарь событий" в главном меню
- Бот отправляет приветственное сообщение с выбором категории:
  ```
  🕌 Календарь событий
  
  Выберите раздел:
  ```

### 4.2 Мероприятия общины (🎪 Мероприятия общины)

#### 4.2.1 Просмотр мероприятий
- Отображается список предстоящих мероприятий (Дата, Время, Место)
- Для каждого мероприятия кнопка `[Подробнее / Записаться]`
- Пагинация при превышении 5 мероприятий на странице

#### 4.2.2 Мои записи (`[ 📝 Мои записи ]`)
- Проверка БД на наличие активных записей пользователя
- Если записей нет: "У вас пока нет активных записей"
- Если есть: список с кнопкой `[❌ Отменить запись]` для каждой

#### 4.2.3 Предложить событие (`[ ➕ Предложить ]`)
- **FSM Implementation:**
  1. Шаг 1: Запрос названия события
  2. Шаг 2: Запрос даты/времени (с валидацией формата)
  3. Шаг 3: Запрос описания
  4. Шаг 4: Подтверждение и сохранение
- **Действие:** Сохранение в таблицу `EventProposal` со статусом 'pending'
- **Уведомление администратора:** Отправка сообщения админам с кнопками `[Approve]` / `[Reject]`

### 4.3 Религиозные события (📅 Религиозные события)

#### 4.3.1 Представление календаря
- Расчет дат Хиджры (использовать библиотеку `hijri-converter`)
- Отображение событий текущего месяца
- **Пагинация:** `[ ⬅️ Prev Month ]` | `[ Next Month ➡️ ]` (редактирование сообщения, а не повторная отправка)

#### 4.3.2 Ближайшие события (`[ ⏩ Ближайшие ]`)
- Расчет дней до следующего крупного события (Рамадан, Курбан-байрам, Ураза-байрам)
- Отображение обратного отсчета

#### 4.3.3 Настройки напоминаний (`[ 🔔 Напоминания ]`)
- Тогглы (стиль чекбокса в инлайн-клавиатуре):
  - `[ ✅/❌ За 1 день ]`
  - `[ ✅/❌ В день события ]`
  - `[ ✅/❌ Напоминания о Джуме ]`
- Сохранение в БД

#### 4.3.4 Годовой список (`[ 📜 Праздники на год ]`)
- Генерация текстового списка ИЛИ отправка предопределенного статического PDF/изображения

## 5. Детали реализации

### 5.1 Новые файлы

#### Обработчики
```
bot/handlers/events/
├── __init__.py
├── community_events.py      # Обработчики мероприятий общины
├── religious_events.py      # Обработчики религиозных событий
├── event_proposals.py       # Обработчики предложений событий
└── event_registrations.py   # Обработчики регистраций
```

#### Сервисы
```
bot/services/
├── calendar_service.py      # Логика работы с календарем
├── event_service.py         # Бизнес-логика мероприятий
└── hijri_service.py         # Конвертация дат Хиджры
```

#### Клавиатуры
```
bot/keyboards/inline/
├── events.py                # Основные клавиатуры событий
└── event_reminders.py       # Клавиатуры напоминаний
```

#### Состояния
```
bot/states/
├── events.py                # FSM состояния для событий
└── __init__.py              # Экспорт состояний
```

### 5.2 Сервис календаря
```python
# bot/services/calendar_service.py
from datetime import datetime, timedelta
from hijri_converter import convert

class CalendarService:
    @staticmethod
    async def get_hijri_date(gregorian_date: datetime) -> str:
        """Конвертирует григорианскую дату в дату Хиджры"""
        hijri = convert.Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        return f"{hijri.day} {hijri.month_name()} {hijri.year} г.х."
    
    @staticmethod
    async def get_upcoming_religious_events() -> list[dict]:
        """Возвращает список предстоящих религиозных событий"""
        today = datetime.now()
        events = []
        
        # Пример: расчет дат Рамадана и праздников
        # Здесь должна быть реальная логика расчета
        
        return events
    
    @staticmethod
    async def get_month_events(month: int, year: int) -> list[dict]:
        """Возвращает события для указанного месяца"""
        # Логика получения событий месяца
        pass
```

### 5.3 Планировщик уведомлений
```python
# Добавить в bot/services/scheduler.py
async def check_event_reminders() -> None:
    """Проверяет события и отправляет уведомления"""
    try:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # 1. Уведомления за 1 день до события
        if any_user_wants_1day_notification():
            events_tomorrow = await get_events_for_date(tomorrow)
            for event in events_tomorrow:
                await send_1day_notification(event)
        
        # 2. Уведомления в день события
        events_today = await get_events_for_date(today)
        for event in events_today:
            await send_same_day_notification(event)
        
        # 3. Уведомления о Джуме (пятница)
        if today.weekday() == 4:  # Пятница
            await send_juma_notification()
            
    except Exception as e:
        logger.error(f"Ошибка в check_event_reminders: {e}")

# Добавить задачу в планировщик
scheduler.add_job(
    check_event_reminders,
    'cron',
    hour=9,  # Проверка в 9:00 каждый день
    id='event_notifications',
    replace_existing=True
)
```

### 5.4 Сервис мероприятий
```python
# bot/services/event_service.py
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

class EventService:
    @staticmethod
    async def get_upcoming_events(session: AsyncSession, limit: int = 10) -> list[CommunityEvent]:
        """Получает предстоящие мероприятия"""
        stmt = (
            select(CommunityEvent)
            .where(
                and_(
                    CommunityEvent.status == EventStatus.ACTIVE,
                    CommunityEvent.start_time > datetime.now()
                )
            )
            .order_by(CommunityEvent.start_time)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_registrations(session: AsyncSession, user_id: int) -> list[EventRegistration]:
        """Получает регистрации пользователя"""
        stmt = (
            select(EventRegistration)
            .join(CommunityEvent)
            .where(
                and_(
                    EventRegistration.user_id == user_id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED,
                    CommunityEvent.status == EventStatus.ACTIVE,
                    CommunityEvent.start_time > datetime.now()
                )
            )
            .order_by(CommunityEvent.start_time)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def register_for_event(session: AsyncSession, user_id: int, event_id: int) -> bool:
        """Регистрирует пользователя на мероприятие"""
        # Проверка, не зарегистрирован ли уже
        existing = await session.execute(
            select(EventRegistration)
            .where(
                and_(
                    EventRegistration.user_id == user_id,
                    EventRegistration.event_id == event_id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED
                )
            )
        )
        
        if existing.scalar_one_or_none():
            return False  # Уже зарегистрирован
        
        # Проверка максимального количества участников
        event = await session.get(CommunityEvent, event_id)
        if event.max_participants:
            current_count = await session.execute(
                select(func.count(EventRegistration.id))
                .where(
                    and_(
                        EventRegistration.event_id == event_id,
                        EventRegistration.status == RegistrationStatus.CONFIRMED
                    )
                )
            )
            if current_count.scalar() >= event.max_participants:
                # Добавить в лист ожидания
                registration = EventRegistration(
                    user_id=user_id,
                    event_id=event_id,
                    status=RegistrationStatus.WAITING
                )
                await session.commit()
                return True
        
        # Обычная регистрация
        registration = EventRegistration(
            user_id=user_id,
            event_id=event_id,
            status=RegistrationStatus.CONFIRMED
        )
        session.add(registration)
        await session.commit()
        return True
```

## 6. Угловые случаи и обработка ошибок

### 6.1 Удаление мероприятия
- **Проблема:** Что делать, если мероприятие удалено, но у пользователей есть активные регистрации?
- **Решение:** При удалении мероприятия:
  1. Изменить статус мероприятия на `CANCELLED` вместо физического удаления
  2. Отправить уведомления всем зарегистрированным пользователям
  3. Обновить статус регистраций на `CANCELLED`
  4. Предложить альтернативные мероприятия

### 6.2 Превышение максимального количества участников
- **Проблема:** Пользователь пытается зарегистрироваться на заполненное мероприятие
- **Решение:** 
  1. Добавить в лист ожидания (`WAITING` статус)
  2. Уведомить пользователя о позиции в очереди
  3. Автоматически переводить в `CONFIRMED` при появлении мест

### 6.3 Конфликт времени
- **Проблема:** Пользователь регистрируется на два мероприятия в одно время
- **Решение:** 
  1. Проверять конфликты при регистрации
  2. Предупреждать пользователя о конфликте
  3. Предлагать выбрать одно из мероприятий

### 6.4 Невалидные даты предложений
- **Проблема:** Пользователь предлагает событие с прошедшей датой
- **Решение:**
  1. Валидация даты на этапе ввода
  2. Минимальная дата = текущая дата + 1 день
  3. Максимальная дата = текущая дата + 1 год

### 6.5 Проблемы с уведомлениями
- **Проблема:** Пользователь не получает уведомления
- **Решение:**
  1. Логирование всех попыток отправки
  2. Ретри логика при ошибках сети
  3. Отслеживание статуса доставки

## 7. Пошаговый план реализации

### Этап 1: Подготовка базы данных (1-2 дня)
1. Добавить новые модели в `database/models.py`
2. Создать миграцию Alembic
3. Применить миграцию к базе данных
4. Обновить модель `Settings` новыми полями

### Этап 2: Сервисный слой (2-3 дня)
1. Создать `bot/services/calendar_service.py`
2. Создать `bot/services/event_service.py`
3. Создать `bot/services/hijri_service.py`
4. Реализовать базовые CRUD операции

### Этап 3: Состояния FSM (1 день)
1. Создать `bot/states/events.py`
2. Определить `EventProposalState` и `EventRegistrationState`
3. Интегрировать с существующей системой состояний

### Этап 4: Клавиатуры (1-2 дня)
1. Создать `bot/keyboards/inline/events.py`
2. Создать `bot/keyboards/inline/event_reminders.py`
3. Реализовать все клавиатуры из спецификации
4. Добавить поддержку локализации

### Этап 5: Обработчики (3-4 дня)
1. Создать структуру `bot/handlers/events/`
2. Реализовать `community_events.py`
3. Реализовать `religious_events.py`
4. Реализовать `event_proposals.py`
5. Реализовать `event_registrations.py`
6. Интегрировать с главным меню

### Этап 6: Планировщик уведомлений (1-2 дня)
1. Расширить `bot/services/scheduler.py`
2. Добавить задачу `check_event_reminders`
3. Реализовать логику отправки уведомлений
4. Протестировать временные зоны

### Этап 7: Тестирование (2-3 дня)
1. Модульные тесты для сервисов
2. Интеграционные тесты для обработчиков
3. Тестирование уведомлений
4. Тестирование угловых случаев

### Этап 8: Деплой и мониторинг (1 день)
1. Обновить зависимости (`requirements.txt`)
2. Проверить миграции на production-like среде
3. Настроить мониторинг ошибок
4. Подготовить документацию для пользователей

## 8. Текстовое содержимое (русский язык)

### 8.1 Сообщения для пользователей

#### Главное меню календаря
```
🕌 Календарь событий

Выберите раздел:
```

#### Мероприятия общины
```
🎪 Мероприятия общины

Предстоящие мероприятия:
1. 15.12 18:30 - Лекция "Основы ислама" (Москва)
2. 17.12 19:00 - Встреча общины (Онлайн)
3. 20.12 14:00 - Курс арабского языка (Центр)

Выберите мероприятие для подробностей или записи.
```

#### Нет активных записей
```
📝 Мои записи

У вас пока нет активных записей на мероприятия.

Хотите посмотреть предстоящие события?
```

#### Предложение события
```
➕ Предложить мероприятие

Пожалуйста, введите название вашего мероприятия:
```

#### Религиозные события
```
📅 Религиозные события

Мухаррам 1446 г.х.
────────────────
1 Мухаррам: Новый год по Хиджре
10 Мухаррам: День Ашура

Используйте кнопки ниже для навигации.
```

#### Ближайшие события
```
⏩ Ближайшие события

До начала Рамадана: 45 дней
До Курбан-байрама: 120 дней

Подготовьтесь заранее! 🕌
```

### 8.2 Уведомления

#### За 1 день до события
```
🔔 Напоминание о мероприятии

Завтра, 15 декабря в 18:30
Лекция "Основы ислама"

Место: Московская соборная мечеть
Не забудьте подготовиться! 📚
```

#### В день события
```
🕌 Сегодня мероприятие!

Сегодня в 18:30
Лекция "Основы ислама"

Место: Московская соборная мечеть
Ждем вас! 🙏
```

#### Уведомление о Джуме
```
📿 Напоминание о Джуме

Сегодня пятница - день congregational prayer!

Рекомендуемое время:
- Полуденная молитва: 13:00
- Проповедь: 13:30

Постарайтесь посетить мечеть. 🕌
```

## 9. Заключение

Данная спецификация предоставляет полное техническое описание функции "Календарь событий" для Islamic Telegram Bot. Реализация включает:

1. **Полноценную систему мероприятий** с регистрацией и управлением
2. **Интеграцию с исламским календарем** для религиозных событий
3. **Гибкую систему уведомлений** с настройками пользователя
4. **Административный интерфейс** для модерации предложений
5. **Масштабируемую архитектуру** для будущих расширений

Спецификация достаточно детализирована для реализации junior-разработчиком и учитывает все основные угловые случаи и требования бизнес-логики.

---
*Документ подготовлен: 10.12.2025*  
*Версия спецификации: 1.0*  
*Статус: Готов к реализации*
