# Полное техническое задание по изменению и реализации кнопки "Обучение"

## Обзор

Данный документ представляет собой полное техническое задание для реализации расширенного функционала кнопки "Обучение" в Islamic Telegram Bot. На основе предоставленного описания экранов и анализа текущей реализации, документ детализирует архитектуру, функциональные требования и план реализации.

## Текущее состояние

### Что уже реализовано:
1. **Модели базы данных** - все необходимые модели для курсов, модулей, тестов и прогресса пользователей
2. **Миграции** - добавлены поля в таблицы `users` и `settings` для обучения
3. **Сервисный слой** - `EducationService` с базовыми методами получения данных
4. **Обработчики** - `education_handlers.py` с основными разделами
5. **Клавиатуры** - `education.py` с основными меню
6. **Интеграция с главным меню** - кнопка "Обучение" в основном меню

### Что требует доработки:
1. **Полная реализация всех 7 экранов** согласно описанию
2. **FSM состояния** для прохождения курсов и тестов
3. **Расширенная бизнес-логика** для расчета прогресса, тестирования
4. **Интеграция с медиа-контентом** (видео, аудио, Telegraph)
5. **AI-помощник** с ограниченным промптом
6. **Система уведомлений** и напоминаний

## Архитектура решения

### 1. Модели базы данных (дополнения)

#### 1.1 Новые поля для существующих моделей

**Модель UserCourseProgress** - добавить поле `is_completed`:
```python
is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
```

**Модель CourseModule** - добавить поля для тестов:
```python
has_test: Mapped[bool] = mapped_column(Boolean, default=False)
test_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tests.id"), nullable=True)
```

**Модель Test** - добавить поле для связи с модулем:
```python
module_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("course_modules.id"), nullable=True)
```

#### 1.2 Новая модель для эфиров (Streams)
```python
class Stream(Base):
    __tablename__ = "streams"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    speaker: Mapped[str] = mapped_column(String(100), nullable=True)
    scheduled_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    stream_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_upcoming: Mapped[bool] = mapped_column(Boolean, default=True)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    reminders: Mapped[list["StreamReminder"]] = relationship(
        "StreamReminder", back_populates="stream", cascade="all, delete-orphan"
    )

class StreamReminder(Base):
    __tablename__ = "stream_reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    stream_id: Mapped[int] = mapped_column(Integer, ForeignKey("streams.id"), nullable=False)
    reminded_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    stream: Mapped["Stream"] = relationship("Stream", back_populates="reminders")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'stream_id', name='uq_user_stream_reminder'),)
```

#### 1.3 Новая модель для сертификатов
```python
class Certificate(Base):
    __tablename__ = "certificates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    certificate_url: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course_certificate'),)
```

### 2. Состояния FSM (расширение)

#### 2.1 CourseLearningState (расширенный)
```python
class CourseLearningState(StatesGroup):
    """Состояния FSM для прохождения курса"""
    selecting_course = State()
    viewing_module = State()
    watching_video = State()
    listening_audio = State()
    reading_telegraph = State()
    answering_quiz = State()
    taking_notes = State()
    module_completed = State()
```

#### 2.2 TestTakingState (расширенный)
```python
class TestTakingState(StatesGroup):
    """Состояния FSM для прохождения теста"""
    selecting_test = State()
    answering_question = State()
    question_explanation = State()
    reviewing_results = State()
    test_completed = State()
```

#### 2.3 StreamState
```python
class StreamState(StatesGroup):
    """Состояния FSM для работы с эфирами"""
    browsing_streams = State()
    viewing_stream = State()
    setting_reminder = State()
    watching_recording = State()
```

#### 2.4 AIAssistantState
```python
class AIAssistantState(StatesGroup):
    """Состояния FSM для AI-помощника"""
    waiting_for_query = State()
    processing_query = State()
    showing_answer = State()
```

### 3. Сервисный слой (расширение)

#### 3.1 EducationService (дополнения)

**Методы для расчета прогресса:**
```python
@staticmethod
async def calculate_overall_progress(session: AsyncSession, user_id: int) -> float:
    """Рассчитывает общий прогресс по формуле: (пройденные уроки / все уроки) * 100"""
    # Всего уроков в базе
    total_lessons = await session.execute(select(func.count(CourseModule.id)))
    total = total_lessons.scalar() or 1
    
    # Пройденные уроки пользователя
    completed_lessons = await session.execute(
        select(func.count(UserModuleProgress.id)).where(
            and_(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.status == "completed"
            )
        )
    )
    completed = completed_lessons.scalar() or 0
    
    return (completed / total) * 100

@staticmethod
async def get_last_activity(session: AsyncSession, user_id: int) -> Dict[str, any]:
    """Получает последнюю активность пользователя"""
    stmt = select(UserModuleProgress).where(
        UserModuleProgress.user_id == user_id
    ).order_by(UserModuleProgress.completed_at.desc()).limit(1)
    
    result = await session.execute(stmt)
    progress = result.scalar_one_or_none()
    
    if progress:
        module = await session.get(CourseModule, progress.module_id)
        course = await session.get(Course, module.course_id) if module else None
        
        return {
            "course_title": course.title if course else "Неизвестный курс",
            "module_title": module.title if module else "Неизвестный урок",
            "module_number": module.order_index if module else 0,
            "completed_at": progress.completed_at
        }
    
    return None
```

