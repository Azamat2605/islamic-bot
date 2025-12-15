"""
Мок-данные для модуля Эфиры (Streams).
Для MVP используем hardcoded данные по требованиям.
"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Stream:
    """Модель эфира/стрима"""
    id: str  # Строковый ID, например "stream_1"
    title: str
    speaker: str
    description: str
    date: str  # Дата в формате "12.12.2025"
    url: str  # URL для просмотра (YouTube или другой)
    is_live: bool  # True для живых трансляций
    thumbnail_url: str  # URL превью
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.thumbnail_url:
            # Генерируем placeholder в зависимости от типа
            if self.is_live:
                self.thumbnail_url = "https://placehold.co/600x400/FF0000/FFFFFF?text=LIVE+Stream"
            else:
                self.thumbnail_url = "https://placehold.co/600x400/0000FF/FFFFFF?text=Recording"


# Hardcoded данные эфиров согласно требованиям
STREAMS_DATA: List[Stream] = [
    # Живые трансляции
    Stream(
        id="stream_1",
        title="Тафсир суры Аль-Фатиха",
        speaker="Шейх Абдуррахман ас-Саади",
        description="Подробное толкование первой суры Корана, включая её значение, "
                   "важность и уроки для повседневной жизни мусульманина.",
        date="15.12.2025",
        url="https://www.youtube.com/watch?v=example_live_1",
        is_live=True,
        thumbnail_url="https://placehold.co/600x400/FF0000/FFFFFF?text=LIVE+Stream"
    ),
    Stream(
        id="stream_2",
        title="Фикх намаза для начинающих",
        speaker="Доктор Мухаммад Салих аль-Мунаджид",
        description="Практическое руководство по правильному совершению намаза: "
                   "от омовения до завершающего таслима. Особое внимание уделено "
                   "распространённым ошибкам.",
        date="16.12.2025",
        url="https://www.youtube.com/watch?v=example_live_2",
        is_live=True,
        thumbnail_url="https://placehold.co/600x400/FF0000/FFFFFF?text=LIVE+Stream"
    ),
    
    # Записи
    Stream(
        id="stream_3",
        title="Жизнь Пророка Мухаммада (ﷺ): Мекканский период",
        speaker="Доктор Тарик Сувейдан",
        description="Детальный анализ жизни Пророка (ﷺ) в Мекке: от рождения до "
                   "хиджры. Исторический контекст, вызовы и уроки для современности.",
        date="10.12.2025",
        url="https://www.youtube.com/watch?v=example_recording_1",
        is_live=False,
        thumbnail_url="https://placehold.co/600x400/0000FF/FFFFFF?text=Recording"
    ),
    Stream(
        id="stream_4",
        title="Основы исламской акыды",
        speaker="Шейх Мухаммад ибн Салих аль-Усаймин",
        description="Систематическое изложение основ исламского вероубеждения "
                   "согласно Корану и Сунне. Подходит как для начинающих, так и "
                   "для углубления знаний.",
        date="05.12.2025",
        url="https://www.youtube.com/watch?v=example_recording_2",
        is_live=False,
        thumbnail_url="https://placehold.co/600x400/0000FF/FFFFFF?text=Recording"
    ),
    Stream(
        id="stream_5",
        title="Духовное очищение в исламе",
        speaker="Имам Абу Хамид аль-Газали (лекция по его трудам)",
        description="Обсуждение концепции ихсана (искренности) и таквы (богобоязненности) "
                   "на основе классических исламских текстов.",
        date="01.12.2025",
        url="https://www.youtube.com/watch?v=example_recording_3",
        is_live=False,
        thumbnail_url="https://placehold.co/600x400/0000FF/FFFFFF?text=Recording"
    ),
]


# Вспомогательные функции
def get_all_streams() -> List[Stream]:
    """Получить все эфиры"""
    return STREAMS_DATA


def get_stream_by_id(stream_id: str) -> Optional[Stream]:
    """Получить эфир по ID (строковому)"""
    for stream in STREAMS_DATA:
        if stream.id == stream_id:
            return stream
    return None


def get_live_streams() -> List[Stream]:
    """Получить только живые трансляции"""
    return [stream for stream in STREAMS_DATA if stream.is_live]


def get_recorded_streams() -> List[Stream]:
    """Получить только записи"""
    return [stream for stream in STREAMS_DATA if not stream.is_live]


def get_streams_sorted_by_date(reverse: bool = True) -> List[Stream]:
    """Получить эфиры, отсортированные по дате"""
    def parse_date(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            return datetime.min
    
    return sorted(
        STREAMS_DATA,
        key=lambda s: parse_date(s.date),
        reverse=reverse  # По умолчанию новые первыми
    )
