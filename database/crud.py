from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import User, Settings


async def ensure_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
) -> User:
    """
    Проверяет существование пользователя по telegram_id.
    Если пользователь существует, обновляет username и full_name (если изменились).
    Если не существует, создаёт новую запись и связанные настройки (Settings).
    Гарантирует, что у пользователя есть настройки (создаёт при отсутствии).
    Возвращает объект пользователя.
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
        # flush, чтобы получить user.id
        await session.flush()
        settings = Settings(user_id=user.id, language="ru", notification_on=True)
        session.add(settings)
        # refresh не обязателен, но может обновить значения по умолчанию
        await session.refresh(user)
        return user

    # Обновляем username и full_name, если они изменились
    updated = False
    if user.username != username:
        user.username = username
        updated = True
    if user.full_name != full_name:
        user.full_name = full_name
        updated = True
    if updated:
        # Коммит не вызываем, оставляем на усмотрение middleware
        pass

    # Проверяем наличие настроек, создаём если отсутствуют
    settings_stmt = select(Settings).where(Settings.user_id == user.id)
    settings_result = await session.execute(settings_stmt)
    settings = settings_result.scalar_one_or_none()
    if not settings:
        settings = Settings(user_id=user.id, language="ru", notification_on=True)
        session.add(settings)
        # Не коммитим здесь, чтобы не нарушать транзакцию
        # Коммит будет выполнен middleware или вызывающим кодом

    return user


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
