# Техническая спецификация 003: Модуль "Обучение"

## Обзор
Модуль "Обучение" предоставляет пользователям структурированную систему курсов по исламским наукам, тестирование знаний, отслеживание прогресса и доступ к образовательным материалам. Модуль включает каталог курсов, активные и завершенные курсы, тесты, статистику прогресса и AI-помощника для обучения.

## Стек технологий
- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.0
- PostgreSQL
- Alembic (миграции)
- Redis (кеширование прогресса)
- APScheduler (напоминания о занятиях)

## 1. Дизайн базы данных

### 1.1 Новые модели SQLAlchemy

#### Модель Course (Курс)
```python
from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Boolean, func, Text, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CourseStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel, native_enum=False), default=CourseLevel.BEGINNER)
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus, native_enum=False), default=CourseStatus.PUBLISHED)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=10)  # Оценочное время прохождения
    order_index: Mapped[int] = mapped_column(Integer, default=0)  # Для сортировки в каталоге
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    modules: Mapped[list["CourseModule"]] = relationship(
        "CourseModule", back_populates="course", cascade="all, delete-orphan", order_by="CourseModule.order_index"
    )
    user_progress: Mapped[list["UserCourseProgress"]] = relationship(
        "UserCourseProgress", back_populates="course", cascade="all, delete-orphan"
    )
```

#### Модель CourseModule (Модуль курса)
```python
class CourseModule(Base):
    __tablename__ = "course_modules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), default="text")  # text, video, audio, quiz
    content_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # URL к медиа-контенту
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # Текстовый контент
    duration_minutes: Mapped[int] = mapped_column(Integer, default=15)  # Длительность в минутах
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="modules")
    user_progress: Mapped[list["UserModuleProgress"]] = relationship(
        "UserModuleProgress", back_populates="module", cascade="all, delete-orphan"
    )
```

#### Модель UserCourseProgress (Прогресс пользователя по курсу)
```python
class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, completed, paused, dropped
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100%
    completed_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    total_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course", back_populates="user_progress")
    module_progress: Mapped[list["UserModuleProgress"]] = relationship(
        "UserModuleProgress", back_populates="course_progress", cascade="all, delete-orphan"
    )
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course'),)
```

#### Модель UserModuleProgress (Прогресс по модулю)
```python
class UserModuleProgress(Base):
    __tablename__ = "user_module_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("course_modules.id"), nullable=False)
    course_progress_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_course_progress.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="not_started")  # not_started, in_progress, completed
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    module: Mapped["CourseModule"] = relationship("CourseModule", back_populates="user_progress")
    course_progress: Mapped["UserCourseProgress"] = relationship(
        "UserCourseProgress", back_populates="module_progress", foreign_keys=[course_progress_id]
    )
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'module_id', name='uq_user_module'),)
```

#### Модель Test (Тест)
```python
class Test(Base):
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id"), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")  # easy, medium, hard
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = без ограничения
    passing_score: Mapped[int] = mapped_column(Integer, default=70)  # Проходной балл в процентах
    max_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = неограниченно
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    course: Mapped["Course"] = relationship("Course")
    questions: Mapped[list["TestQuestion"]] = relationship(
        "TestQuestion", back_populates="test", cascade="all, delete-orphan", order_by="TestQuestion.order_index"
    )
    user_results: Mapped[list["UserTestResult"]] = relationship(
        "UserTestResult", back_populates="test", cascade="all, delete-orphan"
    )
```

#### Модель TestQuestion (Вопрос теста)
```python
class TestQuestion(Base):
    __tablename__ = "test_questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="single_choice")  # single_choice, multiple_choice, text
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="questions")
    options: Mapped[list["TestOption"]] = relationship(
        "TestOption", back_populates="question", cascade="all, delete-orphan", order_by="TestOption.order_index"
    )
```

#### Модель TestOption (Вариант ответа)
```python
class TestOption(Base):
    __tablename__ = "test_options"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)  # Объяснение почему ответ правильный/неправильный
    
    # Relationships
    question: Mapped["TestQuestion"] = relationship("TestQuestion", back_populates="options")
```

#### Модель UserTestResult (Результат теста пользователя)
```python
class UserTestResult(Base):
    __tablename__ = "user_test_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)  # В процентах
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    test: Mapped["Test"] = relationship("Test", back_populates="user_results")
    answers: Mapped[list["UserTestAnswer"]] = relationship(
        "UserTestAnswer", back_populates="test_result", cascade="all, delete-orphan"
    )
    
    # Unique constraint для попытки
    __table_args__ = (UniqueConstraint('user_id', 'test_id', 'attempt_number', name='uq_user_test_attempt'),)
```

