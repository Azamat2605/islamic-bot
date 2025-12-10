"""
Сервис для работы с мероприятиями общины.
"""
import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.models import CommunityEvent, EventRegistration, EventType, EventStatus, RegistrationStatus, User
from bot.services.calendar_service import HijriCalendarService

logger = logging.getLogger(__name__)


class EventService:
    """Сервис для работы с мероприятиями."""
    
    @staticmethod
    async def get_upcoming_events(
        session: AsyncSession, 
        limit: int = 10,
        include_cancelled: bool = False
    ) -> List[CommunityEvent]:
        """Возвращает список предстоящих мероприятий."""
        query = select(CommunityEvent).where(
            CommunityEvent.start_time >= datetime.datetime.now()
        ).order_by(CommunityEvent.start_time)
        
        if not include_cancelled:
            query = query.where(CommunityEvent.status != EventStatus.CANCELLED)
        
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_event_by_id(session: AsyncSession, event_id: int) -> Optional[CommunityEvent]:
        """Возвращает мероприятие по ID."""
        query = select(CommunityEvent).where(CommunityEvent.id == event_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_registrations(
        session: AsyncSession, 
        user_id: int,
        include_cancelled: bool = False
    ) -> List[EventRegistration]:
        """Возвращает регистрации пользователя."""
        query = select(EventRegistration).where(
            EventRegistration.user_id == user_id
        ).join(CommunityEvent)
        
        if not include_cancelled:
            query = query.where(
                and_(
                    EventRegistration.status != RegistrationStatus.CANCELLED,
                    CommunityEvent.status != EventStatus.CANCELLED,
                    CommunityEvent.start_time >= datetime.datetime.now()
                )
            )
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def register_for_event(
        session: AsyncSession, 
        user_id: int, 
        event_id: int
    ) -> Tuple[bool, str]:
        """Регистрирует пользователя на мероприятие."""
        try:
            # Проверяем существование мероприятия
            event = await EventService.get_event_by_id(session, event_id)
            if not event:
                return False, "Мероприятие не найдено"
            
            if event.status == EventStatus.CANCELLED:
                return False, "Мероприятие отменено"
            
            if event.status == EventStatus.FINISHED:
                return False, "Мероприятие уже завершено"
            
            if event.start_time < datetime.datetime.now():
                return False, "Мероприятие уже началось"
            
            # Проверяем максимальное количество участников
            if event.max_participants:
                registrations_count = await EventService.get_event_registrations_count(session, event_id)
                if registrations_count >= event.max_participants:
                    return False, "Достигнуто максимальное количество участников"
            
            # Проверяем, не зарегистрирован ли уже пользователь
            existing_reg = await session.execute(
                select(EventRegistration).where(
                    and_(
                        EventRegistration.user_id == user_id,
                        EventRegistration.event_id == event_id
                    )
                )
            )
            existing_reg = existing_reg.scalar_one_or_none()
            
            if existing_reg:
                if existing_reg.status == RegistrationStatus.CANCELLED:
                    # Возобновляем регистрацию
                    existing_reg.status = RegistrationStatus.CONFIRMED
                    existing_reg.cancelled_at = None
                    await session.commit()
                    return True, "Регистрация возобновлена"
                else:
                    return False, "Вы уже зарегистрированы на это мероприятие"
            
            # Создаём новую регистрацию
            registration = EventRegistration(
                user_id=user_id,
                event_id=event_id,
                status=RegistrationStatus.CONFIRMED
            )
            session.add(registration)
            await session.commit()
            
            return True, "Успешная регистрация на мероприятие"
            
        except Exception as e:
            logger.error(f"Ошибка регистрации на мероприятие: {e}")
            await session.rollback()
            return False, f"Ошибка регистрации: {str(e)}"
    
    @staticmethod
    async def cancel_registration(
        session: AsyncSession,
        registration_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """Отменяет регистрацию пользователя."""
        try:
            query = select(EventRegistration).where(
                and_(
                    EventRegistration.id == registration_id,
                    EventRegistration.user_id == user_id
                )
            )
            result = await session.execute(query)
            registration = result.scalar_one_or_none()
            
            if not registration:
                return False, "Регистрация не найдена"
            
            if registration.status == RegistrationStatus.CANCELLED:
                return False, "Регистрация уже отменена"
            
            registration.status = RegistrationStatus.CANCELLED
            registration.cancelled_at = datetime.datetime.now()
            await session.commit()
            
            return True, "Регистрация отменена"
            
        except Exception as e:
            logger.error(f"Ошибка отмены регистрации: {e}")
            await session.rollback()
            return False, f"Ошибка отмены регистрации: {str(e)}"
    
    @staticmethod
    async def get_event_registrations_count(session: AsyncSession, event_id: int) -> int:
        """Возвращает количество подтверждённых регистраций на мероприятие."""
        query = select(func.count(EventRegistration.id)).where(
            and_(
                EventRegistration.event_id == event_id,
                EventRegistration.status == RegistrationStatus.CONFIRMED
            )
        )
        result = await session.execute(query)
        return result.scalar() or 0
    
    @staticmethod
    async def create_event(
        session: AsyncSession,
        title: str,
        start_time: datetime.datetime,
        created_by: int,
        description: Optional[str] = None,
        location: Optional[str] = None,
        event_type: EventType = EventType.LECTURE,
        max_participants: Optional[int] = None
    ) -> Tuple[bool, Optional[CommunityEvent], str]:
        """Создаёт новое мероприятие."""
        try:
            event = CommunityEvent(
                title=title,
                description=description,
                start_time=start_time,
                location=location,
                event_type=event_type,
                status=EventStatus.ACTIVE,
                max_participants=max_participants,
                created_by=created_by
            )
            
            session.add(event)
            await session.commit()
            await session.refresh(event)
            
            return True, event, "Мероприятие успешно создано"
            
        except Exception as e:
            logger.error(f"Ошибка создания мероприятия: {e}")
            await session.rollback()
            return False, None, f"Ошибка создания мероприятия: {str(e)}"
    
    @staticmethod
    async def update_event(
        session: AsyncSession,
        event_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[CommunityEvent], str]:
        """Обновляет информацию о мероприятии."""
        try:
            event = await EventService.get_event_by_id(session, event_id)
            if not event:
                return False, None, "Мероприятие не найдено"
            
            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)
            
            event.updated_at = datetime.datetime.now()
            await session.commit()
            await session.refresh(event)
            
            return True, event, "Мероприятие успешно обновлено"
            
        except Exception as e:
            logger.error(f"Ошибка обновления мероприятия: {e}")
            await session.rollback()
            return False, None, f"Ошибка обновления мероприятия: {str(e)}"
    
    @staticmethod
    async def cancel_event(session: AsyncSession, event_id: int) -> Tuple[bool, str]:
        """Отменяет мероприятие."""
        try:
            event = await EventService.get_event_by_id(session, event_id)
            if not event:
                return False, "Мероприятие не найдено"
            
            if event.status == EventStatus.CANCELLED:
                return False, "Мероприятие уже отменено"
            
            event.status = EventStatus.CANCELLED
            event.updated_at = datetime.datetime.now()
            
            # Отменяем все активные регистрации
            registrations = await session.execute(
                select(EventRegistration).where(
                    and_(
                        EventRegistration.event_id == event_id,
                        EventRegistration.status == RegistrationStatus.CONFIRMED
                    )
                )
            )
            
            for registration in registrations.scalars().all():
                registration.status = RegistrationStatus.CANCELLED
                registration.cancelled_at = datetime.datetime.now()
            
            await session.commit()
            
            return True, "Мероприятие отменено"
            
        except Exception as e:
            logger.error(f"Ошибка отмены мероприятия: {e}")
            await session.rollback()
            return False, f"Ошибка отмены мероприятия: {str(e)}"
    
    @staticmethod
    async def get_events_for_notification(
        session: AsyncSession,
        hours_before: int = 24
    ) -> List[Tuple[CommunityEvent, List[EventRegistration]]]:
        """Возвращает мероприятия, о которых нужно отправить уведомления."""
        now = datetime.datetime.now()
        notification_time = now + datetime.timedelta(hours=hours_before)
        
        query = select(CommunityEvent).where(
            and_(
                CommunityEvent.status == EventStatus.ACTIVE,
                CommunityEvent.start_time >= now,
                CommunityEvent.start_time <= notification_time
            )
        )
        
        result = await session.execute(query)
        events = list(result.scalars().all())
        
        events_with_registrations = []
        for event in events:
            # Получаем подтверждённые регистрации
            reg_query = select(EventRegistration).where(
                and_(
                    EventRegistration.event_id == event.id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED
                )
            )
            reg_result = await session.execute(reg_query)
            registrations = list(reg_result.scalars().all())
            
            events_with_registrations.append((event, registrations))
        
        return events_with_registrations
