#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных начальным контентом модуля образования.
Запуск: python -m scripts.seed_education
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Добавляем корневую директорию в путь для импорта модулей проекта
sys.path.insert(0, '.')

from database.engine import AsyncSessionLocal
from database.models import (
    Course, CourseModule, Test, CourseLevel, CourseStatus,
    TestQuestion, TestOption, Stream, StreamReminder, Certificate
)


async def seed_courses(session: AsyncSession) -> None:
    """Добавляем курсы и их модули, если их ещё нет."""
    courses_data = [
        {
            "title": "Основы ислама",
            "description": "Базовый курс для новичков. Введение в основные понятия ислама.",
            "short_description": "Введение в ислам",
            "level": CourseLevel.BEGINNER,
            "estimated_hours": 10,
            "cover_image_url": "https://example.com/covers/islam_basics.jpg",
            "modules": [
                {"title": "Модуль 1. Введение", "description": "Что такое ислам?", "duration_minutes": 15, "has_test": True},
                {"title": "Модуль 2. Столпы веры", "description": "Шесть столпов имана", "duration_minutes": 20, "has_test": True},
                {"title": "Модуль 3. Столпы ислама", "description": "Пять столпов ислама", "duration_minutes": 25, "has_test": True},
                {"title": "Модуль 4. Пророки", "description": "Пророки в исламе", "duration_minutes": 20, "has_test": False},
                {"title": "Модуль 5. Коран", "description": "Священная книга", "duration_minutes": 20, "has_test": True},
            ]
        },
        {
            "title": "Намаз для начинающих",
            "description": "Практическое руководство по совершению молитвы. Подробное объяснение каждого действия.",
            "short_description": "Обучение намазу",
            "level": CourseLevel.BEGINNER,
            "estimated_hours": 12,
            "cover_image_url": "https://example.com/covers/prayer_basics.jpg",
            "modules": [
                {"title": "Модуль 1. Подготовка", "description": "Тахарат, вуду", "duration_minutes": 18, "has_test": True},
                {"title": "Модуль 2. Время намаза", "description": "Расписание молитв", "duration_minutes": 15, "has_test": False},
                {"title": "Модуль 3. Позиции", "description": "Положения тела в намазе", "duration_minutes": 25, "has_test": True},
                {"title": "Модуль 4. Суры и дуа", "description": "Тексты для чтения", "duration_minutes": 30, "has_test": True},
                {"title": "Модуль 5. Практика", "description": "Полный цикл намаза", "duration_minutes": 32, "has_test": True},
            ]
        },
        {
            "title": "Фикх для продвинутых",
            "description": "Углубленное изучение исламского права. Для тех, кто хочет понять тонкости фикха.",
            "short_description": "Углубленный фикх",
            "level": CourseLevel.ADVANCED,
            "estimated_hours": 20,
            "cover_image_url": "https://example.com/covers/fiqh_advanced.jpg",
            "modules": [
                {"title": "Модуль 1. Введение в фикх", "description": "Основные понятия", "duration_minutes": 30, "has_test": True},
                {"title": "Модуль 2. Мадхабы", "description": "Школы исламского права", "duration_minutes": 40, "has_test": True},
                {"title": "Модуль 3. Иджтихад", "description": "Методы вынесения решений", "duration_minutes": 35, "has_test": False},
                {"title": "Модуль 4. Современные вопросы", "description": "Фикх в современном мире", "duration_minutes": 45, "has_test": True},
            ]
        }
    ]

    for course_info in courses_data:
        # Проверяем, существует ли курс с таким названием
        stmt = select(Course).where(Course.title == course_info["title"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Курс '{course_info['title']}' уже существует, пропускаем.")
            continue

        course = Course(
            title=course_info["title"],
            description=course_info["description"],
            short_description=course_info.get("short_description"),
            level=course_info["level"],
            status=CourseStatus.PUBLISHED,
            cover_image_url=course_info.get("cover_image_url"),
            estimated_hours=course_info["estimated_hours"],
            order_index=0
        )
        session.add(course)
        await session.flush()  # чтобы получить course.id

        # Добавляем модули
        for idx, module_info in enumerate(course_info["modules"]):
            module = CourseModule(
                course_id=course.id,
                title=module_info["title"],
                description=module_info.get("description"),
                content_type="text",
                content_text="Контент будет добавлен позже.",
                duration_minutes=module_info["duration_minutes"],
                order_index=idx,
                is_free=True,
                has_test=module_info.get("has_test", False)
            )
            session.add(module)

        print(f"Добавлен курс '{course.title}' с {len(course_info['modules'])} модулями.")

    await session.commit()


async def seed_tests(session: AsyncSession) -> None:
    """Добавляем тесты, если их ещё нет."""
    # Сначала получаем курсы и модули для связывания
    stmt_courses = select(Course)
    result_courses = await session.execute(stmt_courses)
    courses = list(result_courses.scalars().all())
    
    if not courses:
        print("Нет курсов для связывания тестов. Сначала создайте курсы.")
        return
    
    course_basics = next((c for c in courses if "Основы ислама" in c.title), None)
    course_prayer = next((c for c in courses if "Намаз" in c.title), None)
    course_fiqh = next((c for c in courses if "Фикх" in c.title), None)
    
    # Получаем модули для связывания
    if course_basics:
        stmt_modules = select(CourseModule).where(CourseModule.course_id == course_basics.id)
        result_modules = await session.execute(stmt_modules)
        basics_modules = list(result_modules.scalars().all())
    else:
        basics_modules = []
    
    tests_data = [
        {
            "title": "Основы веры",
            "description": "Тест по основам веры (иман).",
            "difficulty": "medium",
            "passing_score": 70,
            "course_id": course_basics.id if course_basics else None,
            "module_id": basics_modules[1].id if len(basics_modules) > 1 else None,  # Модуль 2
            "questions": [
                {
                    "question_text": "Сколько столпов веры в исламе?",
                    "options": [
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False},
                        {"text": "4", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Кто является последним пророком?",
                    "options": [
                        {"text": "Муса (Моисей)", "is_correct": False},
                        {"text": "Иса (Иисус)", "is_correct": False},
                        {"text": "Мухаммад", "is_correct": True},
                        {"text": "Ибрахим (Авраам)", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Что такое Таухид?",
                    "options": [
                        {"text": "Единобожие", "is_correct": True},
                        {"text": "Многобожие", "is_correct": False},
                        {"text": "Атеизм", "is_correct": False},
                        {"text": "Политеизм", "is_correct": False},
                    ]
                }
            ]
        },
        {
            "title": "Намаз",
            "description": "Тест по правилам совершения намаза.",
            "difficulty": "easy",
            "passing_score": 60,
            "course_id": course_prayer.id if course_prayer else None,
            "module_id": basics_modules[3].id if len(basics_modules) > 3 else None,  # Модуль 4
            "questions": [
                {
                    "question_text": "Сколько обязательных намазов в день?",
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": False},
                        {"text": "5", "is_correct": True},
                        {"text": "6", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Какое первое действие перед намазом?",
                    "options": [
                        {"text": "Такбир", "is_correct": False},
                        {"text": "Омовение (вуду)", "is_correct": True},
                        {"text": "Чтение суры Аль-Фатиха", "is_correct": False},
                        {"text": "Поклон (руку)", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Как называется утренний намаз?",
                    "options": [
                        {"text": "Фаджр", "is_correct": True},
                        {"text": "Зухр", "is_correct": False},
                        {"text": "Аср", "is_correct": False},
                        {"text": "Магриб", "is_correct": False},
                    ]
                }
            ]
        },
        {
            "title": "Пост",
            "description": "Тест по правилам поста в месяц Рамадан.",
            "difficulty": "medium",
            "passing_score": 75,
            "course_id": None,  # Общий тест
            "module_id": None,
            "questions": [
                {
                    "question_text": "В каком месяце мусульмане соблюдают обязательный пост?",
                    "options": [
                        {"text": "Шавваль", "is_correct": False},
                        {"text": "Рамадан", "is_correct": True},
                        {"text": "Зуль-хиджа", "is_correct": False},
                        {"text": "Мухаррам", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Что нарушает пост?",
                    "options": [
                        {"text": "Приём пищи", "is_correct": True},
                        {"text": "Чтение Корана", "is_correct": False},
                        {"text": "Сон", "is_correct": False},
                        {"text": "Прогулка", "is_correct": False},
                    ]
                },
                {
                    "question_text": "Когда начинается пост?",
                    "options": [
                        {"text": "С рассветом", "is_correct": True},
                        {"text": "С восходом солнца", "is_correct": False},
                        {"text": "С полуднем", "is_correct": False},
                        {"text": "С закатом", "is_correct": False},
                    ]
                }
            ]
        }
    ]

    for test_info in tests_data:
        stmt = select(Test).where(Test.title == test_info["title"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Тест '{test_info['title']}' уже существует, пропускаем.")
            continue

        test = Test(
            title=test_info["title"],
            description=test_info["description"],
            course_id=test_info["course_id"],
            module_id=test_info["module_id"],
            difficulty=test_info["difficulty"],
            passing_score=test_info["passing_score"],
            is_active=True
        )
        session.add(test)
        await session.flush()

        for q_idx, question_info in enumerate(test_info["questions"]):
            question = TestQuestion(
                test_id=test.id,
                question_text=question_info["question_text"],
                question_type="single_choice",
                order_index=q_idx,
                points=1
            )
            session.add(question)
            await session.flush()

            for o_idx, option_info in enumerate(question_info["options"]):
                option = TestOption(
                    question_id=question.id,
                    option_text=option_info["text"],
                    is_correct=option_info["is_correct"],
                    order_index=o_idx,
                    explanation="Правильный ответ объясняется в уроках курса."
                )
                session.add(option)

        print(f"Добавлен тест '{test.title}' с {len(test_info['questions'])} вопросами.")

    await session.commit()


async def seed_streams(session: AsyncSession) -> None:
    """Добавляем стримы, если их ещё нет."""
    streams_data = [
        {
            "title": "Живая лекция: Основы ислама",
            "description": "Прямой эфир с шейхом Ахмадом о основах ислама для новичков.",
            "speaker": "Шейх Ахмад",
            "scheduled_time": datetime.now() + timedelta(days=2, hours=19),
            "duration_minutes": 90,
            "stream_url": "https://youtube.com/live/abc123",
            "is_upcoming": True,
            "max_participants": 1000
        },
        {
            "title": "Разбор суры Аль-Фатиха",
            "description": "Подробный тафсир первой суры Корана.",
            "speaker": "Доктор Юсуф",
            "scheduled_time": datetime.now() + timedelta(days=5, hours=20),
            "duration_minutes": 120,
            "stream_url": "https://youtube.com/live/def456",
            "is_upcoming": True,
            "max_participants": 500
        },
        {
            "title": "Архив: История пророков",
            "description": "Запись лекции о жизни пророков в исламе.",
            "speaker": "Профессор Ибрагим",
            "scheduled_time": datetime.now() - timedelta(days=10),
            "duration_minutes": 150,
            "recording_url": "https://youtube.com/watch?v=xyz789",
            "is_upcoming": False,
            "max_participants": None
        }
    ]

    for stream_info in streams_data:
        stmt = select(Stream).where(Stream.title == stream_info["title"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Стрим '{stream_info['title']}' уже существует, пропускаем.")
            continue

        stream = Stream(
            title=stream_info["title"],
            description=stream_info["description"],
            speaker=stream_info.get("speaker"),
            scheduled_time=stream_info["scheduled_time"],
            duration_minutes=stream_info["duration_minutes"],
            stream_url=stream_info.get("stream_url"),
            recording_url=stream_info.get("recording_url"),
            is_upcoming=stream_info["is_upcoming"],
            max_participants=stream_info.get("max_participants")
        )
        session.add(stream)
        print(f"Добавлен стрим '{stream.title}'.")

    await session.commit()


async def seed_certificates(session: AsyncSession) -> None:
    """Добавляем примеры сертификатов, если их ещё нет."""
    # Получаем первого пользователя (если есть)
    from database.models import User
    stmt_user = select(User).limit(1)
    result_user = await session.execute(stmt_user)
    user = result_user.scalar_one_or_none()
    
    if not user:
        print("Нет пользователей для создания сертификатов.")
        return
    
    # Получаем курсы
    stmt_courses = select(Course).limit(2)
    result_courses = await session.execute(stmt_courses)
    courses = list(result_courses.scalars().all())
    
    for course in courses:
        stmt = select(Certificate).where(
            (Certificate.user_id == user.id) & (Certificate.course_id == course.id)
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Сертификат для курса '{course.title}' уже существует, пропускаем.")
            continue
        
        certificate = Certificate(
            user_id=user.id,
            course_id=course.id,
            certificate_url=f"https://example.com/certificates/{user.id}_{course.id}.pdf",
            score=85.5
        )
        session.add(certificate)
        print(f"Добавлен сертификат для курса '{course.title}'.")

    await session.commit()


async def main() -> None:
    """Основная функция."""
    async with AsyncSessionLocal() as session:
        try:
            print("Начало заполнения базы данных образовательным контентом...")
            await seed_courses(session)
            await seed_tests(session)
            await seed_streams(session)
            await seed_certificates(session)
            print("Заполнение завершено успешно.")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при заполнении: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