#### Модель UserTestAnswer (Ответ пользователя на вопрос)
```python
class UserTestAnswer(Base):
    __tablename__ = "user_test_answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_result_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_test_results.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_questions.id"), nullable=False)
    selected_option_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON массив ID выбранных вариантов
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # Для текстовых ответов
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    points_earned: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    test_result: Mapped["UserTestResult"] = relationship("UserTestResult", back_populates="answers")
    question: Mapped["TestQuestion"] = relationship("TestQuestion")
```

#### Обновление модели User
```python
# Добавить в существующую модель User следующие поля:
class User(Base):
    __tablename__ = "users"
    # ... существующие поля ...
    
    # Новые поля для обучения
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)  # beginner, intermediate, advanced
    total_courses_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    learning_streak_days: Mapped[int] = mapped_column(Integer, default=0)  # Отдельная серия для обучения
    last_learning_activity: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships для обучения
    course_progress: Mapped[list["UserCourseProgress"]] = relationship("UserCourseProgress", back_populates="user")
    module_progress: Mapped[list["UserModuleProgress"]] = relationship("UserModuleProgress", back_populates="user")
    test_results: Mapped[list["UserTestResult"]] = relationship("UserTestResult", back_populates="user")
```

#### Обновление модели Settings
```python
# Добавить в существующую модель Settings следующие поля:
class Settings(Base):
    __tablename__ = "settings"
    # ... существующие поля ...
    
    # Новые поля для уведомлений об обучении
    notify_course_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_test_results: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_courses: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Настройки обучения
    daily_learning_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_learning_time: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "morning", "afternoon", "evening"
    auto_continue_courses: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 1.2 Миграции
```bash
# Создать миграцию
alembic revision --autogenerate -m "add_education_module_tables"

# Применить миграцию
alembic upgrade head
```

## 2. Состояния FSM

### 2.1 CourseLearningState
```python
from aiogram.fsm.state import State, StatesGroup

class CourseLearningState(StatesGroup):
    """Состояния FSM для прохождения курса"""
    selecting_course = State()
    viewing_module = State()
    answering_quiz = State()
    taking_notes = State()
```

### 2.2 TestTakingState
```python
class TestTakingState(StatesGroup):
    """Состояния FSM для прохождения теста"""
    selecting_test = State()
    answering_question = State()
    reviewing_results = State()
```

### 2.3 EducationSettingsState
```python
class EducationSettingsState(StatesGroup):
    """Состояния FSM для настройки обучения"""
    setting_daily_goal = State()
    setting_preferred_time = State()
    configuring_notifications = State()
