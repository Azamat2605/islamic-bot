"""
Сервис для работы с религиозным календарём (Хиджра) и событиями.
"""
import datetime
from typing import Optional, List, Tuple
from hijri_converter import Hijri, Gregorian
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class HijriCalendarService:
    """Сервис для работы с датами Хиджры."""
    
    @staticmethod
    def gregorian_to_hijri(date: datetime.date) -> Hijri:
        """Конвертирует григорианскую дату в Хиджру."""
        try:
            return Hijri.from_gregorian(date.year, date.month, date.day)
        except Exception as e:
            logger.error(f"Ошибка конвертации даты {date}: {e}")
            # Возвращаем текущую дату Хиджры как fallback
            return Hijri.today()
    
    @staticmethod
    def hijri_to_gregorian(hijri_date: Hijri) -> datetime.date:
        """Конвертирует дату Хиджры в григорианскую."""
        try:
            return hijri_date.to_gregorian()
        except Exception as e:
            logger.error(f"Ошибка конвертации даты Хиджры {hijri_date}: {e}")
            return datetime.date.today()
    
    @staticmethod
    def get_current_hijri_month() -> Tuple[int, int]:
        """Возвращает текущий месяц и год Хиджры."""
        today_hijri = Hijri.today()
        return today_hijri.month, today_hijri.year
    
    @staticmethod
    def get_hijri_month_dates(year: int, month: int) -> List[Tuple[datetime.date, Hijri]]:
        """Возвращает список дат для указанного месяца Хиджры."""
        dates = []
        # Определяем количество дней в месяце Хиджры
        hijri_date = Hijri(year, month, 1)
        days_in_month = hijri_date.month_length()
        
        for day in range(1, days_in_month + 1):
            hijri = Hijri(year, month, day)
            gregorian = hijri.to_gregorian()
            dates.append((gregorian, hijri))
        
        return dates
    
    @staticmethod
    def get_important_islamic_dates(year: Optional[int] = None) -> List[dict]:
        """Возвращает список важных исламских дат для указанного года Хиджры."""
        if year is None:
            year = Hijri.today().year
        
        important_dates = [
            {
                "name": "Рамадан",
                "hijri_month": 9,
                "hijri_day": 1,
                "description": "Священный месяц поста"
            },
            {
                "name": "Ид аль-Фитр (Ураза-байрам)",
                "hijri_month": 10,
                "hijri_day": 1,
                "description": "Праздник разговения"
            },
            {
                "name": "День Арафа",
                "hijri_month": 12,
                "hijri_day": 9,
                "description": "День стояния на горе Арафат"
            },
            {
                "name": "Ид аль-Адха (Курбан-байрам)",
                "hijri_month": 12,
                "hijri_day": 10,
                "description": "Праздник жертвоприношения"
            },
            {
                "name": "Исра и Мирадж",
                "hijri_month": 7,
                "hijri_day": 27,
                "description": "Ночь вознесения Пророка ﷺ"
            },
            {
                "name": "День Ашура",
                "hijri_month": 1,
                "hijri_day": 10,
                "description": "10-й день месяца Мухаррам"
            },
            {
                "name": "Мавлид ан-Наби",
                "hijri_month": 3,
                "hijri_day": 12,
                "description": "День рождения Пророка Мухаммада ﷺ"
            },
        ]
        
        # Добавляем григорианские даты
        for event in important_dates:
            try:
                hijri = Hijri(year, event["hijri_month"], event["hijri_day"])
                event["gregorian_date"] = hijri.to_gregorian()
                event["hijri_date_str"] = str(hijri)
            except Exception as e:
                logger.error(f"Ошибка вычисления даты для {event['name']}: {e}")
                event["gregorian_date"] = None
                event["hijri_date_str"] = f"{event['hijri_day']} {event['hijri_month']} {year} г.х."
        
        return important_dates
    
    @staticmethod
    def get_upcoming_event(days_limit: int = 30) -> Optional[dict]:
        """Возвращает ближайшее важное событие в пределах указанного количества дней."""
        today = datetime.date.today()
        current_hijri = Hijri.today()
        
        events = HijriCalendarService.get_important_islamic_dates(current_hijri.year)
        events_next_year = HijriCalendarService.get_important_islamic_dates(current_hijri.year + 1)
        all_events = events + events_next_year
        
        upcoming = []
        for event in all_events:
            if event["gregorian_date"] and event["gregorian_date"] >= today:
                days_until = (event["gregorian_date"] - today).days
                if days_until <= days_limit:
                    event_copy = event.copy()
                    event_copy["days_until"] = days_until
                    upcoming.append(event_copy)
        
        if not upcoming:
            return None
        
        # Сортируем по количеству дней до события
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming[0]
    
    @staticmethod
    def get_hijri_month_name(month: int) -> str:
        """Возвращает название месяца Хиджры."""
        month_names = {
            1: "Мухаррам",
            2: "Сафар",
            3: "Раби аль-авваль",
            4: "Раби ас-сани",
            5: "Джумада аль-уля",
            6: "Джумада ас-сания",
            7: "Раджаб",
            8: "Шаабан",
            9: "Рамадан",
            10: "Шавваль",
            11: "Зуль-када",
            12: "Зуль-хиджа"
        }
        return month_names.get(month, f"Месяц {month}")
    
    @staticmethod
    def get_juma_dates_for_month(year: int, month: int) -> List[datetime.date]:
        """Возвращает даты пятниц (Джума) для указанного григорианского месяца."""
        juma_dates = []
        # Первый день месяца
        current_date = datetime.date(year, month, 1)
        # Последний день месяца
        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        # Находим первую пятницу
        while current_date <= last_day:
            if current_date.weekday() == 4:  # 4 = пятница
                juma_dates.append(current_date)
                current_date += datetime.timedelta(days=7)
            else:
                current_date += datetime.timedelta(days=1)
        
        return juma_dates