#### 3.2 StreamService
```python
class StreamService:
    """Сервис для работы с эфирами"""
    
    @staticmethod
    async def get_upcoming_streams(session: AsyncSession, limit: int = 5) -> List[Dict]:
        """Получает предстоящие эфиры"""
        now = datetime.now()
        stmt = select(Stream).where(
            and_(
                Stream.scheduled_time > now,
                Stream.is_upcoming == True
            )
        ).order_by(Stream.scheduled_time).limit(limit)
        
        result = await session.execute(stmt)
        streams = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "title": s.title,
                "speaker": s.speaker,
                "scheduled_time": s.scheduled_time,
                "duration_minutes": s.duration_minutes,
                "time_until": s.scheduled_time - now
            }
            for s in streams
        ]
    
    @staticmethod
    async def get_stream_recordings(session: AsyncSession, page: int = 1, per_page: int = 10) -> List[Dict]:
        """Получает архив записей эфиров с пагинацией"""
        offset = (page - 1) * per_page
        stmt = select(Stream).where(
            and_(
                Stream.recording_url.is_not(None),
                Stream.is_upcoming == False
            )
        ).order_by(Stream.scheduled_time.desc()).offset(offset).limit(per_page)
        
        result = await session.execute(stmt)
        streams = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "title": s.title,
                "speaker": s.speaker,
                "scheduled_time": s.scheduled_time,
                "recording_url": s.recording_url
            }
            for s in streams
        ]
```

#### 3.3 AIService
```python
class AIService:
    """Сервис для работы с AI-помощником"""
    
    SYSTEM_PROMPT = """Ты исламский ассистент. Отвечай только фактами из проверенных источников.
Правила:
1. Отвечай только на вопросы, связанные с исламом, Кораном, хадисами, историей
2. Не выноси фетвы (решения о халяле/хараме)
3. Не решай личные или семейные споры
4. Если вопрос сложный или требует фикх-анализа, отправляй к ученым
5. Используй только информацию из базы знаний бота
6. Будь краток и точен

Если вопрос вне компетенции, вежливо откажись отвечать."""

    @staticmethod
    async def process_query(query: str, user_context: Dict = None) -> str:
        """Обрабатывает запрос пользователя через AI"""
        # Здесь будет интеграция с OpenAI/Claude API
        # Пока заглушка
        if "аят" in query.lower() or "коран" in query.lower():
            return "В Коране сказано: \"Читай во имя Господа твоего, Который сотворил...\" (Сура Аль-Аляк, 96:1)"
        elif "хадис" in query.lower():
            return "Пророк Мухаммад (мир ему и благословение) сказал: \"Стремление к знаниям — обязанность каждого мусульманина\"."
        elif "термин" in query.lower():
            return "Иснад — это цепочка передатчиков хадиса от Пророка (мир ему и благословение) до составителя сборника."
        else:
            return "Я могу помочь с поиском аятов, объяснением терминов из уроков или переводом с арабского. Уточните ваш вопрос."
```

### 4. Клавиатуры (расширение)

#### 4.1 Главный дашборд (Экран 1)
```python
def get_education_dashboard_keyboard(
    user_name: str,
    overall_progress: float,
    last_activity: Dict = None
) -> InlineKeyboardMarkup:
    """Клавиатура для главного дашборда обучения"""
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки
    builder.row(
        InlineKeyboardButton(
            text="▶️ Продолжить обучение",
            callback_data=EducationCallback(action="continue_last").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📚 Каталог курсов",
            callback_data=EducationCallback(action="catalog").pack()
        ),
        InlineKeyboardButton(
            text="✅ Завершенные курсы",
            callback_data=EducationCallback(action="completed").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🧠 Раздел Тесты",
            callback_data=EducationCallback(action="tests").pack()
        ),
        InlineKeyboardButton(
            text="🎙 Эфиры и Записи",
            callback_data=EducationCallback(action="streams").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🤖 Исламский Помощник",
            callback_data=EducationCallback(action="assistant").pack()
        ),
        InlineKeyboardButton(
            text="🔙 В главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()
```