```

## 3. Клавиатуры и интерфейс

### 3.1 Основное меню обучения
```python
def get_education_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню раздела 'Обучение'"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📚 КАТАЛОГ КУРСОВ",
            callback_data="edu:catalog"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔄 Активные курсы",
            callback_data="edu:active"
        ),
        InlineKeyboardButton(
            text="✅ Завершенные курсы",
            callback_data="edu:completed"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📝 Тесты",
            callback_data="edu:tests"
        ),
        InlineKeyboardButton(
            text="🎙️ Эфиры",
            callback_data="edu:streams"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📊 Прогресс",
            callback_data="edu:progress"
        ),
        InlineKeyboardButton(
            text="🔍 Помощник",
            callback_data="edu:assistant"
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

### 3.2 Клавиатура активных курсов
```python
def get_active_courses_keyboard(active_courses: list[UserCourseProgress]) -> InlineKeyboardMarkup:
    """Клавиатура для активных курсов"""
    builder = InlineKeyboardBuilder()
    
    for progress in active_courses:
        course = progress.course
        progress_text = f"{progress.progress_percentage:.0f}%"
        builder.row(
            InlineKeyboardButton(
                text=f"{course.title} ({progress_text})",
                callback_data=f"edu:course:{course.id}"
            )
        )
    
    # Кнопки действий
    builder.row(
        InlineKeyboardButton(text="▶ Продолжить", callback_data="edu:continue"),
        InlineKeyboardButton(text="📊 Прогресс", callback_data="edu:detailed_progress")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="edu:main")
    )
    
    return builder.as_markup()
```

### 3.3 Клавиатура завершенных курсов
```python
def get_completed_courses_keyboard(completed_courses: list[UserCourseProgress]) -> InlineKeyboardMarkup:
    """Клавиатура для завершенных курсов"""
    builder = InlineKeyboardBuilder()
    
    for progress in completed_courses:
        course = progress.course
        medal = "🥇" if progress.score > 90 else "🥈" if progress.score > 70 else "🥉"
        builder.row(
            InlineKeyboardButton(
                text=f"{medal} {course.title}",
                callback_data=f"edu:review:{course.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔄 Повторить материал", callback_data="edu:review_all")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="edu:main")
    )
    
    return builder.as_markup()
```

### 3.4 Клавиатура тестов
```python
def get_tests_keyboard(user_results: list[UserTestResult]) -> InlineKeyboardMarkup:
    """Клавиатура для раздела тестов"""
    builder = InlineKeyboardBuilder()
    
    for result in user_results:
        test = result.test
        score_text = f"{result.score:.0f}%"
        builder.row(
            InlineKeyboardButton(
                text=f"{test.title} ({score_text})",
                callback_data=f"edu:test_result:{result.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="📝 Пройти новый тест", callback_data="edu:new_test"),
        InlineKeyboardButton(text="📊 Мои результаты", callback_data="edu:my_results")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="edu:main")
    )
    
    return builder.as_markup()
```

### 3.5 Клавиатура прогресса
```python
def get_progress_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для раздела прогресса"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📈 Детальная статистика", callback_data="edu:detailed_stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="📅 За месяц", callback_data="edu:month_stats"),
        InlineKeyboardButton(text="📅 За год", callback_data="edu:year_stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="🏆 Достижения", callback_data="edu:achievements")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="edu:main")
    )
    
    return builder.as_markup()
```

### 3.6 Клавиатура прохождения теста
```python
def get_test_question_keyboard(question: TestQuestion, question_number: int, total_questions: int) -> InlineKeyboardMarkup:
    """Клавиатура для вопроса теста"""
    builder = InlineKeyboardBuilder()
    
    # Варианты ответов
    for option in question.options:
        builder.row(
            InlineKeyboardButton(
                text=f"{option.option_text}",
                callback_data=f"edu:answer:{question.id}:{option.id}"
            )
        )
    
    # Навигация
    if question_number > 1:
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"edu:prev_question:{question.id}")
        )
    
    if question_number < total_questions:
        builder.row(
            InlineKeyboardButton(text="Далее ➡️", callback_data=f"edu:next_question:{question.id}")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="✅ Завершить тест", callback_data="edu:finish_test")
        )
    
    builder.row(
        InlineKeyboardButton(text="❌ Отменить тест", callback_data="edu:cancel_test")
    )
    
    return builder.as_markup()
```

## 4. Функциональные требования

### 4.1 Точка входа
- Пользователь нажимает "Обучение" в главном меню (Reply Button)
- Бот отправляет приветственное сообщение с описанием раздела и главным меню:
  ```
  📚 ОБУЧЕНИЕ
  
  Добро пожаловать в раздел обучения! Здесь вы найдете:
  • Курсы по основам ислама
  • Интерактивные тесты
  • Отслеживание прогресса
  • AI-помощник для вопросов
  
  Выберите раздел:
  ```

### 4.2 Активные курсы (`🔄 Активные курсы`)

#### 4.2.1 Отображение активных курсов
- Заголовок: "🎯 АКТИВНЫЕ КУРСЫ (X):" где X - количество активных курсов
- Для каждого курса отображается:
  - Название курса
  - Прогресс в процентах
  - Количество пройденных/всего модулей (например: "3/5 modules")
- Пример отображения (как в требованиях):
  ```
  🎯 АКТИВНЫЕ КУРСЫ (2):
  
  1. "Основы ислама" (Progress: 65%, 3/5 modules)
  2. "Намаз для начинающих" (Progress: 40%, 2/5 modules)
  ```
- Кнопки: `[▶ Продолжить]` `[📊 Прогресс]` + `[Back]`

#### 4.2.2 Продолжение курса
- При нажатии на курс или кнопку "Продолжить":
  - Определяется следующий непройденный модуль
  - Отображается содержимое модуля (текст/видео/аудио)
  - Предлагается кнопка "✅ Завершить модуль"
  - После завершения обновляется прогресс

### 4.3 Завершенные курсы (`✅ Завершенные курсы`)

#### 4.3.1 Отображение завершенных курсов
- Заголовок: "✅ Завершенные курсы (X)" где X - количество курсов
- Для каждого курса отображается название с медалью (🥇, 🥈, 🥉) в зависимости от результата
- Пример отображения:
  ```
  ✅ Завершенные курсы (5)
  
  🥇 Введение в ислам
  🥈 Фикх очищения
  🥉 История пророков
  ```
- Кнопки: `[🔄 Повторить материал]` + `[Back]`

#### 4.3.2 Повторение материала
- При нажатии "Повторить материал":
  - Открывается меню выбора модулей для повторения
  - Пользователь может выбрать любой модуль из курса
  - Отображается оригинальный контент модуля

### 4.4 Тесты (`📝 Тесты`)

#### 4.4.1 Отображение тестов
- Для каждого теста отображается:
  - Название теста
  - Лучший результат пользователя в процентах
- Пример отображения:
  ```
  📝 ТЕСТЫ
  
  Основы веры (85%)
  Намаз (70%)
  Пост (90%)
  ```
- Кнопки: `[📝 Пройти новый тест]` `[📊 Мои результаты]` + `[Back]`

#### 4.4.2 Прохождение нового теста
- При нажатии "Пройти новый тест":
  - Отображается список доступных тестов
  - Пользователь выбирает тест
  - Запускается FSM для прохождения теста
  - Вопросы отображаются по одному с вариантами ответов
  - По завершении показывается результат

### 4.5 Прогресс (`📊 Прогресс`)

#### 4.5.1 Отображение статистики
- Заголовок с общей статистикой:
  ```
  📊 ВАШ ПРОГРЕСС
  
  За месяц:
  • Курсов завершено: 2
  • Тестов пройдено: 5
  • Уровень: 12
  • Время обучения: 15ч 30м
  ```
- Кнопки: `[📈 Детальная статистика]` + `[Back]`

#### 4.5.2 Детальная статистика
- При нажатии "Детальная статистика":
  - Отображается график прогресса за последние 30 дней
  - Список последних активностей
  - Достижения и бейджи

### 4.6 Заглушки (Stubs)
- Каталог курсов (`📚 КАТАЛОГ КУРСОВ`): "Раздел в разработке"
- Эфиры (`🎙️ Эфиры`): "Раздел в разработке"
- Помощник (`🔍 Помощник`): "Раздел в разработке"

## 5. Детали реализации

### 5.1 Новые файлы

#### Обработчики
```
bot/handlers/sections/education/
├── __init__.py
├── main_handlers.py           # Главное меню и навигация
├── course_handlers.py         # Обработчики курсов
├── test_handlers.py           # Обработчики тестов
├── progress_handlers.py       # Обработчики прогресса
└── stub_handlers.py           # Заглушки (каталог, эфиры, помощник)
```

#### Сервисы
```
bot/services/
├── education_service.py       # Логика работы с обучением
├── course_service.py          # Бизнес-логика курсов
├── test_service.py            # Бизнес-логика тестов
└── progress_service.py        # Расчет и анализ прогресса
```

#### Клавиатуры
```
bot/keyboards/inline/
├── education.py               # Основные клавиатуры обучения
├── course_keyboards.py        # Клавиатуры для курсов
└── test_keyboards.py          # Клавиатуры для тестов
```

#### Состояния
```
bot/states/
├── education.py               # FSM состояния для обучения
└── __init__.py                # Экспорт состояний
```

### 5.2 Сервис обучения
```python
# bot/services/education_service.py
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional

class EducationService:
    @staticmethod
    async def get_user_active_courses(session: AsyncSession, user_id: int) -> list[UserCourseProgress]:
        """Получает активные курсы пользователя"""
        stmt = (
            select(UserCourseProgress)
            .join(Course)
            .where(
                and_(
                    UserCourseProgress.user_id == user_id,
                    UserCourseProgress.status == "active",
                    Course.status == CourseStatus.PUBLISHED
                )
            )
            .order_by(UserCourseProgress.last_accessed_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_completed_courses(session: AsyncSession, user_id: int) -> list[UserCourseProgress]:
        """Получает завершенные курсы пользователя"""
        stmt = (
            select(UserCourseProgress)
            .join(Course)
            .where(
                and_(
                    UserCourseProgress.user_id == user_id,
                    UserCourseProgress.status == "completed",
                    Course.status == CourseStatus.PUBLISHED
                )
            )
            .order_by(UserCourseProgress.completed_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_test_results(session: AsyncSession, user_id: int, limit: int = 10) -> list[UserTestResult]:
        """Получает результаты тестов пользователя"""
        stmt = (
            select(UserTestResult)
            .join(Test)
            .where(
                and_(
                    UserTestResult.user_id == user_id,
                    Test.is_active == True
                )
            )
            .order_by(UserTestResult.completed_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def calculate_user_progress(session: AsyncSession, user_id: int) -> dict:
        """Рассчитывает общий прогресс пользователя"""
        # Статистика за месяц
        month_ago = datetime.now() - timedelta(days=30)
        
        # Курсы завершено за месяц
        courses_completed = await session.execute(
            select(func.count(UserCourseProgress.id))
            .where(
                and_(
                    UserCourseProgress.user_id == user_id,
                    UserCourseProgress.status == "completed",
                    UserCourseProgress.completed_at >= month_ago
                )
            )
        )
        
        # Тестов пройдено за месяц
        tests_completed = await session.execute(
            select(func.count(UserTestResult.id))
            .where(
                and_(
                    UserTestResult.user_id == user_id,
                    UserTestResult.completed_at >= month_ago
                )
            )
        )
        
        # Общее время обучения за месяц
        learning_time = await session.execute(
            select(func.sum(UserModuleProgress.time_spent_minutes))
            .where(
                and_(
                    UserModuleProgress.user_id == user_id,
                    UserModuleProgress.completed_at >= month_ago
                )
            )
        )
        
        return {
            "courses_completed": courses_completed.scalar() or 0,
            "tests_completed": tests_completed.scalar() or 0,
            "learning_time_minutes": learning_time.scalar() or 0,
            "level": await EducationService.calculate_user_level(session, user_id)
        }
    
    @staticmethod
    async def calculate_user_level(session: AsyncSession, user_id: int) -> int:
        """Рассчитывает уровень пользователя на основе прогресса"""
        # Базовая логика: 1 уровень за каждый завершенный курс + 0.5 уровня за каждый пройденный тест
        courses_completed = await session.execute(
            select(func.count(UserCourseProgress.id))
            .where(
                and_(
                    UserCourseProgress.user_id == user_id,
                    UserCourseProgress.status == "completed"
                )
            )
        )
        
        tests_passed = await session.execute(
            select(func.count(UserTestResult.id))
            .where(
                and_(
                    UserTestResult.user_id == user_id,
                    UserTestResult.passed == True
                )
            )
        )
        
        base_level = (courses_completed.scalar() or 0) * 1
        test_bonus = (tests_passed.scalar() or 0) * 0.5
        
        return int(base_level + test_bonus) + 1  # +1 для начального уровня
```

### 5.3 Сервис курсов
```python
# bot/services/course_service.py
class CourseService:
    @staticmethod
    async def start_course(session: AsyncSession, user_id: int, course_id: int) -> Optional[UserCourseProgress]:
        """Начинает курс для пользователя"""
        # Проверяем, не начат ли уже курс
        existing = await session.execute(
            select(UserCourseProgress)
            .where(
                and_(
                    UserCourseProgress.user_id == user_id,
                    UserCourseProgress.course_id == course_id
                )
            )
        )
        
        if existing.scalar_one_or_none():
            return None
        
        # Получаем курс
        course = await session.get(Course, course_id)
        if not course or course.status != CourseStatus.PUBLISHED:
            return None
        
        # Создаем запись о прогрессе
        total_modules = len(course.modules)
        progress = UserCourseProgress(
            user_id=user_id,
            course_id=course_id,
            status="active",
            progress_percentage=0.0,
            completed_modules_count=0,
            total_modules_count=total_modules
        )
        
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
        
        return progress
    
    @staticmethod
    async def complete_module(
        session: AsyncSession,
        user_id: int,
        module_id: int
    ) -> Optional[UserModuleProgress]:
        """Отмечает модуль как завершенный"""
        # Находим прогресс по модулю
        stmt = select(UserModuleProgress).where(
            and_(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module_id
            )
        )
        result = await session.execute(stmt)
        module_progress = result.scalar_one_or_none()
        
        if not module_progress:
            # Создаем новую запись
            module = await session.get(CourseModule, module_id)
            if not module:
                return None
            
            # Находим прогресс по курсу
            course_progress = await session.execute(
                select(UserCourseProgress).where(
                    and_(
                        UserCourseProgress.user_id == user_id,
                        UserCourseProgress.course_id == module.course_id
                    )
                )
            )
            course_progress_obj = course_progress.scalar_one_or_none()
            
            module_progress = UserModuleProgress(
                user_id=user_id,
                module_id=module_id,
                course_progress_id=course_progress_obj.id if course_progress_obj else None,
                status="completed",
                completed_at=datetime.now()
            )
            session.add(module_progress)
        else:
            # Обновляем существующую запись
            module_progress.status = "completed"
            module_progress.completed_at = datetime.now()
        
        # Обновляем прогресс по курсу
        if module_progress.course_progress_id:
            course_progress = await session.get(UserCourseProgress, module_progress.course_progress_id)
            if course_progress:
                # Пересчитываем прогресс
                completed_modules = await session.execute(
                    select(func.count(UserModuleProgress.id)).where(
                        and_(
                            UserModuleProgress.course_progress_id == course_progress.id,
                            UserModuleProgress.status == "completed"
                        )
                    )
                )
                completed_count = completed_modules.scalar() or 0
                
                course_progress.completed_modules_count = completed_count
                if course_progress.total_modules_count > 0:
                    course_progress.progress_percentage = (
                        completed_count / course_progress.total_modules_count
                    ) * 100
                
                # Если все модули завершены, отмечаем курс как завершенный
                if completed_count >= course_progress.total_modules_count:
                    course_progress.status = "completed"
                    course_progress.completed_at = datetime.now()
        
        await session.commit()
        await session.refresh(module_progress)
        return module_progress
    
    @staticmethod
    async def get_next_module(
        session: AsyncSession,
        user_id: int,
        course_id: int
    ) -> Optional[CourseModule]:
        """Получает следующий непройденный модуль курса"""
        # Получаем все модули курса
        stmt = select(CourseModule).where(
            CourseModule.course_id == course_id
        ).order_by(CourseModule.order_index)
        
        result = await session.execute(stmt)
        modules = result.scalars().all()
        
        # Находим первый непройденный модуль
        for module in modules:
            module_progress = await session.execute(
                select(UserModuleProgress).where(
                    and_(
                        UserModuleProgress.user_id == user_id,
                        UserModuleProgress.module_id == module.id,
                        UserModuleProgress.status == "completed"
                    )
                )
            )
            if not module_progress.scalar_one_or_none():
                return module
        
        return None
```

### 5.4 Сервис тестов
```python
# bot/services/test_service.py
class TestService:
    @staticmethod
    async def start_test(session: AsyncSession, user_id: int, test_id: int) -> Optional[UserTestResult]:
        """Начинает тест для пользователя"""
        # Проверяем максимальное количество попыток
        test = await session.get(Test, test_id)
        if not test or not test.is_active:
            return None
        
        if test.max_attempts:
            current_attempts = await session.execute(
                select(func.count(UserTestResult.id)).where(
                    and_(
                        UserTestResult.user_id == user_id,
                        UserTestResult.test_id == test_id
                    )
                )
            )
            if (current_attempts.scalar() or 0) >= test.max_attempts:
                return None
        
        # Создаем запись о результате теста
        total_questions = len(test.questions)
        test_result = UserTestResult(
            user_id=user_id,
            test_id=test_id,
            total_questions=total_questions,
            attempt_number=await TestService.get_next_attempt_number(session, user_id, test_id)
        )
        
        session.add(test_result)
        await session.commit()
        await session.refresh(test_result)
        
        return test_result
    
    @staticmethod
    async def get_next_attempt_number(
        session: AsyncSession,
        user_id: int,
        test_id: int
    ) -> int:
        """Получает номер следующей попытки"""
        stmt = select(func.max(UserTestResult.attempt_number)).where(
            and_(
                UserTestResult.user_id == user_id,
                UserTestResult.test_id == test_id
            )
        )
        result = await session.execute(stmt)
        max_attempt = result.scalar() or 0
        return max_attempt + 1
    
    @staticmethod
    async def submit_answer(
        session: AsyncSession,
        test_result_id: int,
        question_id: int,
        selected_option_ids: list[int] = None,
        answer_text: str = None
    ) -> Optional[UserTestAnswer]:
        """Сохраняет ответ пользователя на вопрос"""
        # Получаем вопрос
        question = await session.get(TestQuestion, question_id)
        if not question:
            return None
        
        # Проверяем правильность ответа
        is_correct = False
        points_earned = 0.0
        
        if question.question_type == "single_choice" and selected_option_ids:
            # Для одиночного выбора проверяем, что выбран правильный вариант
            correct_option = await session.execute(
                select(TestOption).where(
                    and_(
                        TestOption.question_id == question_id,
                        TestOption.is_correct == True
                    )
                )
            )
            correct_option_obj = correct_option.scalar_one_or_none()
            
            if correct_option_obj and selected_option_ids[0] == correct_option_obj.id:
                is_correct = True
                points_earned = question.points
        
        elif question.question_type == "multiple_choice" and selected_option_ids:
            # Для множественного выбора проверяем, что выбраны все правильные варианты
            correct_options = await session.execute(
                select(TestOption).where(
                    and_(
                        TestOption.question_id == question_id,
                        TestOption.is_correct == True
                    )
                )
            )
            correct_option_ids = {opt.id for opt in correct_options.scalars().all()}
            selected_set = set(selected_option_ids)
            
            if correct_option_ids == selected_set:
                is_correct = True
                points_earned = question.points
        
        # Создаем или обновляем запись ответа
        existing_answer = await session.execute(
            select(UserTestAnswer).where(
                and_(
                    UserTestAnswer.test_result_id == test_result_id,
                    UserTestAnswer.question_id == question_id
                )
            )
        )
        answer = existing_answer.scalar_one_or_none()
        
        if answer:
            # Обновляем существующий ответ
            answer.selected_option_ids = json.dumps(selected_option_ids) if selected_option_ids else None
            answer.answer_text = answer_text
            answer.is_correct = is_correct
            answer.points_earned = points_earned
        else:
            # Создаем новый ответ
            answer = UserTestAnswer(
                test_result_id=test_result_id,
                question_id=question_id,
                selected_option_ids=json.dumps(selected_option_ids) if selected_option_ids else None,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned
            )
            session.add(answer)
        
        await session.commit()
        await session.refresh(answer)
        return answer
    
    @staticmethod
    async def finish_test(session: AsyncSession, test_result_id: int) -> Optional[UserTestResult]:
        """Завершает тест и рассчитывает результат"""
        test_result = await session.get(UserTestResult, test_result_id)
        if not test_result:
            return None
        
        # Получаем все ответы
        answers = await session.execute(
            select(UserTestAnswer).where(
                UserTestAnswer.test_result_id == test_result_id
            )
        )
        answers_list = answers.scalars().all()
        
        # Рассчитываем результат
        total_points = sum(answer.points_earned for answer in answers_list)
        max_points = test_result.total_questions  # Предполагаем 1 балл за вопрос
        
        test_result.correct_answers = sum(1 for answer in answers_list if answer.is_correct)
        test_result.score = (total_points / max_points) * 100 if max_points > 0 else 0
        test_result.passed = test_result.score >= test_result.test.passing_score
        test_result.completed_at = datetime.now()
        
        await session.commit()
        await session.refresh(test_result)
        return test_result
```

## 6. Угловые случаи и обработка ошибок

### 6.1 Прерывание курса
- **Проблема:** Пользователь прерывает прохождение курса на середине
- **Решение:**
  1. Сохранять прогресс после каждого модуля
  2. При возобновлении предлагать продолжить с последнего непройденного модуля
  3. Добавлять кнопку "Начать заново" для сброса прогресса

### 6.2 Истечение времени теста
- **Проблема:** Пользователь не успевает завершить тест за отведенное время
- **Решение:**
  1. Отслеживать время начала теста
  2. При истечении времени автоматически завершать тест
  3. Учитывать только ответы, данные до истечения времени

### 6.3 Потеря соединения
- **Проблема:** Пользователь теряет соединение во время прохождения курса/теста
- **Решение:**
  1. Реализовать автосохранение прогресса
  2. При восстановлении соединения предлагать продолжить с последней сохраненной точки
  3. Хранить состояние FSM в Redis для восстановления

### 6.4 Конфликт данных
- **Проблема:** Одновременное обновление прогресса с разных устройств
- **Решение:**
  1. Использовать optimistic locking с версиями записей
  2. При конфликте предлагать пользователю выбрать актуальную версию
  3. Логировать конфликты для анализа

### 6.5 Недостаток контента
- **Проблема:** В курсе недостаточно модулей или тестов
- **Решение:**
  1. Проверять минимальные требования при публикации курса
  2. Отмечать курсы как "в разработке"
  3. Уведомлять администраторов о необходимости дополнения контента

## 7. Пошаговый план реализации

### Этап 1: Подготовка базы данных (2-3 дня)
1. Добавить новые модели в `database/models.py`
2. Обновить существующие модели `User` и `Settings`
3. Создать миграцию Alembic
4. Применить миграцию к базе данных
5. Создать начальные данные (seed data) для тестирования

### Этап 2: Сервисный слой (3-4 дня)
1. Создать `bot/services/education_service.py`
2. Создать `bot/services/course_service.py`
3. Создать `bot/services/test_service.py`
4. Создать `bot/services/progress_service.py`
5. Реализовать базовые CRUD операции и бизнес-логику

### Этап 3: Состояния FSM (1-2 дня)
1. Создать `bot/states/education.py`
2. Определить `CourseLearningState`, `TestTakingState`, `EducationSettingsState`
3. Интегрировать с существующей системой состояний
4. Реализовать middleware для восстановления состояния

### Этап 4: Клавиатуры (2-3 дня)
1. Создать `bot/keyboards/inline/education.py`
2. Создать `bot/keyboards/inline/course_keyboards.py`
3. Создать `bot/keyboards/inline/test_keyboards.py`
4. Реализовать все клавиатуры из спецификации
5. Добавить поддержку локализации

### Этап 5: Обработчики (4-5 дней)
1. Создать структуру `bot/handlers/sections/education/`
2. Реализовать `main_handlers.py` (главное меню)
3. Реализовать `course_handlers.py` (курсы)
4. Реализовать `test_handlers.py` (тесты)
5. Реализовать `progress_handlers.py` (прогресс)
6. Реализовать `stub_handlers.py` (заглушки)
7. Интегрировать с главным меню бота

### Этап 6: Планировщик уведомлений (1-2 дня)
1. Расширить `bot/services/scheduler.py`
2. Добавить задачу `check_learning_reminders`
3. Реализовать логику напоминаний о занятиях
4. Реализовать уведомления о новых курсах и тестах

### Этап 7: Тестирование (3-4 дня)
1. Модульные тесты для сервисов
2. Интеграционные тесты для обработчиков
3. Тестирование FSM состояний
4. Тестирование уведомлений и напоминаний
5. Тестирование угловых случаев

### Этап 8: Деплой и мониторинг (1-2 дня)
1. Обновить зависимости (`requirements.txt`)
2. Проверить миграции на production-like среде
3. Настроить мониторинг ошибок и метрик
4. Подготовить документацию для пользователей
5. Создать руководство для администраторов по добавлению курсов

## 8. Текстовое содержимое (русский язык)

### 8.1 Сообщения для пользователей

#### Главное меню обучения
```
📚 ОБУЧЕНИЕ

Добро пожаловать в раздел обучения! Здесь вы найдете:
• Курсы по основам ислама
• Интерактивные тесты
• Отслеживание прогресса
• AI-помощник для вопросов

Выберите раздел:
```

#### Активные курсы
```
🎯 АКТИВНЫЕ КУРСЫ (2):

1. "Основы ислама" (Progress: 65%, 3/5 modules)
2. "Намаз для начинающих" (Progress: 40%, 2/5 modules)

Выберите курс для продолжения или используйте кнопки ниже.
```

#### Завершенные курсы
```
✅ Завершенные курсы (5)

🥇 Введение в ислам
🥈 Фикх очищения
🥉 История пророков

Поздравляем с завершением курсов! 🎉
```

#### Тесты
```
📝 ТЕСТЫ

Основы веры (85%)
Намаз (70%)
Пост (90%)

Проверьте свои знания или пройдите новый тест!
```

#### Прогресс
```
📊 ВАШ ПРОГРЕСС

За месяц:
• Курсов завершено: 2
• Тестов пройдено: 5
• Уровень: 12
• Время обучения: 15ч 30м

Продолжайте в том же духе! 💪
```

#### Заглушки
```
🚧 РАЗДЕЛ В РАЗРАБОТКЕ

Функция "Каталог курсов" находится в разработке.
Мы работаем над добавлением новых курсов!

Ожидайте обновления в ближайшее время. ⏳
```

### 8.2 Уведомления

#### Напоминание о занятии
```
🔔 Напоминание об обучении

Не забывайте про ежедневное обучение!
Сегодня вы еще не занимались.

Рекомендуемое время: 30 минут
Текущая серия: 5 дней подряд

Продолжайте серию! 📚
```

#### Завершение курса
```
🎉 Поздравляем!

Вы успешно завершили курс:
"Основы ислама"

Результат: 92% 🥇
Время прохождения: 8 часов

Поздравляем с отличным результатом! 🎓
```

#### Результат теста
```
📊 РЕЗУЛЬТАТ ТЕСТА

Тест: "Основы веры"
Ваш результат: 85% ✅

Правильных ответов: 17/20
Время: 12 минут 30 секунд

Отличная работа! Продолжайте в том же духе! 💪
```

#### Достижение нового уровня
```
🏆 НОВЫЙ УРОВЕНЬ!

Поздравляем! Вы достигли уровня 12!

Ваши достижения:
• Завершено курсов: 5
• Пройдено тестов: 12
• Общее время обучения: 45 часов

Следующая цель: уровень 13 🚀
```

## 9. Заключение

Данная спецификация предоставляет полное техническое описание модуля "Обучение" для Islamic Telegram Bot. Реализация включает:

1. **Структурированную систему курсов** с модулями различного типа (текст, видео, аудио, тесты)
2. **Комплексную систему тестирования** с поддержкой различных типов вопросов
3. **Детальное отслеживание прогресса** с статистикой и достижениями
4. **Гибкую систему уведомлений** о занятиях и напоминаниях
5. **Масштабируемую архитектуру** для будущего расширения (каталог курсов, эфиры, AI-помощник)

### 9.1 Ключевые особенности
- **Интуитивный интерфейс**: Соответствует предоставленным mock-данным и требованиям UI/UX
- **Гибкая архитектура**: Легко расширяется новыми типами контента и функциями
- **Надежное хранение данных**: Полная история прогресса пользователей
- **Поддержка многопользовательской работы**: Оптимизировано для одновременной работы тысяч пользователей
- **Интеграция с существующей системой**: Использует текущую инфраструктуру бота (база данных, миграции, планировщик)

### 9.2 Будущие расширения
1. **Каталог курсов**: Система поиска и фильтрации курсов
2. **Эфиры**: Прямые трансляции и вебинары
3. **AI-помощник**: Интеграция с LLM для ответов на вопросы
4. **Социальные функции**: Обсуждения курсов, рейтинги, лидерборды
5. **Мобильное приложение**: Нативная реализация для iOS/Android

### 9.3 Критерии успеха
- **Пользовательский опыт**: Удобная навигация, понятный прогресс, мотивирующие уведомления
- **Производительность**: Быстрая загрузка контента, отзывчивый интерфейс
- **Надежность**: Минимальное количество ошибок, автоматическое восстановление после сбоев
- **Масштабируемость**: Поддержка роста пользовательской базы без деградации производительности

Спецификация достаточно детализирована для реализации командой разработчиков и учитывает все основные требования бизнес-логики, угловые случаи и технические ограничения.

---
*Документ подготовлен: 11.12.2025*  
*Версия спецификации: 1.0*  
*Статус: Готов к реализации*  
*Автор: Senior Full-Stack Python Developer / System Architect*
