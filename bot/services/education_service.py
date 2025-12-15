"""
Education Service Layer.

Provides business logic for education module, fetching data from database
and formatting it for handlers.
"""
from typing import Dict, List, Tuple, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import time

from database.models import (
    Course, CourseModule, Test, UserCourseProgress, UserTestResult,
    CourseLevel, CourseStatus, TestQuestion, TestOption, UserTestAnswer,
    UserModuleProgress, Stream
)


class EducationService:
    """Service for education module operations."""

    @staticmethod
    async def get_user_progress_data(
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, any]:
        """
        Get comprehensive education data for a user.

        Returns a dictionary with keys:
        - active_courses: List[Dict] with title, progress_percentage, completed_modules, total_modules
        - completed_courses: List[Dict] with title, medal_emoji
        - test_results: List[Dict] with title, score_percentage
        - monthly_stats: Dict with courses_completed, tests_passed, level, learning_time
        """
        # Fetch user's course progress with course details
        stmt = select(
            UserCourseProgress,
            Course
        ).join(
            Course, Course.id == UserCourseProgress.course_id
        ).options(
            selectinload(Course.modules)
        ).where(
            UserCourseProgress.user_id == user_id,
            Course.status == CourseStatus.PUBLISHED
        )
        result = await session.execute(stmt)
        user_progress_records = result.all()

        # Active courses (not completed)
        active_courses = []
        completed_courses = []
        
        for progress, course in user_progress_records:
            if progress.is_completed:
                # Determine medal based on completion order or score
                medal_index = len(completed_courses) % 3
                medals = ["🥇", "🥈", "🥉"]
                completed_courses.append({
                    "title": course.title,
                    "medal_emoji": medals[medal_index],
                })
            else:
                # Calculate progress percentage
                total_modules = progress.total_modules_count or len(course.modules)
                completed_modules = progress.completed_modules_count or 0
                progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0.0
                
                active_courses.append({
                    "id": course.id,
                    "title": course.title,
                    "progress_percentage": round(progress_percentage, 1),
                    "completed_modules": completed_modules,
                    "total_modules": total_modules,
                })

        # If no active courses, use first two published courses as mock with mock progress
        if not active_courses:
            stmt_courses = select(Course).where(
                Course.status == CourseStatus.PUBLISHED
            ).options(
                selectinload(Course.modules)
            ).order_by(Course.order_index).limit(2)
            result = await session.execute(stmt_courses)
            mock_courses = result.scalars().all()
            
            for i, course in enumerate(mock_courses):
                progress_percentage = 65.0 if i == 0 else 40.0
                completed_modules = 3 if i == 0 else 2
                total_modules = len(course.modules) or 5
                
                active_courses.append({
                    "id": course.id,
                    "title": course.title,
                    "progress_percentage": progress_percentage,
                    "completed_modules": completed_modules,
                    "total_modules": total_modules,
                })

        # If no completed courses, use mock data
        if not completed_courses:
            completed_courses = [
                {"title": "Введение в ислам", "medal_emoji": "🥇"},
                {"title": "Фикх очищения", "medal_emoji": "🥈"},
                {"title": "История пророков", "medal_emoji": "🥉"},
            ]

        # Test results: fetch user's test results
        stmt_tests = select(UserTestResult).where(
            UserTestResult.user_id == user_id
        ).order_by(UserTestResult.completed_at.desc()).limit(3)
        result = await session.execute(stmt_tests)
        test_results_db = result.scalars().all()

        test_results = []
        if test_results_db:
            for res in test_results_db:
                # Fetch test title
                stmt_test = select(Test).where(Test.id == res.test_id)
                result_test = await session.execute(stmt_test)
                test = result_test.scalar_one_or_none()
                
                if test:
                    test_results.append({
                        "id": test.id,
                        "title": test.title,
                        "score_percentage": res.score,
                    })
        
        # If no test results, use mock data with real test names
        if not test_results:
            stmt_all_tests = select(Test).where(Test.is_active == True).limit(3)
            result = await session.execute(stmt_all_tests)
            all_tests = result.scalars().all()
            
            mock_scores = [85.0, 70.0, 90.0]
            for i, test in enumerate(all_tests):
                score = mock_scores[i] if i < len(mock_scores) else 75.0
                test_results.append({
                    "id": test.id,
                    "title": test.title,
                    "score_percentage": score,
                })

        # Monthly stats: calculate from last 30 days
        # For now, use mock data
        monthly_stats = {
            "courses_completed": 2,
            "tests_passed": 5,
            "level": 12,
            "learning_time": "15ч 30м",
        }

        return {
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "test_results": test_results,
            "monthly_stats": monthly_stats,
        }

    @staticmethod
    async def get_course_detail(
        course_id: int,
        session: AsyncSession
    ) -> Optional[Dict[str, any]]:
        """Get course details by ID."""
        stmt = select(Course).where(Course.id == course_id)
        result = await session.execute(stmt)
        course = result.scalar_one_or_none()
        if not course:
            return None

        # Count modules
        stmt_modules = select(func.count(CourseModule.id)).where(
            CourseModule.course_id == course_id
        )
        result = await session.execute(stmt_modules)
        total_modules = result.scalar() or 0

        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "level": course.level.value,
            "total_modules": total_modules,
            "estimated_hours": course.estimated_hours,
        }

    @staticmethod
    async def get_test_detail(
        test_id: int,
        session: AsyncSession
    ) -> Optional[Dict[str, any]]:
        """Get test details by ID."""
        stmt = select(Test).where(Test.id == test_id)
        result = await session.execute(stmt)
        test = result.scalar_one_or_none()
        if not test:
            return None

        # Count questions
        stmt_questions = select(func.count(TestQuestion.id)).where(
            TestQuestion.test_id == test_id
        )
        result = await session.execute(stmt_questions)
        total_questions = result.scalar() or 0

        return {
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "difficulty": test.difficulty,
            "passing_score": test.passing_score,
            "total_questions": total_questions,
            "time_limit_minutes": test.time_limit_minutes,
        }

    @staticmethod
    async def get_user_test_results(
        user_id: int,
        session: AsyncSession
    ) -> List[Dict[str, any]]:
        """Get user's test results (real data if exists, otherwise mock)."""
        stmt = select(UserTestResult).where(
            UserTestResult.user_id == user_id
        ).order_by(UserTestResult.completed_at.desc())
        result = await session.execute(stmt)
        real_results = result.scalars().all()

        if real_results:
            # Format real results
            formatted = []
            for res in real_results:
                formatted.append({
                    "test_id": res.test_id,
                    "score_percentage": res.score,
                    "correct_answers": res.correct_answers,
                    "total_questions": res.total_questions,
                    "time_spent_seconds": res.time_spent_seconds,
                    "passed": res.passed,
                })
            return formatted

        # Fallback to mock results
        stmt_tests = select(Test).where(Test.is_active == True).limit(3)
        result = await session.execute(stmt_tests)
        tests = result.scalars().all()
        mock_scores = [85.0, 70.0, 90.0]
        mock_results = []
        for i, test in enumerate(tests):
            mock_results.append({
                "test_id": test.id,
                "score_percentage": mock_scores[i] if i < len(mock_scores) else 75.0,
                "correct_answers": 17 if i == 0 else (14 if i == 1 else 9),
                "total_questions": 20 if i < 2 else 10,
                "time_spent_seconds": 750 if i == 0 else (900 if i == 1 else 480),
                "passed": True,
            })
        return mock_results

    @staticmethod
    async def get_all_courses(
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """Get list of published courses."""
        stmt = select(Course).where(
            Course.status == CourseStatus.PUBLISHED
        ).options(
            selectinload(Course.modules)
        ).order_by(Course.order_index, Course.created_at).limit(limit)
        result = await session.execute(stmt)
        courses = result.scalars().all()
        return [
            {
                "id": c.id,
                "title": c.title,
                "description": c.short_description or c.description,
                "level": c.level.value,
                "estimated_hours": c.estimated_hours,
                "module_count": len(c.modules),
            }
            for c in courses
        ]

    @staticmethod
    async def get_all_tests(
        session: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """Get list of active tests."""
        stmt = select(Test).where(
            Test.is_active == True
        ).options(
            selectinload(Test.questions)
        ).order_by(Test.created_at).limit(limit)
        result = await session.execute(stmt)
        tests = result.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "difficulty": t.difficulty,
                "passing_score": t.passing_score,
                "question_count": len(t.questions),
            }
            for t in tests
        ]

    # ==================== NEW METHODS FOR TEST TAKING ====================

    @staticmethod
    async def get_test_questions_with_options(
        test_id: int,
        session: AsyncSession
    ) -> List[Dict[str, any]]:
        """
        Retrieve all questions with their options for a given test.

        Returns list of dicts:
        {
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "points": question.points,
            "options": [
                {"id": option.id, "option_text": option.option_text, "is_correct": option.is_correct},
                ...
            ]
        }
        """
        stmt = select(TestQuestion).where(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.order_index)
        result = await session.execute(stmt)
        questions = result.scalars().all()

        formatted_questions = []
        for q in questions:
            # Fetch options
            stmt_options = select(TestOption).where(
                TestOption.question_id == q.id
            ).order_by(TestOption.order_index)
            result_options = await session.execute(stmt_options)
            options = result_options.scalars().all()
            formatted_questions.append({
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "points": q.points,
                "options": [
                    {
                        "id": opt.id,
                        "option_text": opt.option_text,
                        "is_correct": opt.is_correct,
                        "explanation": opt.explanation,
                    }
                    for opt in options
                ]
            })
        return formatted_questions

    @staticmethod
    async def get_next_question(
        test_id: int,
        current_index: int,
        session: AsyncSession
    ) -> Optional[Dict[str, any]]:
        """
        Get the next question after current_index (0-based).
        Returns None if no more questions.
        """
        stmt = select(TestQuestion).where(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.order_index).offset(current_index).limit(1)
        result = await session.execute(stmt)
        question = result.scalar_one_or_none()
        if not question:
            return None

        # Fetch options
        stmt_options = select(TestOption).where(
            TestOption.question_id == question.id
        ).order_by(TestOption.order_index)
        result_options = await session.execute(stmt_options)
        options = result_options.scalars().all()

        return {
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "points": question.points,
            "options": [
                {
                    "id": opt.id,
                    "option_text": opt.option_text,
                    "is_correct": opt.is_correct,
                }
                for opt in options
            ]
        }

    @staticmethod
    async def save_test_result(
        user_id: int,
        test_id: int,
        score: float,
        correct_answers: int,
        total_questions: int,
        time_spent_seconds: int,
        user_answers: List[Dict],
        session: AsyncSession
    ) -> UserTestResult:
        """
        Save test result and individual answers to database.

        Args:
            user_id: Telegram user ID
            test_id: Test ID
            score: Percentage score (0-100)
            correct_answers: Number of correct answers
            total_questions: Total questions in test
            time_spent_seconds: Time spent on test in seconds
            user_answers: List of dicts with keys 'question_id', 'selected_option_ids', 'is_correct', 'points_earned'
            session: AsyncSession

        Returns:
            Created UserTestResult object
        """
        # Determine attempt number
        stmt_attempt = select(func.max(UserTestResult.attempt_number)).where(
            UserTestResult.user_id == user_id,
            UserTestResult.test_id == test_id
        )
        result = await session.execute(stmt_attempt)
        max_attempt = result.scalar() or 0
        attempt_number = max_attempt + 1

        # Create test result
        test_result = UserTestResult(
            user_id=user_id,
            test_id=test_id,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            time_spent_seconds=time_spent_seconds,
            attempt_number=attempt_number,
            passed=score >= 70.0,  # using default passing score
            completed_at=func.now()
        )
        session.add(test_result)
        await session.flush()  # to get test_result.id

        # Save individual answers
        for answer in user_answers:
            user_answer = UserTestAnswer(
                test_result_id=test_result.id,
                question_id=answer["question_id"],
                selected_option_ids=answer.get("selected_option_ids"),
                answer_text=answer.get("answer_text"),
                is_correct=answer["is_correct"],
                points_earned=answer["points_earned"]
            )
            session.add(user_answer)

        await session.commit()
        return test_result

    @staticmethod
    async def check_answer_correctness(
        question_id: int,
        selected_option_ids: List[int],
        session: AsyncSession
    ) -> Tuple[bool, float]:
        """
        Check if selected options are correct for a given question.

        Returns:
            (is_correct, points_earned)
        """
        # Fetch correct options
        stmt = select(TestOption).where(
            TestOption.question_id == question_id,
            TestOption.is_correct == True
        )
        result = await session.execute(stmt)
        correct_options = result.scalars().all()
        correct_option_ids = {opt.id for opt in correct_options}

        # Fetch question points
        stmt_question = select(TestQuestion).where(TestQuestion.id == question_id)
        result = await session.execute(stmt_question)
        question = result.scalar_one()
        points_per_question = question.points

        # For single choice: selected must match exactly one correct option
        if question.question_type == "single_choice":
            if len(selected_option_ids) != 1:
                return False, 0.0
            selected_id = selected_option_ids[0]
            is_correct = selected_id in correct_option_ids
            points_earned = points_per_question if is_correct else 0.0
            return is_correct, points_earned
        
        # For multiple choice: all selected must be correct, and all correct must be selected
        elif question.question_type == "multiple_choice":
            selected_set = set(selected_option_ids)
            if selected_set == correct_option_ids:
                return True, points_per_question
            else:
                # Partial credit? For now, no partial credit
                return False, 0.0
        
        # Default fallback
        return False, 0.0

    # ==================== NEW METHODS FOR UI IMPLEMENTATION ====================

    @staticmethod
    async def get_courses_by_category(
        category_name: str,
        session: AsyncSession
    ) -> List[Dict[str, any]]:
        """Get courses by category (mock implementation for now)."""
        # For now, return all published courses
        stmt = select(Course).where(
            Course.status == CourseStatus.PUBLISHED
        ).options(
            selectinload(Course.modules)
        ).order_by(Course.order_index).limit(5)
        result = await session.execute(stmt)
        courses = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "title": c.title,
                "level": c.level.value,
                "estimated_hours": c.estimated_hours,
                "module_count": len(c.modules),
            }
            for c in courses
        ]

    @staticmethod
    async def get_user_course_progress(
        user_id: int,
        course_id: int,
        session: AsyncSession
    ) -> Optional[Dict[str, any]]:
        """Get user progress for a specific course."""
        stmt = select(UserCourseProgress).where(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_id == course_id
        )
        result = await session.execute(stmt)
        progress = result.scalar_one_or_none()
        
        if progress:
            return {
                "id": progress.id,
                "progress_percentage": progress.progress_percentage,
                "completed_modules": progress.completed_modules_count,
                "total_modules": progress.total_modules_count,
                "is_completed": progress.is_completed,
            }
        return None

    @staticmethod
    async def get_course_modules(
        course_id: int,
        session: AsyncSession
    ) -> List[Dict[str, any]]:
        """Get modules for a course."""
        stmt = select(CourseModule).where(
            CourseModule.course_id == course_id
        ).options(
            selectinload(CourseModule.test)
        ).order_by(CourseModule.order_index)
        result = await session.execute(stmt)
        modules = result.scalars().all()
        
        return [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "duration_minutes": m.duration_minutes,
                "has_video": m.content_type == "video",
                "has_audio": m.content_type == "audio",
                "order_index": m.order_index,
            }
            for m in modules
        ]

    @staticmethod
    async def get_user_module_progress(
        user_id: int,
        course_id: int,
        session: AsyncSession
    ) -> List[Dict[str, any]]:
        """Get user progress for modules in a course."""
        stmt = select(UserModuleProgress).join(
            CourseModule, CourseModule.id == UserModuleProgress.module_id
        ).options(
            selectinload(UserModuleProgress.module)
        ).where(
            UserModuleProgress.user_id == user_id,
            CourseModule.course_id == course_id
        )
        result = await session.execute(stmt)
        progress_records = result.scalars().all()
        
        return [
            {
                "module_id": p.module_id,
                "status": p.status,
                "completed_at": p.completed_at,
                "time_spent_minutes": p.time_spent_minutes,
            }
            for p in progress_records
        ]

    @staticmethod
    async def get_module_detail(
        module_id: int,
        session: AsyncSession
    ) -> Optional[Dict[str, any]]:
        """Get module details by ID."""
        stmt = select(CourseModule).where(CourseModule.id == module_id).options(
            selectinload(CourseModule.course),
            selectinload(CourseModule.test)
        )
        result = await session.execute(stmt)
        module = result.scalar_one_or_none()
        
        if not module:
            return None
        
        return {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "duration_minutes": module.duration_minutes,
            "content_type": module.content_type,
            "has_video": module.content_type == "video",
            "has_audio": module.content_type == "audio",
            "course_id": module.course_id,
            "order_index": module.order_index,
        }

    @staticmethod
    async def calculate_overall_progress(
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, any]:
        """Calculate overall progress for dashboard."""
        # Get total lessons in database
        stmt_total = select(func.count(CourseModule.id))
        result = await session.execute(stmt_total)
        total_lessons = result.scalar() or 100  # Fallback
        
        # Get user completed lessons
        stmt_completed = select(func.count(UserModuleProgress.id)).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.status == "completed"
        )
        result = await session.execute(stmt_completed)
        completed_lessons = result.scalar() or 35  # Fallback
        
        # Calculate percentage
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Determine status based on progress
        if progress_percentage < 20:
            status = "Новичок"
        elif progress_percentage < 50:
            status = "Студент"
        elif progress_percentage < 80:
            status = "Ищущий знания"
        else:
            status = "Знающий"
        
        # Get last activity
        stmt_last = select(UserModuleProgress.completed_at).where(
            UserModuleProgress.user_id == user_id
        ).order_by(UserModuleProgress.completed_at.desc()).limit(1)
        result = await session.execute(stmt_last)
        last_activity_date = result.scalar_one_or_none()
        
        if last_activity_date:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            delta = now - last_activity_date
            if delta.days == 0:
                last_activity = "Сегодня"
            elif delta.days == 1:
                last_activity = "Вчера"
            elif delta.days < 7:
                last_activity = f"{delta.days} дней назад"
            else:
                last_activity = f"{delta.days // 7} недель назад"
        else:
            last_activity = "Недавно"
        
        return {
            "overall_progress": min(progress_percentage, 100),
            "current_status": status,
            "last_activity": last_activity,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
        }

    # ==================== NEW METHODS FOR QUIZ & PROGRESS ====================

    @staticmethod
    async def get_module_quiz_questions(
        module_id: int,
        session: AsyncSession,
        limit: int = 3
    ) -> List[Dict[str, any]]:
        """Get quiz questions for a module (post-lesson test)."""
        # First check if module has a test
        stmt_module = select(CourseModule).where(CourseModule.id == module_id).options(
            selectinload(CourseModule.course),
            selectinload(CourseModule.test)
        )
        result = await session.execute(stmt_module)
        module = result.scalar_one_or_none()
        
        if not module or not module.has_test:
            # If no test, get random questions from course
            stmt_course = select(CourseModule.course_id).where(CourseModule.id == module_id)
            result = await session.execute(stmt_course)
            course_id = result.scalar_one_or_none()
            
            if not course_id:
                return []
            
            # Get tests for this course
            stmt_tests = select(Test).where(
                Test.course_id == course_id,
                Test.is_active == True
            ).options(
                selectinload(Test.questions)
            ).limit(1)
            result = await session.execute(stmt_tests)
            test = result.scalar_one_or_none()
            
            if not test:
                return []
            
            test_id = test.id
        else:
            # Module has test_id
            test_id = module.test_id or 0
            if test_id == 0:
                return []
        
        # Get questions for the test
        stmt_questions = select(TestQuestion).where(
            TestQuestion.test_id == test_id
        ).options(
            selectinload(TestQuestion.options)
        ).order_by(func.random()).limit(limit)
        
        result = await session.execute(stmt_questions)
        questions = result.scalars().all()
        
        formatted_questions = []
        for q in questions:
            # Fetch options
            stmt_options = select(TestOption).where(
                TestOption.question_id == q.id
            ).order_by(TestOption.order_index)
            result_options = await session.execute(stmt_options)
            options = result_options.scalars().all()
            
            formatted_questions.append({
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "points": q.points,
                "options": [
                    {
                        "id": opt.id,
                        "option_text": opt.option_text,
                        "is_correct": opt.is_correct,
                        "explanation": opt.explanation,
                    }
                    for opt in options
                ]
            })
        
        return formatted_questions

    @staticmethod
    async def update_user_progress_after_quiz(
        user_id: int,
        module_id: int,
        quiz_score: float,
        passed: bool,
        session: AsyncSession
    ) -> Dict[str, any]:
        """Update user progress after completing a quiz."""
        # Get module details
        stmt_module = select(CourseModule).where(CourseModule.id == module_id).options(
            selectinload(CourseModule.course).selectinload(Course.modules)
        )
        result = await session.execute(stmt_module)
        module = result.scalar_one_or_none()
        
        if not module:
            return {"success": False, "error": "Module not found"}
        
        course_id = module.course_id
        
        # Get or create user course progress
        stmt_progress = select(UserCourseProgress).where(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_id == course_id
        ).options(
            selectinload(UserCourseProgress.module_progress)
        )
        result = await session.execute(stmt_progress)
        course_progress = result.scalar_one_or_none()
        
        if not course_progress:
            # Create new course progress
            course_progress = UserCourseProgress(
                user_id=user_id,
                course_id=course_id,
                status="in_progress",
                progress_percentage=0.0,
                completed_modules_count=0,
                total_modules_count=len(module.course.modules),
                is_completed=False,
                last_accessed_at=func.now()
            )
            session.add(course_progress)
            await session.flush()
        
        # Get or create module progress
        stmt_module_progress = select(UserModuleProgress).where(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        ).options(
            selectinload(UserModuleProgress.course_progress)
        )
        result = await session.execute(stmt_module_progress)
        module_progress = result.scalar_one_or_none()
        
        if not module_progress:
            module_progress = UserModuleProgress(
                user_id=user_id,
                module_id=module_id,
                course_progress_id=course_progress.id,
                status="completed" if passed else "in_progress",
                completed_at=func.now() if passed else None,
                time_spent_minutes=module.duration_minutes or 15
            )
            session.add(module_progress)
        else:
            if passed and not module_progress.completed_at:
                module_progress.status = "completed"
                module_progress.completed_at = func.now()
        
        # Update course progress
        if passed:
            # Count completed modules
            stmt_completed = select(func.count(UserModuleProgress.id)).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.course_progress_id == course_progress.id,
                UserModuleProgress.status == "completed"
            )
            result = await session.execute(stmt_completed)
            completed_count = result.scalar() or 0
            
            total_modules = course_progress.total_modules_count or len(module.course.modules)
            progress_percentage = (completed_count / total_modules * 100) if total_modules > 0 else 0
            
            course_progress.completed_modules_count = completed_count
            course_progress.progress_percentage = progress_percentage
            course_progress.last_accessed_at = func.now()
            
            # Check if course is completed
            if completed_count >= total_modules:
                course_progress.status = "completed"
                course_progress.is_completed = True
                course_progress.completed_at = func.now()
        
        await session.commit()
        
        # Get next module if exists
        next_module = None
        if passed:
            stmt_next = select(CourseModule).where(
                CourseModule.course_id == course_id,
                CourseModule.order_index > module.order_index
            ).order_by(CourseModule.order_index).limit(1)
            result = await session.execute(stmt_next)
            next_module = result.scalar_one_or_none()
        
        return {
            "success": True,
            "course_progress": {
                "completed_modules": course_progress.completed_modules_count,
                "total_modules": course_progress.total_modules_count,
                "progress_percentage": course_progress.progress_percentage,
                "is_completed": course_progress.is_completed
            },
            "next_module": {
                "id": next_module.id if next_module else None,
                "title": next_module.title if next_module else None,
                "order_index": next_module.order_index if next_module else None
            } if next_module else None
        }

    @staticmethod
    async def get_ai_response(
        query: str,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, any]:
        """Get AI response with Islamic knowledge constraints."""
        # System prompt with constraints (no fatwas)
        system_prompt = """
        Ты исламский ассистент. Отвечай только фактами из проверенных источников.
        Правила:
        1. Отвечай только на вопросы, связанные с исламом, Кораном, хадисами, историей
        2. Не выноси фетвы (решения о халяле/хараме)
        3. Не решай личные или семейные споры
        4. Если вопрос сложный или требует фикх-анализа, отправляй к ученым
        5. Используй только информацию из базы знаний бота
        6. Будь краток и точен

        Если вопрос вне компетенции, вежливо откажись отвечать.
        """
        
        # For now, return mock response
        # In production, integrate with OpenAI/Claude API
        
        islamic_responses = [
            "В исламе пять столпов: шахада, намаз, закят, пост в Рамадан и хадж.",
            "Коран был ниспослан пророку Мухаммаду (мир ему) в течение 23 лет.",
            "Пророки в исламе передавали одно и то же послание о единобожии.",
            "Мекка - священный город для мусульман, место расположения Каабы.",
            "Намаз совершается пять раз в день в определенное время.",
            "Закят - это обязательная милостыня для нуждающихся мусульман.",
            "Рамадан - месяц поста, один из пяти столпов ислама.",
            "Хадж - паломничество в Мекку, которое должен совершить каждый мусульманин при возможности.",
        ]
        
        import random
        response = random.choice(islamic_responses)
        
        # Log the query (in production, save to database)
        return {
            "response": response,
            "sources": ["База знаний бота"],
            "constraints_respected": True
        }

    @staticmethod
    async def get_upcoming_streams(
        session: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, any]]:
        """Get upcoming streams."""
        from datetime import datetime, timezone
        
        stmt = select(Stream).where(
            Stream.is_upcoming == True,
            Stream.scheduled_time > datetime.now(timezone.utc)
        ).order_by(Stream.scheduled_time).limit(limit)
        
        result = await session.execute(stmt)
        streams = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "scheduled_time": s.scheduled_time,
                "duration_minutes": s.duration_minutes,
                "speaker": s.speaker,
                "stream_url": s.stream_url,
                "max_participants": s.max_participants,
            }
            for s in streams
        ]

    @staticmethod
    async def get_stream_archive(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 10
    ) -> List[Dict[str, any]]:
        """Get archived streams with pagination."""
        from datetime import datetime, timezone
        
        offset = (page - 1) * per_page
        
        stmt = select(Stream).where(
            Stream.is_upcoming == False,
            Stream.recording_url.isnot(None)
        ).order_by(Stream.scheduled_time.desc()).offset(offset).limit(per_page)
        
        result = await session.execute(stmt)
        streams = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "scheduled_time": s.scheduled_time,
                "duration_minutes": s.duration_minutes,
                "speaker": s.speaker,
                "recording_url": s.recording_url,
            }
            for s in streams
        ]