#### 4.2 Клавиатура урока (Экран 3)
```python
def get_lesson_keyboard(
    module_id: int,
    has_video: bool,
    has_audio: bool,
    has_telegraph: bool,
    has_test: bool
) -> InlineKeyboardMarkup:
    """Клавиатура для меню урока"""
    builder = InlineKeyboardBuilder()
    
    if has_video:
        builder.row(
            InlineKeyboardButton(
                text="▶️ Смотреть видео",
                callback_data=EducationCallback(action="watch_video", module_id=module_id).pack()
            )
        )
    
    if has_audio:
        builder.row(
            InlineKeyboardButton(
                text="🎧 Слушать аудио",
                callback_data=EducationCallback(action="listen_audio", module_id=module_id).pack()
            )
        )
    
    if has_telegraph:
        builder.row(
            InlineKeyboardButton(
                text="📝 Читать подробно (Telegraph)",
                callback_data=EducationCallback(action="read_telegraph", module_id=module_id).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Я изучил / Далее",
            callback_data=EducationCallback(action="complete_module", module_id=module_id).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=EducationCallback(action="back_to_course").pack()
        ),
        InlineKeyboardButton(
            text="Меню курса",
            callback_data=EducationCallback(action="course_menu").pack()
        )
    )
    
    return builder.as_markup()
```

#### 4.3 Клавиатура теста (Экран 4)
```python
def get_test_question_keyboard(
    question_id: int,
    options: List[Dict],
    question_number: int,
    total_questions: int,
    is_multiple_choice: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура для вопроса теста"""
    builder = InlineKeyboardBuilder()
    
    for option in options:
        emoji = "✅" if option.get("is_correct", False) else "○"
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {option['option_text']}",
                callback_data=EducationCallback(
                    action="select_answer",
                    question_id=question_id,
                    option_id=option["id"]
                ).pack()
            )
        )
    
    # Навигация
    nav_buttons = []
    if question_number > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=EducationCallback(
                    action="prev_question",
                    question_id=question_id
                ).pack()
            )
        )
    
    if question_number < total_questions:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Далее ➡️",
                callback_data=EducationCallback(
                    action="next_question",
                    question_id=question_id
                ).pack()
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(
                text="✅ Завершить тест",
                callback_data=EducationCallback(action="finish_test").pack()
            )
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить тест",
            callback_data=EducationCallback(action="cancel_test").pack()
        )
    )
    
    return builder.as_markup()
```

### 5. Обработчики (расширение)

#### 5.1 Главный дашборд (Экран 1)
```python
@router.callback_query(EducationCallback.filter(F.action == "dashboard"))
async def education_dashboard(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext
) -> None:
    """Главный дашборд обучения"""
    user_id = callback.from_user.id
    
    # Получаем данные пользователя
    user = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user_obj = user.scalar_one_or_none()
    
    # Рассчитываем общий прогресс
    overall_progress = await EducationService.calculate_overall_progress(session, user_id)
    
    # Получаем последнюю активность
    last_activity = await EducationService.get_last_activity(session, user_id)
    
    # Формируем сообщение
    progress_bar = "▓" * int(overall_progress / 10) + "░" * (10 - int(overall_progress / 10))
    
    text = _(
        "🕌 <b>ЦЕНТР ОБУЧЕНИЯ</b>\n\n"
        "<i>\"Стремление к знаниям — обязанность каждого мусульманина.\"</i>\n\n"
        "👤 <b>Студент:</b> {user_name}\n"
        "⭐ <b>Статус:</b> Ищущий знания\n"
        "📈 <b>Общий прогресс знаний:</b>\n"
        "{progress_bar} {progress_percentage:.0f}%\n\n"
    ).format(
        user_name=user_obj.full_name if user_obj else "Гость",
        progress_bar=progress_bar,
        progress_percentage=overall_progress
    )
    
    if last_activity:
        text += _(
            "<b>Последняя активность:</b>\n"
            "📖 Курс: \"{course_title}\"\n"
            "🔖 Урок {lesson_number}: \"{lesson_title}\"\n\n"
        ).format(
            course_title=last_activity["course_title"],
            lesson_number=last_activity["module_number"],
            lesson_title=last_activity["module_title"]
        )
    
    text += _("<i>Нажмите «Продолжить», чтобы вернуться к уроку.</i>")
    
    await callback.message.edit_text(
        text,
        reply_markup=get_education_dashboard_keyboard(
            user_name=user_obj.full_name if user_obj else "Гость",
            overall_progress=overall_progress,
            last_activity=last_activity
        ),
        parse_mode="HTML"
    )
    await callback.answer()
```

