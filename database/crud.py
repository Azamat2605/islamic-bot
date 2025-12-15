from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database.models import (
    User, Settings, Course, CourseModule, UserCourseProgress, UserModuleProgress,
    Test, TestQuestion, TestOption, UserTestResult, UserTestAnswer,
    Stream, StreamReminder, Certificate
)


async def get_or_create_user_with_settings(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    username: str | None = None,
) -> tuple[User, Settings]:
    """
    Проверяет существование пользователя по telegram_id.
    Если не существует, создаёт и User, и Settings в одной транзакции.
    Всегда возвращает кортеж (User, Settings).
    """
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        # Создаём нового пользователя и настройки
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        session.add(user)
        await session.flush()  # Получаем user.id
        
        # Создаём настройки с дефолтными значениями для молитв
        settings = Settings(
            user_id=user.id,
            language="ru",
            timezone="Europe/Moscow",
            madhab="Hanafi",
            notify_fajr=True,
            notify_dhuhr=True,
            notify_asr=True,
            notify_maghrib=True,
            notify_isha=True,
        )
        session.add(settings)
        await session.commit()
        return user, settings

    # Получаем настройки пользователя
    settings_stmt = select(Settings).where(Settings.user_id == user.id)
    settings_result = await session.execute(settings_stmt)
    settings = settings_result.scalar_one_or_none()
    
    if not settings:
        # Создаём настройки, если их нет
        settings = Settings(
            user_id=user.id,
            language="ru",
            timezone="Europe/Moscow",
            madhab="Hanafi",
            notify_fajr=True,
            notify_dhuhr=True,
            notify_asr=True,
            notify_maghrib=True,
            notify_isha=True,
        )
        session.add(settings)
        await session.commit()
    
    # Обновляем username и full_name, если они изменились
    updated = False
    if user.username != username:
        user.username = username
        updated = True
    if user.full_name != full_name:
        user.full_name = full_name
        updated = True
    if updated:
        await session.commit()
    
    return user, settings


async def get_user_with_settings(
    session: AsyncSession,
    telegram_id: int,
) -> tuple[User | None, Settings | None]:
    """
    Возвращает пользователя и его настройки по telegram_id в одном запросе.
    Использует joinedload для эффективной загрузки связанных настроек.
    Если пользователь не найден, возвращает (None, None).
    """
    stmt = (
        select(User)
        .options(joinedload(User.settings))
        .where(User.telegram_id == telegram_id)
    )
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    if user is None:
        return None, None
    settings = user.settings
    return user, settings


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """
    Возвращает язык пользователя из таблицы Settings по telegram_id.
    Если запись не найдена, возвращает "ru".
    Если язык не входит в список поддерживаемых, возвращает "ru".
    """
    print(f"DEBUG GETTER: Fetching language for telegram_id={telegram_id}")
    stmt = (
        select(Settings.language)
        .join(User, Settings.user_id == User.id)
        .where(User.telegram_id == telegram_id)
    )
    result = await session.execute(stmt)
    # Безопасная обработка возможных дубликатов: берем первый
    languages = result.scalars().all()
    if not languages:
        print(f"DEBUG GETTER: No language found, returning 'ru'")
        return "ru"
    lang = languages[0]
    
    # Проверяем, что язык входит в список поддерживаемых
    from bot.core.config import SUPPORTED_LOCALES
    if lang not in SUPPORTED_LOCALES:
        print(f"DEBUG GETTER: Language '{lang}' not in supported locales, returning 'ru'")
        return "ru"
    
    print(f"DEBUG GETTER: Returning language '{lang}' (Source: DB)")
    return lang


