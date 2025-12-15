"""
Данные для модуля Хадисы (группировка по темам).
Для MVP используем hardcoded данные по требованиям.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Hadith:
    """Модель хадиса"""
    id: str  # Строковый ID, например "hadith_1"
    text: str  # Текст хадиса
    source: str  # Источник, например "Bukhari, 123"
    topic: str  # Тема (topic_id)


@dataclass
class HadithTopic:
    """Модель темы хадисов"""
    id: str  # Строковый ID, например "topic_nawawi"
    name: str  # Название темы
    description: str  # Описание темы
    hadiths: List[Hadith]  # Список хадисов в этой теме


# Hardcoded данные хадисов согласно требованиям
HADITH_TOPICS_DATA: List[HadithTopic] = [
    # 1. "40 Hadiths of Nawawi" (первые 3-5 хадисов)
    HadithTopic(
        id="topic_nawawi",
        name="40 хадисов Ан-Навави",
        description="Сборник из 42 важнейших хадисов, охватывающих основы религии.",
        hadiths=[
            Hadith(
                id="nawawi_1",
                text="Поистине, дела оцениваются только по намерениям, и, поистине, каждому человеку достанется только то, что он намеревался обрести.",
                source="Аль-Бухари, Муслим",
                topic="topic_nawawi"
            ),
            Hadith(
                id="nawawi_2",
                text="Ислам построен на пяти столпах: свидетельстве, что нет божества, кроме Аллаха, и что Мухаммад — посланник Аллаха, совершении молитвы, выплате закята, хадже и посте в месяц Рамадан.",
                source="Аль-Бухари, Муслим",
                topic="topic_nawawi"
            ),
            Hadith(
                id="nawawi_3",
                text="Признаком хорошего исповедания ислама человеком является его отказ от того, что его не касается.",
                source="Тирмизи, Ибн Маджа",
                topic="topic_nawawi"
            ),
            Hadith(
                id="nawawi_4",
                text="Не уверует никто из вас по-настоящему, пока не станет желать своему брату того же, чего желает себе.",
                source="Аль-Бухари, Муслим",
                topic="topic_nawawi"
            ),
            Hadith(
                id="nawawi_5",
                text="Запретное очевидно, и дозволенное очевидно, а между ними находится сомнительное.",
                source="Аль-Бухари, Муслим",
                topic="topic_nawawi"
            ),
        ]
    ),
    
    # 2. "Character (Adab)" (3-5 хадисов о хороших манерах)
    HadithTopic(
        id="topic_adab",
        name="Характер и нравственность (Адаб)",
        description="Хадисы о хороших манерах, этикете и нравственности в исламе.",
        hadiths=[
            Hadith(
                id="adab_1",
                text="Самый лучший из вас тот, кто обладает наилучшим нравом.",
                source="Аль-Бухари, Муслим",
                topic="topic_adab"
            ),
            Hadith(
                id="adab_2",
                text="Вера верующего не будет совершенной, пока он не станет желать своему брату того же, чего желает себе.",
                source="Аль-Бухари, Муслим",
                topic="topic_adab"
            ),
            Hadith(
                id="adab_3",
                text="Улыбка в лицо твоему брату — это милостыня (садака).",
                source="Тирмизи",
                topic="topic_adab"
            ),
            Hadith(
                id="adab_4",
                text="Тот, кто не проявляет милосердия к младшим и не уважает старших, не из нас.",
                source="Тирмизи",
                topic="topic_adab"
            ),
            Hadith(
                id="adab_5",
                text="Поистине, Аллах любит, когда кто-либо из вас выполняет работу, он выполняет её наилучшим образом.",
                source="Байхаки",
                topic="topic_adab"
            ),
        ]
    ),
    
    # 3. "Prayer (Salah)" (3-5 хадисов о важности намаза)
    HadithTopic(
        id="topic_salah",
        name="Намаз (Салят)",
        description="Хадисы о важности, достоинствах и правильном совершении намаза.",
        hadiths=[
            Hadith(
                id="salah_1",
                text="Первое, за что будет спрошен раб в День Воскресения — это намаз. Если намаз его будет хорош, то и остальные его дела будут хороши. Если намаз его будет плох, то и остальные его дела будут плохи.",
                source="Табарани",
                topic="topic_salah"
            ),
            Hadith(
                id="salah_2",
                text="Между человеком и неверием — оставление намаза.",
                source="Муслим",
                topic="topic_salah"
            ),
            Hadith(
                id="salah_3",
                text="Если бы у дверей дома кого-либо из вас протекала река, и он купался бы в ней пять раз в день, разве осталась бы на нём грязь? Так же и пять ежедневных молитв очищают человека от грехов.",
                source="Аль-Бухари, Муслим",
                topic="topic_salah"
            ),
            Hadith(
                id="salah_4",
                text="Самый тяжёлый намаз для лицемеров — ночной и утренний намазы.",
                source="Аль-Бухари, Муслим",
                topic="topic_salah"
            ),
            Hadith(
                id="salah_5",
                text="Когда кто-либо из вас совершает намаз, он разговаривает со своим Господом.",
                source="Аль-Бухари",
                topic="topic_salah"
            ),
        ]
    ),
]


# Вспомогательные функции
def get_all_topics() -> List[HadithTopic]:
    """Получить все темы хадисов"""
    return HADITH_TOPICS_DATA


def get_topic_by_id(topic_id: str) -> Optional[HadithTopic]:
    """Получить тему по ID"""
    for topic in HADITH_TOPICS_DATA:
        if topic.id == topic_id:
            return topic
    return None


def get_hadith_by_id(hadith_id: str) -> Optional[Hadith]:
    """Получить хадис по ID"""
    for topic in HADITH_TOPICS_DATA:
        for hadith in topic.hadiths:
            if hadith.id == hadith_id:
                return hadith
    return None


def get_hadiths_by_topic(topic_id: str) -> List[Hadith]:
    """Получить все хадисы по теме"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return []
    return topic.hadiths


def get_hadith_by_topic_and_index(topic_id: str, index: int) -> Optional[Hadith]:
    """Получить хадис по теме и индексу (0-based)"""
    hadiths = get_hadiths_by_topic(topic_id)
    if 0 <= index < len(hadiths):
        return hadiths[index]
    return None


def get_total_hadiths_in_topic(topic_id: str) -> int:
    """Получить общее количество хадисов в теме"""
    hadiths = get_hadiths_by_topic(topic_id)
    return len(hadiths)