#### 5.2 Каталог курсов (Экран 2)
```python
@router.callback_query(EducationCallback.filter(F.action == "catalog"))
async def catalog_categories(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Каталог курсов - категории"""
    # Категории курсов
    categories = [
        {"id": 1, "name": "Акыда", "emoji": "📖", "count": 5},
        {"id": 2, "name": "Фикх", "emoji": "⚖️", "count": 8},
        {"id": 3, "name": "Коран", "emoji": "📜", "count": 6},
        {"id": 4, "name": "История", "emoji": "🏛️", "count": 4},
    ]
    
    lines = []
    for cat in categories:
        lines.append(f"{cat['emoji']} <b>{cat['name']}</b> ({cat['count']} курсов)")
    
    text = _(
        "📚 <b>КАТАЛОГ КУРСОВ</b>\n\n"
        "Выберите категорию:\n\n"
        "{categories}\n\n"
        "<i>Нажмите на категорию, чтобы увидеть список курсов.</i>"
    ).format(categories="\n".join(lines))
    
    # Создаем клавиатуру с категориями
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.row(
            InlineKeyboardButton(
                text=f"{cat['emoji']} {cat['name']}",
                callback_data=EducationCallback(action="category", category_id=cat["id"]).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=EducationCallback(action="dashboard").pack()
        )
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
```

#### 5.3 Прохождение урока (Экран 3)
```python
@router.callback_query(EducationCallback.filter(F.action == "view_module"))
async def view_module(
    callback: types.CallbackQuery,
    callback_data: EducationCallback,
    session: AsyncSession,
    state: FSMContext
) -> None:
    """Просмотр урока"""
    module_id = callback_data.module_id
    user_id = callback.from_user.id
    
    # Получаем данные модуля
    stmt = select(CourseModule).where(CourseModule.id == module_id)
    result = await session.execute(stmt)
    module = result.scalar_one_or_none()
    
    if not module:
        await callback.answer(_("Урок не найден."), show_alert=True)
        return
    
    # Получаем данные курса
    course = await session.get(Course, module.course_id)
    
    # Получаем прогресс пользователя по курсу
    stmt_progress = select(UserCourseProgress).where(
        and_(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_id == course.id
        )
    )
    result = await session.execute(stmt_progress)
    course_progress = result.scalar_one_or_none()
    
    # Рассчитываем прогресс курса
    completed_modules = course_progress.completed_modules_count if course_progress else 0
    total_modules = len(course.modules) if course else 1
    
    # Формируем сообщение
    text = _(
        "[📊 Прогресс курса: {completed}/{total}]\n"
        "🎯 <b>Урок {number}: \"{title}\"</b>\n\n"
    ).format(
        completed=completed_modules,
        total=total_modules,
        number=module.order_index,
        title=module.title
    )
    
    # Добавляем контент в зависимости от типа
    if module.content_type == "video" and module.content_url:
        text += _(
            "📹 <b>ВИДЕО-УРОК</b> [Длительность: {duration}]\n"
            "<i>Нажмите \"Смотреть\" ниже, бот пришлет видео.</i>\n\n"
        ).format(duration=f"{module.duration_minutes}:00")
    
    if module.content_type == "audio" and module.content_url:
        text += _(
            "🎧 <b>АУДИО-ЛЕКЦИЯ</b> [Длительность: {duration}]\n"
            "<i>Доступна для прослушивания в фоне.</i>\n\n"
        ).format(duration=f"{module.duration_minutes}:00")
    
    if module.content_text:
        text += _(
            "📋 <b>КОНСПЕКТ:</b>\n"
            "{content}\n\n"
        ).format(content=module.content_text[:500] + "..." if len(module.content_text) > 500 else module.content_text)
    
    # Добавляем цитату для примера
    text += _(
        "<blockquote>\"Именна иснад — это часть религии. "
        "Если бы не иснад, каждый говорил бы что хотел.\" (Ибн аль-Мубарак)</blockquote>\n\n"
        "💡 <b>ЗАПОМНИТЕ:</b>\n"
        "Хадис считается достоверным (Сахих) только при непрерывности цепочки передатчиков."
    )
    
    # Определяем доступные типы контента
    has_video = module.content_type == "video" and module.content_url
    has_audio = module.content_type == "audio" and module.content_url
    has_telegraph = module.content_text and len(module.content_text) > 1000
    has_test = module.has_test
    
    await callback.message.edit_text(
        text,
        reply_markup=get_lesson_keyboard(
            module_id=module_id,
            has_video=has_video,
            has_audio=has_audio,
            has_telegraph=has_telegraph,
            has_test=has_test
        ),
        parse_mode="HTML"
    )
    
    # Сохраняем состояние
    await state.set_state(CourseLearningState.viewing_module)
    await state.update_data(module_id=module_id, course_id=course.id)
    
    await callback.answer()
```

