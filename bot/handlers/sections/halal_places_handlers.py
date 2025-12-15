from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.halal_service import HalalService
from bot.states.halal import HalalStates
from bot.keyboards.inline.halal import (
    get_halal_main_keyboard,
    get_categories_keyboard,
    get_location_request_keyboard,
    get_places_list_keyboard,
    get_place_details_keyboard
)
from bot.keyboards.reply import get_main_menu
from bot.callbacks.halal import HalalCallback, HalalAction

router = Router(name="halal_places")


# Главный обработчик раздела Halal Places
@router.message(F.text == __("Халяль места"))
@router.callback_query(F.data == "halal_places")
async def halal_places_main_handler(
    event: types.Message | types.CallbackQuery,
    session: AsyncSession
) -> None:
    """
    Главный экран Halal Places.
    Обрабатывает как нажатие кнопки в Reply-клавиатуре, так и callback из Inline-клавиатуры.
    """
    # Получаем статистику по категориям
    counts = await HalalService.get_counts_by_category(session)
    
    # Формируем текст со статистикой
    text = _(
        "🥩 ХАЛЯЛЬ МЕСТА\n\n"
        "Найдите проверенные места поблизости:\n"
        "• Мечети для молитвы\n"
        "• Рестораны с халяль едой\n"
        "• Магазины с халяль продуктами\n"
        "• Магазины одежды\n\n"
        "📊 Статистика:\n"
        "🕌 Мечети: {mosques_count}\n"
        "🍴 Рестораны: {restaurants_count}\n"
        "🛒 Магазины: {shops_count}\n\n"
        "Выберите действие:"
    ).format(
        mosques_count=counts.get("mosque", 0),
        restaurants_count=counts.get("restaurant", 0),
        shops_count=counts.get("shop", 0) + counts.get("clothes", 0)
    )
    
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(
            text,
            reply_markup=get_halal_main_keyboard(counts)
        )
        await event.answer()
    else:  # Message
        await event.answer(
            text,
            reply_markup=get_halal_main_keyboard(counts)
        )


