from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.states.profile import ProfileStates
from database.models import User, Settings
from database.crud import get_user_with_settings, get_or_create_user_with_settings
from bot.keyboards.inline.profile import profile_keyboard, gender_keyboard, language_keyboard
from bot.core.loader import i18n

router = Router(name="profile")


def get_profile_text(user: User, settings: Settings) -> str:
    """Формирует текст профиля с учетом всех настроек."""
    # Формат времени
    time_format_display = _("24h") if settings.time_format else _("12h")
    
    return _(
        "👤 *Ваш профиль*\n\n"
        "📊 *Статистика:*\n"
        "   • Дней подряд: *{streak_days}*\n\n"
        "👤 *Аккаунт:*\n"
        "   • Имя: *{full_name}*\n"
        "   • Пол: *{gender}*\n"
        "   • Город: *{city}*\n\n"
        "⚙️ *Настройки:*\n"
        "   • Язык: *{language}*\n"
        "   • Часовой пояс: *{timezone}*\n"
        "   • Формат времени: *{time_format}*\n"
    ).format(
        streak_days=user.streak_days,
        full_name=user.full_name,
        gender=user.gender if user.gender else _("Не указано"),
        city=user.city if user.city else _("Не указано"),
        language=settings.language.upper(),
        timezone=settings.timezone,
        time_format=time_format_display,
    )


@router.message(Command("profile"))
@router.message(F.text == __("👤 Мой профиль"))
async def profile_command_handler(message: types.Message, session: AsyncSession) -> None:
    """Обработчик команды /profile и кнопки '👤 Мой профиль'."""
    telegram_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Гарантируем, что пользователь и настройки существуют (создаём или обновляем)
    user, settings = await get_or_create_user_with_settings(session, telegram_id, full_name, username)
    # Настройки должны существовать благодаря get_or_create_user_with_settings, но на всякий случай проверяем
    if not settings:
        # Если настройки всё же отсутствуют (крайний случай), создаём их
        settings = Settings(user_id=user.id, language="ru", notification_on=True)
        session.add(settings)
        await session.commit()

    # Формируем текст профиля с улучшенным оформлением
    profile_text = get_profile_text(user, settings)

    # Отправляем сообщение с клавиатурой
    await message.answer(
        profile_text,
        reply_markup=profile_keyboard(user, settings),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "edit_gender")
async def edit_gender_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запуск FSM для ввода пола."""
    await callback.answer()
    await callback.message.answer(_("Введите ваш пол (например, Мужской, Женский):"))
    await state.set_state(ProfileStates.entering_gender)


@router.callback_query(F.data == "edit_city")
async def edit_city_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Запуск FSM для ввода города."""
    await callback.answer()
    await callback.message.answer(_("Введите ваш город:"))
    await state.set_state(ProfileStates.entering_city)




@router.callback_query(F.data.startswith("gender_"))
async def set_gender_from_keyboard_handler(
    callback: types.CallbackQuery, session: AsyncSession
) -> None:
    """Установка пола через предопределённые кнопки."""
    gender_map = {
        "gender_male": "Мужской",
        "gender_female": "Женский",
        "gender_other": "Другой",
    }
    gender_key = callback.data
    gender = gender_map.get(gender_key)
    if not gender:
        await callback.answer(_("Неверный выбор."), show_alert=True)
        return

    user = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = user.scalar_one_or_none()
    if not user:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return

    user.gender = gender
    await session.commit()

    # Обновляем сообщение профиля
    settings_result = await session.execute(
        select(Settings).where(Settings.user_id == user.id)
    )
    settings_list = settings_result.scalars().all()
    if not settings_list:
        await callback.answer(_("Настройки не найдены."), show_alert=True)
        return
    
    settings = settings_list[0]

    profile_text = get_profile_text(user, settings)

    await callback.message.edit_text(
        profile_text,
        reply_markup=profile_keyboard(user, settings),
        parse_mode="Markdown",
    )
    await callback.answer(_("Пол обновлён."))


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Отмена действия и возврат в профиль."""
    await state.clear()
    await callback.answer(_("Действие отменено."))
    # Можно вернуть в профиль, но пока просто закрываем клавиатуру
    await callback.message.delete()


import logging
from bot.cache.redis import clear_cache
from database.crud import get_user_language
from bot.keyboards.reply import get_main_menu

logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("lang_"))
async def set_language_handler(
    callback: types.CallbackQuery, session: AsyncSession
) -> None:
    """Установка языка."""
    lang = callback.data.split("_")[1]  # lang_ru, lang_en, etc.
    logger.info(f"User {callback.from_user.id} changing language to {lang}")
    user = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = user.scalar_one_or_none()
    if not user:
        await callback.answer(_("Пользователь не найден."), show_alert=True)
        return

    # Временный фикс для обработки дубликатов: берем первую запись
    settings_result = await session.execute(
        select(Settings).where(Settings.user_id == user.id)
    )
    settings_list = settings_result.scalars().all()
    if not settings_list:
        await callback.answer(_("Настройки не найдены."), show_alert=True)
        return
    
    # Берем первую запись (самую старую или новую - не важно, потом удалим дубликаты)
    settings = settings_list[0]

    settings.language = lang
    await session.commit()
    logger.info(f"Language saved to DB: {lang} for user_id {user.id}")
    
    # Инвалидация кэша для get_user_language (если используется)
    try:
        await clear_cache(get_user_language, session, callback.from_user.id)
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")

    # Устанавливаем локаль для текущего контекста
    i18n.ctx_locale.set(lang)
    current_locale = i18n.ctx_locale.get()
    logger.info(f"Locale set to {lang} in context, current_locale = {current_locale}")
    # Проверяем, какой перевод будет использован через i18n.gettext
    test_translation = i18n.gettext("Язык изменён.")
    logger.info(f"Translation test: '{test_translation}'")
    
    # Удаляем старое сообщение с настройками
    await callback.message.delete()
    
    # Отправляем новое сообщение с подтверждением и обновлённой главной клавиатурой
    await callback.message.answer(
        i18n.gettext("Язык изменён."),
        reply_markup=get_main_menu(),
    )


@router.message(ProfileStates.entering_gender)
async def process_gender(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """Обработка введённого пола."""
    gender = message.text.strip()
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user.scalar_one_or_none()
    if user:
        user.gender = gender
        await session.commit()

    await state.clear()
    await message.answer(_("Пол обновлён."))
    # Можно автоматически вернуть в профиль, но пока просто сообщение


@router.message(ProfileStates.entering_city)
async def process_city(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """Обработка введённого города."""
    city = message.text.strip()
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user.scalar_one_or_none()
    if user:
        user.city = city
        await session.commit()

    await state.clear()
    await message.answer(_("Город обновлён."))


# Старый обработчик для обратной совместимости
@router.callback_query(F.data == "profile_settings")
async def profile_settings_handler(callback: types.CallbackQuery) -> None:
    """Обработчик раздела 'Мой профиль / настройки'."""
    await callback.answer(
        "Раздел '👤 МОЙ ПРОФИЛЬ / НАСТРОЙКИ' теперь доступен через команду /profile.",
        show_alert=True,
    )