#### 5.4 Тестирование (Экран 4)
```python
@router.callback_query(EducationCallback.filter(F.action == "start_test"))
async def start_test(
    callback: types.CallbackQuery,
    callback_data: EducationCallback,
    session: AsyncSession,
    state: FSMContext
) -> None:
    """Начало теста"""
    test_id = callback_data.test_id
    user_id = callback.from_user.id
    
    # Получаем данные теста
    test = await session.get(Test, test_id)
    if not test or not test.is_active:
        await callback.answer(_("Тест не найден или неактивен."), show_alert=True)
        return
    
    # Проверяем максимальное количество попыток
    if test.max_attempts:
        stmt_attempts = select(func.count(UserTestResult.id)).where(
            and_(
                UserTestResult.user_id == user_id,
                UserTestResult.test_id == test_id
            )
        )
        result = await session.execute(stmt_attempts)
        attempts = result.scalar() or 0
        
        if attempts >= test.max_attempts:
            await callback.answer(
                _("Вы исчерпали максимальное количество попыток для этого теста."),
                show_alert=True
            )
            return
    
    # Создаем запись о результате теста
    test_result = UserTestResult(
        user_id=user_id,
        test_id=test_id,
        total_questions=len(test.questions),
        started_at=datetime.now()
    )
    
    session.add(test_result)
    await session.commit()
    await session.refresh(test_result)
    
    # Получаем первый вопрос
    questions = await EducationService.get_test_questions_with_options(test_id, session)
    if not questions:
        await callback.answer(_("В тесте нет вопросов."), show_alert=True)
        return
    
    first_question = questions[0]
    
    # Формируем сообщение
    text = _(
        "🧠 <b>ТЕСТ: {test_title}</b>\n\n"
        "Вопрос 1 из {total}:\n\n"
        "<b>{question_text}</b>\n\n"
        "Выберите правильный ответ:"
    ).format(
        test_title=test.title,
        total=len(questions),
        question_text=first_question["question_text"]
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_test_question_keyboard(
            question_id=first_question["id"],
            options=first_question["options"],
            question_number=1,
            total_questions=len(questions)
        ),
        parse_mode="HTML"
    )
    
    # Сохраняем состояние
    await state.set_state(TestTakingState.answering_question)
    await state.update_data(
        test_id=test_id,
        test_result_id=test_result.id,
        current_question=0,
        user_answers=[],
        start_time=datetime.now()
    )
    
    await callback.answer()
```

#### 5.5 Эфиры и записи (Экран 5)
```python
@router.callback_query(EducationCallback.filter(F.action == "streams"))
async def streams_main(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Главное меню эфиров"""
    # Получаем предстоящие эфиры
    upcoming_streams = await StreamService.get_upcoming_streams(session, limit=3)
    
    # Получаем количество записей
    stmt_count = select(func.count(Stream.id)).where(
        and_(
            Stream.recording_url.is_not(None),
            Stream.is_upcoming == False
        )
    )
    result = await session.execute(stmt_count)
    recordings_count = result.scalar() or 0
    
    text = _(
        "🎙 <b>ЛЕКТОРИЙ (Эфиры)</b>\n\n"
    )
    
    if upcoming_streams:
        next_stream = upcoming_streams[0]
        hours_until = int(next_stream["time_until"].total_seconds() / 3600)
        
        text += _(
            "🔴 <b>Ближайший эфир:</b>\n"
            "Тема: \"{title}\"\n"
            "Спикер: {speaker}\n"
            "📅 Дата: {date}\n"
            "⏳ До начала: {hours} часа(ов)\n\n"
        ).format(
            title=next_stream["title"],
            speaker=next_stream["speaker"] or "Не указан",
            date=next_stream["scheduled_time"].strftime("%d.%m.%Y %H:%M"),
            hours=hours_until
        )
    else:
        text += _("🔴 <b>Ближайший эфир:</b>\nНет запланированных эфиров.\n\n")
    
    text += _(
        "💾 <b>Архив записей:</b>\n"
        "В базе доступно {count} записей прошедших уроков."
    ).format(count=recordings_count)
    
    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()
    
    if upcoming_streams:
        builder.row(
            InlineKeyboardButton(
                text="🔔 Напомнить о трансляции",
                callback_data=EducationCallback(action="set_reminder", stream_id=upcoming_streams[0]["id"]).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="📂 Открыть Архив",
            callback_data=EducationCallback(action="open_archive", page=1).pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=EducationCallback(action="dashboard").pack()
        )
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
```