async def set_user_language(session: AsyncSession, user_id: int, language: str) -> None:
    """
    Устанавливает язык пользователя в таблице Settings.
    """
    stmt = select(Settings).where(Settings.user_id == user_id)
    result = await session.execute(stmt)
    settings_list = result.scalars().all()
    if settings_list:
        # Берем первую запись (дубликаты должны быть удалены, но на всякий случай)
        settings = settings_list[0]
        settings.language = language
        await session.commit()
    else:
        # Создаём запись Settings, если её нет (маловероятно)
        settings = Settings(user_id=user_id, language=language, notification_on=True)
        session.add(settings)
        await session.commit()


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Получить пользователя по telegram_id"""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_settings(session: AsyncSession, user_id: int) -> Settings | None:
    """Получить настройки пользователя по user_id"""
    stmt = select(Settings).where(Settings.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_settings(session: AsyncSession, settings_id: int, update_data: dict) -> None:
    """Обновить настройки"""
    stmt = select(Settings).where(Settings.id == settings_id)
    result = await session.execute(stmt)
    settings = result.scalar_one_or_none()
    if settings:
        for key, value in update_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        await session.commit()


async def update_user_settings(session: AsyncSession, telegram_id: int, **kwargs) -> Settings | None:
    """
    Находит настройки пользователя по telegram_id и обновляет указанные поля.
    Возвращает обновлённый объект Settings или None, если пользователь не найден.
    """
    # Сначала находим пользователя
    user_stmt = select(User).where(User.telegram_id == telegram_id)
    user_result = await session.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Находим настройки пользователя
    settings_stmt = select(Settings).where(Settings.user_id == user.id)
    settings_result = await session.execute(settings_stmt)
    settings = settings_result.scalar_one_or_none()
    
    if not settings:
        # Создаём настройки, если их нет
        settings = Settings(
            user_id=user.id,
            language="ru",
            timezone="Europe/Moscow",
            madhab="Hanafi",
            notify_fajr=True,
            notify_dhuhr=True,
            notify_asr=True,
            notify_maghrib=True,
            notify_isha=True,
        )
        session.add(settings)
        await session.flush()
    
    # Обновляем указанные поля
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    await session.commit()
    return settings


async def update_user(session: AsyncSession, user_id: int, update_data: dict) -> None:
    """Обновить данные пользователя"""
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await session.commit()


# ==================== EDUCATION CRUD METHODS ====================

async def get_course_by_id(session: AsyncSession, course_id: int) -> Course | None:
    """Получить курс по ID с загрузкой модулей"""
    stmt = select(Course).where(Course.id == course_id).options(selectinload(Course.modules))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_courses_by_level(session: AsyncSession, level: str) -> list[Course]:
    """Получить курсы по уровню сложности"""
    stmt = select(Course).where(Course.level == level).order_by(Course.order_index)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_all_courses(session: AsyncSession) -> list[Course]:
    """Получить все опубликованные курсы"""
    stmt = select(Course).where(Course.status == "published").order_by(Course.order_index)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_course_modules(session: AsyncSession, course_id: int) -> list[CourseModule]:
    """Получить модули курса"""
    stmt = select(CourseModule).where(CourseModule.course_id == course_id).order_by(CourseModule.order_index)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_module_by_id(session: AsyncSession, module_id: int) -> CourseModule | None:
    """Получить модуль по ID"""
    stmt = select(CourseModule).where(CourseModule.id == module_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_course_progress(
    session: AsyncSession, user_id: int, course_id: int
) -> UserCourseProgress | None:
    """Получить прогресс пользователя по курсу"""
    stmt = select(UserCourseProgress).where(
        and_(UserCourseProgress.user_id == user_id, UserCourseProgress.course_id == course_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_course_progress(
    session: AsyncSession, user_id: int, course_id: int
) -> UserCourseProgress:
    """Создать запись прогресса пользователя по курсу"""
    progress = UserCourseProgress(
        user_id=user_id,
        course_id=course_id,
        status="active",
        progress_percentage=0.0,
        completed_modules_count=0,
        total_modules_count=0,
        is_completed=False
    )
    session.add(progress)
    await session.flush()
    return progress


async def update_user_course_progress(
    session: AsyncSession, progress_id: int, update_data: dict
) -> None:
    """Обновить прогресс курса пользователя"""
    stmt = select(UserCourseProgress).where(UserCourseProgress.id == progress_id)
    result = await session.execute(stmt)
    progress = result.scalar_one_or_none()
    if progress:
        for key, value in update_data.items():
            if hasattr(progress, key):
                setattr(progress, key, value)
        await session.commit()


async def get_user_module_progress(
    session: AsyncSession, user_id: int, module_id: int
) -> UserModuleProgress | None:
    """Получить прогресс пользователя по модулю"""
    stmt = select(UserModuleProgress).where(
        and_(UserModuleProgress.user_id == user_id, UserModuleProgress.module_id == module_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_module_progress(
    session: AsyncSession, user_id: int, module_id: int, course_progress_id: int | None = None
) -> UserModuleProgress:
    """Создать запись прогресса пользователя по модулю"""
    progress = UserModuleProgress(
        user_id=user_id,
        module_id=module_id,
        course_progress_id=course_progress_id,
        status="in_progress",
        time_spent_minutes=0
    )
    session.add(progress)
    await session.flush()
    return progress


async def complete_user_module(
    session: AsyncSession, user_id: int, module_id: int
) -> UserModuleProgress | None:
    """Отметить модуль как завершенный"""
    stmt = select(UserModuleProgress).where(
        and_(UserModuleProgress.user_id == user_id, UserModuleProgress.module_id == module_id)
    )
    result = await session.execute(stmt)
    progress = result.scalar_one_or_none()
    if progress:
        progress.status = "completed"
        progress.completed_at = func.now()
        await session.commit()
    return progress


async def get_test_by_id(session: AsyncSession, test_id: int) -> Test | None:
    """Получить тест по ID с вопросами и вариантами"""
    stmt = select(Test).where(Test.id == test_id).options(
        selectinload(Test.questions).selectinload(TestQuestion.options)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_tests_by_course(session: AsyncSession, course_id: int) -> list[Test]:
    """Получить тесты курса"""
    stmt = select(Test).where(Test.course_id == course_id).order_by(Test.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_user_test_result(
    session: AsyncSession, user_id: int, test_id: int, attempt_number: int = 1
) -> UserTestResult | None:
    """Получить результат теста пользователя"""
    stmt = select(UserTestResult).where(
        and_(
            UserTestResult.user_id == user_id,
            UserTestResult.test_id == test_id,
            UserTestResult.attempt_number == attempt_number
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_test_result(
    session: AsyncSession, user_id: int, test_id: int, attempt_number: int = 1
) -> UserTestResult:
    """Создать запись результата теста пользователя"""
    result = UserTestResult(
        user_id=user_id,
        test_id=test_id,
        attempt_number=attempt_number,
        score=0.0,
        correct_answers=0,
        total_questions=0,
        time_spent_seconds=0,
        passed=False
    )
    session.add(result)
    await session.flush()
    return result


async def update_user_test_result(
    session: AsyncSession, result_id: int, update_data: dict
) -> None:
    """Обновить результат теста пользователя"""
    stmt = select(UserTestResult).where(UserTestResult.id == result_id)
    result = await session.execute(stmt)
    test_result = result.scalar_one_or_none()
    if test_result:
        for key, value in update_data.items():
            if hasattr(test_result, key):
                setattr(test_result, key, value)
        await session.commit()


async def get_streams_upcoming(session: AsyncSession, limit: int = 10) -> list[Stream]:
    """Получить предстоящие стримы"""
    stmt = select(Stream).where(Stream.is_upcoming == True).order_by(Stream.scheduled_time).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_streams_archive(session: AsyncSession, limit: int = 10) -> list[Stream]:
    """Получить архив стримов"""
    stmt = select(Stream).where(Stream.is_upcoming == False).order_by(Stream.scheduled_time.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_stream_reminder(
    session: AsyncSession, user_id: int, stream_id: int
) -> StreamReminder:
    """Создать напоминание о стриме"""
    reminder = StreamReminder(
        user_id=user_id,
        stream_id=stream_id
    )
    session.add(reminder)
    await session.flush()
    return reminder


async def get_user_stream_reminders(
    session: AsyncSession, user_id: int
) -> list[StreamReminder]:
    """Получить напоминания пользователя о стримах"""
    stmt = select(StreamReminder).where(StreamReminder.user_id == user_id).options(
        selectinload(StreamReminder.stream)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_certificate_by_user_and_course(
    session: AsyncSession, user_id: int, course_id: int
) -> Certificate | None:
    """Получить сертификат пользователя по курсу"""
    stmt = select(Certificate).where(
        and_(Certificate.user_id == user_id, Certificate.course_id == course_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_certificate(
    session: AsyncSession, user_id: int, course_id: int, certificate_url: str, score: float = 0.0
) -> Certificate:
    """Создать сертификат"""
    certificate = Certificate(
        user_id=user_id,
        course_id=course_id,
        certificate_url=certificate_url,
        score=score
    )
    session.add(certificate)
    await session.flush()
    return certificate