# Обработчик ближайших мест
@router.callback_query(HalalCallback.filter(F.action == HalalAction.NEAREST))
async def nearest_places_handler(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Запрос геолокации для поиска ближайших мест.
    """
    text = _(
        "📍 БЛИЖАЙШИЕ МЕСТА\n\n"
        "Для поиска мест поблизости, пожалуйста, поделитесь своей геолокацией.\n\n"
        "Нажмите кнопку ниже, чтобы отправить ваше местоположение:"
    )
    
    await callback.message.edit_text(text)
    await callback.message.answer(
        _("Пожалуйста, отправьте ваше местоположение:"),
        reply_markup=get_location_request_keyboard()
    )
    
    await state.set_state(HalalStates.waiting_for_location)
    await callback.answer()


# Обработчик полученной геолокации
@router.message(HalalStates.waiting_for_location, F.location)
async def location_received_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """
    Обработка полученной геолокации.
    """
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    
    # Получаем ближайшие места
    nearby_places = await HalalService.get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        session=session,
        limit=5,
        radius_km=10.0
    )
    
    if not nearby_places:
        text = _(
            "📍 БЛИЖАЙШИЕ МЕСТА\n\n"
            "К сожалению, в радиусе 10 км не найдено халяль мест.\n"
            "Попробуйте поискать по категориям."
        )
        await message.answer(text, reply_markup=get_categories_keyboard())
        await state.clear()
        return
    
    # Формируем текст со списком мест
    places_text = ""
    for i, place in enumerate(nearby_places, 1):
        place_type_emoji = {
            "mosque": "🕌",
            "restaurant": "🍴",
            "shop": "🛒",
            "clothes": "👕",
            "other": "📍"
        }.get(place["place_type"], "📍")
        
        places_text += _(
            "{i}. {emoji} {title}\n"
            "   📍 ~{distance} км\n"
            "   🕒 {working_hours}\n\n"
        ).format(
            i=i,
            emoji=place_type_emoji,
            title=place["title"],
            distance=place["distance"],
            working_hours=place["working_hours"] or _("Не указано")
        )
    
    text = _("📍 БЛИЖАЙШИЕ МЕСТА (отсортированы по расстоянию)\n\n{places}").format(
        places=places_text
    )
    
    await message.answer(
        text,
        reply_markup=get_places_list_keyboard(nearby_places)
    )
    await state.clear()


# Обработчик выбора категории
@router.callback_query(HalalCallback.filter(F.action == HalalAction.CATEGORY))
async def category_selection_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ списка мест в выбранной категории.
    Если category is None - показываем клавиатуру выбора категорий.
    """
    category = callback_data.category
    
    # Если category не указан, показываем клавиатуру выбора категорий
    if not category:
        await callback.message.edit_text(
            _("🔍 ПОИСК ПО КАТЕГОРИЯМ\n\nВыберите категорию:"),
            reply_markup=get_categories_keyboard()
        )
        await callback.answer()
        return
    
    # Маппинг категорий на русские названия
    category_names = {
        "mosque": "🕌 МЕЧЕТИ",
        "restaurant": "🍴 РЕСТОРАНЫ",
        "shop": "🛒 МАГАЗИНЫ",
        "clothes": "👕 МАГАЗИНЫ ОДЕЖДЫ"
    }
    
    category_name = category_names.get(category, _("Категория"))
    
    # Получаем места по категории
    places = await HalalService.get_places_by_category(
        category=category,
        session=session,
        limit=10
    )
    
    if not places:
        text = _(
            "{category_name}\n\n"
            "В этой категории пока нет мест.\n"
            "Мы работаем над добавлением новых мест!"
        ).format(category_name=category_name)
        
        await callback.message.edit_text(
            text,
            reply_markup=get_categories_keyboard()
        )
        await callback.answer()
        return
    
    # Формируем текст со списком мест
    places_text = ""
    for i, place in enumerate(places, 1):
        places_text += _(
            "{i}. {title}\n"
            "   📍 {address}\n"
            "   🕒 {working_hours}\n\n"
        ).format(
            i=i,
            title=place["title"],
            address=place["address"],
            working_hours=place["working_hours"] or _("Не указано")
        )
    
    text = _("{category_name}\n\n{places}").format(
        category_name=category_name,
        places=places_text
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_places_list_keyboard(places)
    )
    await callback.answer()


# Обработчик деталей места
@router.callback_query(HalalCallback.filter(F.action == HalalAction.PLACE_DETAILS))
async def place_details_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ детальной информации о месте.
    """
    place_id = callback_data.place_id
    
    # Получаем детали места
    place = await HalalService.get_place_details(place_id, session)
    
    if not place:
        await callback.answer(_("Место не найдено."), show_alert=True)
        return
    
    # Маппинг типов мест на эмодзи
    place_type_emoji = {
        "mosque": "🕌",
        "restaurant": "🍴",
        "shop": "🛒",
        "clothes": "👕",
        "other": "📍"
    }.get(place["place_type"], "📍")
    
    # Формируем текст
    text = _(
        "{emoji} {title}\n\n"
        "📍 Адрес: {address}\n"
        "🕒 Время работы: {working_hours}\n"
        "📞 Телефон: {phone}\n"
        "{verified}\n\n"
        "{description}"
    ).format(
        emoji=place_type_emoji,
        title=place["title"],
        address=place["address"],
        working_hours=place["working_hours"] or _("Не указано"),
        phone=place["phone"] or _("Не указан"),
        verified=_("✅ Проверено") if place["is_verified"] else "",
        description=place["description"] or _("Описание отсутствует.")
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_place_details_keyboard(place_id, is_favorite=False)
    )
    await callback.answer()


# Обработчик показа на карте
@router.callback_query(HalalCallback.filter(F.action == HalalAction.MAP))
async def show_on_map_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Показ места на карте.
    """
    place_id = callback_data.place_id
    
    if place_id == 0:
        # Показать все места на карте (заглушка)
        await callback.answer(
            _("Функция показа всех мест на карте в разработке."),
            show_alert=True
        )
        return
    
    # Получаем детали места
    place = await HalalService.get_place_details(place_id, session)
    
    if not place:
        await callback.answer(_("Место не найдено."), show_alert=True)
        return
    
    # Отправляем местоположение
    await callback.message.answer_venue(
        latitude=place["latitude"],
        longitude=place["longitude"],
        title=place["title"],
        address=place["address"]
    )
    
    await callback.answer()


# Обработчик кнопки "Назад"
@router.callback_query(HalalCallback.filter(F.action == HalalAction.BACK))
async def back_handler(
    callback: types.CallbackQuery,
    callback_data: HalalCallback,
    session: AsyncSession
) -> None:
    """
    Обработка кнопки "Назад".
    """
    from_state = callback_data.from_state
    
    if from_state == "main":
        # Возврат из меню Халяль в ГЛАВНОЕ МЕНЮ БОТА
        # Удаляем текущее сообщение и отправляем главное меню
        await callback.message.delete()
        await callback.message.answer(
            _("🏠 ГЛАВНОЕ МЕНЮ"),
            reply_markup=get_main_menu()
        )
    
    elif from_state == "categories":
        # Возврат к выбору категории
        await callback.message.edit_text(
            _("🔍 ПОИСК ПО КАТЕГОРИЯМ\n\nВыберите категорию:"),
            reply_markup=get_categories_keyboard()
        )
    
    elif from_state in ["list", "details"]:
        # Возврат к списку категорий
        await callback.message.edit_text(
            _("🔍 ПОИСК ПО КАТЕГОРИЯМ\n\nВыберите категорию:"),
            reply_markup=get_categories_keyboard()
        )
    
    await callback.answer()


# Обработчик кнопки "Назад" в Reply клавиатуре
@router.message(HalalStates.waiting_for_location, F.text == "🔙 Назад")
async def back_from_location_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """
    Обработка кнопки "Назад" в состоянии ожидания геолокации.
    """
    await state.clear()
    
    # Возвращаемся к главному меню
    counts = await HalalService.get_counts_by_category(session)
    
    text = _(
        "🥩 ХАЛЯЛЬ МЕСТА\n\n"
        "Найдите проверенные места поблизости:\n"
        "• Мечети для молитвы\n"
        "• Рестораны с халяль едой\n"
        "• Магазины с халяль продуктами\n"
        "• Магазины одежды\n\n"
        "📊 Статистика:\n"
        "🕌 Мечети: {mosques_count}\n"
        "🍴 Рестораны: {restaurants_count}\n"
        "🛒 Магазины: {shops_count}\n\n"
        "Выберите действие:"
    ).format(
        mosques_count=counts.get("mosque", 0),
        restaurants_count=counts.get("restaurant", 0),
        shops_count=counts.get("shop", 0) + counts.get("clothes", 0)
    )
    
    await message.answer(
        text,
        reply_markup=get_halal_main_keyboard(counts)
    )