#### 5.6 Завершенные курсы (Экран 6)
```python
@router.callback_query(EducationCallback.filter(F.action == "completed_courses"))
async def completed_courses_detailed(
    callback: types.CallbackQuery,
    session: AsyncSession
) -> None:
    """Детальный вид завершенных курсов"""
    user_id = callback.from_user.id
    
    # Получаем завершенные курсы пользователя
    stmt = select(UserCourseProgress).where(
        and_(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.status == "completed"
        )
    ).order_by(UserCourseProgress.completed_at.desc())
    
    result = await session.execute(stmt)
    completed_progress = result.scalars().all()
    
    if not completed_progress:
        text = _(
            "🏆 <b>ВАШИ ДОСТИЖЕНИЯ</b>\n\n"
            "У вас пока нет завершенных курсов.\n"
            "Начните обучение и получите свой первый сертификат!"
        )
    else:
        text = _(
            "🏆 <b>ВАШИ ДОСТИЖЕНИЯ</b>\n\n"
            "МашаАллах, вы полностью завершили следующие курсы:\n\n"
        )
        
        for i, progress in enumerate(completed_progress[:5], 1):
            course = await session.get(Course, progress.course_id)
            if not course:
                continue
                
            # Проверяем наличие сертификата
            stmt_cert = select(Certificate).where(
                and_(
                    Certificate.user_id == user_id,
                    Certificate.course_id == course.id
                )
            )
            result_cert = await session.execute(stmt_cert)
            certificate = result_cert.scalar_one_or_none()
            
            medal = "🥇" if progress.progress_percentage > 90 else "🥈" if progress.progress_percentage > 70 else "🥉"
            
            text += _(
                "{i}. <b>{medal} {title}</b> (Завершено: {date})\n"
                "   — Оценка: {score}/5\n"
                "   — Тесты: {tests}%\n\n"
            ).format(
                i=i,
                medal=medal,
                title=course.title,
                date=progress.completed_at.strftime("%d.%m.%Y") if progress.completed_at else "Не указано",
                score=int(progress.progress_percentage / 20),  # Конвертируем в 5-балльную систему
                tests=int(progress.progress_percentage)
            )
    
    text += _("<i>Нажмите на курс, чтобы скачать сертификат или повторить.</i>")
    
    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()
    
    for i, progress in enumerate(completed_progress[:3], 1):
        course = await session.get(Course, progress.course_id)
        if not course:
            continue
            
        builder.row(
            InlineKeyboardButton(
                text=f"📜 Скачать сертификат ({course.title[:20]})",
                callback_data=EducationCallback(action="download_certificate", course_id=course.id).pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔄 Пройти заново",
            callback_data=EducationCallback(action="retake_course").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=EducationCallback(action="dashboard").pack()
        )
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
```

#### 5.7 AI-помощник (Экран 7)
```python
@router.callback_query(EducationCallback.filter(F.action == "assistant"))
async def ai_assistant_entry(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Вход в AI-помощник"""
    text = _(
        "🤖 <b>ПОМОЩНИК В ОБУЧЕНИИ</b>\n\n"
        "Ассаляму алейкум! Я искусственный интеллект, подключенный к базе знаний бота.\n\n"
        "<b>Я могу:</b>\n"
        "✅ Найти аят или хадис по теме.\n"
        "✅ Объяснить термин из урока.\n"
        "✅ Перевести слово с арабского.\n\n"
        "⛔ <b>Я НЕ МОГУ:</b>\n"
        "❌ Давать фетвы (решения о халяле/хараме).\n"
        "❌ Решать личные/семейные споры.\n\n"
        "<i>Напишите ваш вопрос ниже:</i>"
    )
    
    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Выйти в меню",
            callback_data=EducationCallback(action="dashboard").pack()
        )
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    
    # Устанавливаем состояние ожидания запроса
    await state.set_state(AIAssistantState.waiting_for_query)
    await callback.answer()

@router.message(AIAssistantState.waiting_for_query)
async def process_ai_query(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """Обработка запроса к AI-помощнику"""
    query = message.text
    user_id = message.from_user.id
    
    if not query or len(query.strip()) < 3:
        await message.answer(_("Пожалуйста, задайте вопрос длиннее 3 символов."))
        return
    
    # Показываем индикатор обработки
    processing_msg = await message.answer(_("🤔 Обрабатываю ваш вопрос..."))
    
    try:
        # Обрабатываем запрос через AI
        response = await AIService.process_query(query)
        
        # Формируем ответ
        text = _(
            "🤖 <b>ОТВЕТ ПОМОЩНИКА</b>\n\n"
            "<b>Ваш вопрос:</b>\n"
            "{query}\n\n"
            "<b>Ответ:</b>\n"
            "{response}\n\n"
            "<i>Задайте следующий вопрос или вернитесь в меню.</i>"
        ).format(query=query, response=response)
        
        # Создаем клавиатуру
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="🔙 Выйти в меню",
                callback_data=EducationCallback(action="dashboard").pack()
            )
        )
        
        await processing_msg.delete()
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        
    except Exception as e:
        await processing_msg.delete()
        await message.answer(_("Произошла ошибка при обработке запроса. Попробуйте позже."))
        logger.error(f"AI query error: {e}")
    
    # Сбрасываем состояние
    await state.clear()
```

### 6. Планировщик уведомлений

#### 6.1 Напоминания об обучении
```python
async def check_learning_reminders():
    """Проверяет и отправляет напоминания об обучении"""
    async with async_session() as session:
        # Находим пользователей, которые не занимались сегодня
        today = datetime.now().date()
        stmt = select(User).where(
            or_(
                User.last_learning_activity.is_(None),
                func.date(User.last_learning_activity) < today
            )
        ).limit(100)
        
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        for user in users:
            # Проверяем настройки уведомлений
            settings = await session.execute(
                select(Settings).where(Settings.user_id == user.telegram_id)
            )
            settings_obj = settings.scalar_one_or_none()
            
            if not settings_obj or not settings_obj.notify_course_reminders:
                continue
            
            # Отправляем напоминание
            try:
                text = _(
                    "🔔 Напоминание об обучении\n\n"
                    "Не забывайте про ежедневное обучение!\n"
                    "Сегодня вы еще не занимались.\n\n"
                    "Рекомендуемое время: {minutes} минут\n"
                    "Текущая серия: {days} дней подряд\n\n"
                    "Продолжайте серию! 📚"
                ).format(
                    minutes=settings_obj.daily_learning_goal_minutes,
                    days=user.learning_streak_days
                )
                
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                    reply_markup=get_education_dashboard_keyboard(
                        user_name=user.full_name,
                        overall_progress=0
                    )
                )
                
            except Exception as e:
                logger.error(f"Failed to send learning reminder to {user.telegram_id}: {e}")
```

#### 6.2 Напоминания об эфирах
```python
async def check_stream_reminders():
    """Проверяет и отправляет напоминания об эфирах"""
    async with async_session() as session:
        # Находим эфиры, которые начнутся через 15 минут
        reminder_time = datetime.now() + timedelta(minutes=15)
        
        stmt = select(Stream).where(
            and_(
                Stream.scheduled_time <= reminder_time,
                Stream.scheduled_time > datetime.now(),
                Stream.is_upcoming == True
            )
        )
        
        result = await session.execute(stmt)
        streams = result.scalars().all()
        
        for stream in streams:
            # Находим пользователей, которые установили напоминание
            stmt_reminders = select(StreamReminder).where(
                and_(
                    StreamReminder.stream_id == stream.id,
                    StreamReminder.reminded_at.is_(None)
                )
            )
            
            result = await session.execute(stmt_reminders)
            reminders = result.scalars().all()
            
            for reminder in reminders:
                try:
                    text = _(
                        "🔔 Напоминание о трансляции\n\n"
                        "Эфир начнется через 15 минут!\n\n"
                        "<b>Тема:</b> {title}\n"
                        "<b>Спикер:</b> {speaker}\n"
                        "<b>Время:</b> {time}\n\n"
                        "Не пропустите! 🎙️"
                    ).format(
                        title=stream.title,
                        speaker=stream.speaker or "Не указан",
                        time=stream.scheduled_time.strftime("%H:%M")
                    )
                    
                    await bot.send_message(
                        chat_id=reminder.user_id,
                        text=text,
                        parse_mode="HTML"
                    )
                    
                    # Отмечаем напоминание как отправленное
                    reminder.reminded_at = datetime.now()
                    await session.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to send stream reminder: {e}")
```

### 7. Пошаговый план реализации

#### Этап 1: Доработка моделей и миграций (2 дня)
1. Добавить недостающие поля в существующие модели
2. Создать новые модели: Stream, StreamReminder, Certificate
3. Создать миграции Alembic
4. Применить миграции к базе данных

#### Этап 2: Расширение сервисного слоя (3 дня)
1. Дополнить EducationService методами расчета прогресса
2. Создать StreamService для работы с эфирами
3. Создать AIService для AI-помощника
4. Реализовать CertificateService для генерации сертификатов

#### Этап 3: Реализация FSM состояний (2 дня)
1. Создать расширенные состояния для курсов и тестов
2. Реализовать состояния для эфиров и AI-помощника
3. Интегрировать с существующей системой состояний

#### Этап 4: Доработка клавиатур (2 дня)
1. Создать клавиатуры для всех 7 экранов
2. Реализовать динамические клавиатуры для уроков и тестов
3. Добавить поддержку пагинации для каталога и архива

#### Этап 5: Реализация обработчиков (4 дня)
1. Доработать существующие обработчики
2. Реализовать обработчики для всех 7 экранов
3. Интегрировать FSM состояния
4. Реализовать обработку медиа-контента

#### Этап 6: Интеграция с медиа и внешними сервисами (3 дня)
1. Интеграция с Telegraph для длинных текстов
2. Реализация отправки видео и аудио файлов
3. Интеграция с AI API (OpenAI/Claude)
4. Генерация сертификатов (изображения)

#### Этап 7: Планировщик уведомлений (2 дня)
1. Реализация напоминаний об обучении
2. Реализация напоминаний об эфирах
3. Интеграция с существующим планировщиком

#### Этап 8: Тестирование и отладка (3 дня)
1. Модульное тестирование сервисов
2. Интеграционное тестирование обработчиков
3. Тестирование FSM состояний
4. Тестирование уведомлений
5. Исправление ошибок

### 8. Текстовое содержимое (локализация)

#### 8.1 Ключевые тексты для локализации

**Главный дашборд:**
```python
_("🕌 <b>ЦЕНТР ОБУЧЕНИЯ</b>")
_("\"Стремление к знаниям — обязанность каждого мусульманина.\"")
_("👤 <b>Студент:</b> {user_name}")
_("⭐ <b>Статус:</b> Ищущий знания")
_("📈 <b>Общий прогресс знаний:</b>")
_("<i>Нажмите «Продолжить», чтобы вернуться к уроку.</i>")
```

**AI-помощник:**
```python
_("🤖 <b>ПОМОЩНИК В ОБУЧЕНИИ</b>")
_("Ассаляму алейкум! Я искусственный интеллект, подключенный к базе знаний бота.")
_("<b>Я могу:</b>")
_("✅ Найти аят или хадис по теме.")
_("✅ Объяснить термин из урока.")
_("✅ Перевести слово с арабского.")
_("⛔ <b>Я НЕ МОГУ:</b>")
_("❌ Давать фетвы (решения о халяле/хараме).")
_("❌ Решать личные/семейные споры.")
_("<i>Напишите ваш вопрос ниже:</i>")
```

#### 8.2 Поддержка языков
- Русский (основной)
- Английский
- Арабский
- Татарский
- Башкирский

### 9. Мониторинг и аналитика

#### 9.1 Метрики для отслеживания
1. **Активность пользователей:**
   - Количество активных пользователей в разделе обучения
   - Среднее время обучения в день
   - Количество завершенных курсов
   - Процент пользователей, возвращающихся к обучению

2. **Эффективность контента:**
   - Самые популярные курсы
   - Процент завершения курсов
   - Средние результаты тестов
   - Время, затраченное на разные типы контента

3. **Технические метрики:**
   - Время отклика сервисов
   - Количество ошибок
   - Загрузка медиа-контента

#### 9.2 Интеграция с аналитикой
- Amplitude для пользовательской аналитики
- Sentry для отслеживания ошибок
- Prometheus для технических метрик
- Grafana для визуализации

### 10. Заключение

Данное техническое задание предоставляет полную архитектуру для реализации расширенного функционала кнопки "Обучение" в Islamic Telegram Bot. Реализация включает:

1. **7 полноценных экранов** с детальной бизнес-логикой
2. **Расширенную систему прогресса** с расчетом по формуле из требований
3. **Интеграцию с медиа-контентом** (видео, аудио, Telegraph)
4. **AI-помощника** с ограниченным промптом для безопасных ответов
5. **Систему уведомлений** и напоминаний
6. **Генерацию сертификатов** для завершенных курсов
7. **Поддержку многопользовательской работы** и локализации

#### 10.1 Критерии успеха
- **Полное соответствие требованиям:** Все 7 экранов реализованы согласно описанию
- **Удобство использования:** Интуитивный интерфейс, быстрая навигация
- **Надежность:** Минимальное количество ошибок, стабильная работа
- **Производительность:** Быстрая загрузка контента, отзывчивый интерфейс
- **Масштабируемость:** Поддержка роста пользовательской базы

#### 10.2 Будущие улучшения
1. **Социальные функции:** Обсуждения курсов, рейтинги, лидерборды
2. **Персонализация:** Рекомендации курсов на основе прогресса
3. **Офлайн-режим:** Кэширование контента для работы без интернета
4. **Геймификация:** Бейджи, достижения, соревнования
5. **Интеграция с другими сервисами:** YouTube для видео, SoundCloud для аудио

---

**Документ подготовлен:** 11.12.2025  
**Версия ТЗ:** 1.0  
**Статус:** Готов к реализации  
**Автор:** Senior Full-Stack Python Developer / System Architect  

**Приложения:**
1. [Схема базы данных]()
2. [Диаграмма состояний FSM]()
3. [Макеты интерфейса]()
4. [API спецификация для AI-интеграции]()
