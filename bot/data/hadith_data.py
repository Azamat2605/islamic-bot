"""
Мок-данные для модуля Хадисов.
Для MVP используем по 5 хадисов из каждого сборника.
"""

import random
from typing import Optional, List, Dict

HADITH_DATA = {
    "books": [
        {
            "id": "bukhari",
            "name_arabic": "صحيح البخاري",
            "name_transliteration": "Sahih al-Bukhari",
            "name_translation": "Сахих Аль-Бухари",
            "total_hadiths": 7563,
            "description": "Сборник достоверных хадисов, составленный имамом Аль-Бухари.",
            "hadiths": [
                {
                    "id": "bukhari_1",
                    "book_id": "bukhari",
                    "number": 1,
                    "arabic_text": "إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى",
                    "transliteration": "Innamal a'malu binniyyat, wa innama likulli imri'in ma nawa",
                    "translation": {
                        "kuliev": "Поистине, дела оцениваются только по намерениям, и, поистине, каждому человеку достанется только то, что он намеревался обрести.",
                        "osmanov": "Воистину, дела оцениваются по намерениям, и каждому человеку — то, что он намеревался."
                    },
                    "narrator": "Умар ибн аль-Хаттаб",
                    "chapter": "Книга Откровения",
                    "source": "Сахих Аль-Бухари, Книга 1, Хадис 1",
                    "tags": ["намерение", "вера"],
                    "grade": "сахих",
                    "related_ayahs": []
                },
                {
                    "id": "bukhari_2",
                    "book_id": "bukhari",
                    "number": 2,
                    "arabic_text": "بني الإسلام على خمس",
                    "transliteration": "Buniyal Islamu 'ala khams",
                    "translation": {
                        "kuliev": "Ислам построен на пяти столпах: свидетельстве, что нет божества, кроме Аллаха, и что Мухаммад — посланник Аллаха, совершении молитвы, выплате закята, хадже и посте в месяц Рамадан.",
                        "osmanov": "Ислам зиждется на пяти столпах: свидетельстве, что нет божества, кроме Аллаха, и что Мухаммад — посланник Аллаха, совершении молитвы, выплате закята, хадже и посте в Рамадан."
                    },
                    "narrator": "Абдуллах ибн Умар",
                    "chapter": "Книга Веры",
                    "source": "Сахих Аль-Бухари, Книга 2, Хадис 8",
                    "tags": ["столпы", "ислам"],
                    "grade": "сахих",
                    "related_ayahs": []
                },
                {
                    "id": "bukhari_3",
                    "book_id": "bukhari",
                    "number": 3,
                    "arabic_text": "إن الله لا ينظر إلى صوركم وأموالكم، ولكن ينظر إلى قلوبكم وأعمالكم",
                    "transliteration": "Innallaha la yanzuru ila suwarikum wa amwalikum, walakin yanzuru ila qulubikum wa a'malikum",
                    "translation": {
                        "kuliev": "Поистине, Аллах не смотрит на ваши облики и ваше имущество, но смотрит на ваши сердца и ваши дела.",
                        "osmanov": "Воистину, Аллах не смотрит на ваши лица и ваше имущество, а смотрит на ваши сердца и ваши деяния."
                    },
                    "narrator": "Абу Хурайра",
                    "chapter": "Книга Веры",
                    "source": "Сахих Аль-Бухари, Книга 2, Хадис 49",
                    "tags": ["сердце", "дела"],
                    "grade": "сахих",
                    "related_ayahs": []
                }
            ]
        },
        {
            "id": "muslim",
            "name_arabic": "صحيح مسلم",
            "name_transliteration": "Sahih Muslim",
            "name_translation": "Сахих Муслим",
            "total_hadiths": 7563,
            "description": "Второй по авторитетности сборник достоверных хадисов после Сахих Аль-Бухари.",
            "hadiths": [
                {
                    "id": "muslim_1",
                    "book_id": "muslim",
                    "number": 1,
                    "arabic_text": "من حسن إسلام المرء تركه ما لا يعنيه",
                    "transliteration": "Man husna islamil mar'i tarkuhu ma la ya'nihi",
                    "translation": {
                        "kuliev": "Признаком хорошего исповедания ислама человеком является его отказ от того, что его не касается.",
                        "osmanov": "Признаком совершенства ислама человека является оставление им того, что его не касается."
                    },
                    "narrator": "Абу Хурайра",
                    "chapter": "Книга Веры",
                    "source": "Сахих Муслим, Книга 1, Хадис 1",
                    "tags": ["ислам", "этика"],
                    "grade": "сахих",
                    "related_ayahs": []
                },
                {
                    "id": "muslim_2",
                    "book_id": "muslim",
                    "number": 2,
                    "arabic_text": "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه",
                    "transliteration": "La yu'minu ahadukum hatta yuhibba li akhihi ma yuhibbu li nafsihi",
                    "translation": {
                        "kuliev": "Не уверует никто из вас по-настоящему, пока не станет желать своему брату того же, чего желает себе.",
                        "osmanov": "Не уверует никто из вас, пока не будет желать брату своему того же, чего желает себе."
                    },
                    "narrator": "Анас ибн Малик",
                    "chapter": "Книга Веры",
                    "source": "Сахих Муслим, Книга 1, Хадис 72",
                    "tags": ["любовь", "братство"],
                    "grade": "сахих",
                    "related_ayahs": []
                }
            ]
        },
        {
            "id": "nawawi",
            "name_arabic": "الأربعون النووية",
            "name_transliteration": "Al-Arba'in al-Nawawiyyah",
            "name_translation": "40 хадисов Ан-Навави",
            "total_hadiths": 42,
            "description": "Сборник из 42 важнейших хадисов, охватывающих основы религии.",
            "hadiths": [
                {
                    "id": "nawawi_1",
                    "book_id": "nawawi",
                    "number": 1,
                    "arabic_text": "إنما الأعمال بالنيات",
                    "transliteration": "Innamal a'malu binniyyat",
                    "translation": {
                        "kuliev": "Поистине, дела оцениваются только по намерениям.",
                        "osmanov": "Воистину, дела оцениваются по намерениям."
                    },
                    "narrator": "Умар ибн аль-Хаттаб",
                    "chapter": "Первый хадис",
                    "source": "40 хадисов Ан-Навави, Хадис 1",
                    "tags": ["намерение"],
                    "grade": "сахих",
                    "related_ayahs": []
                },
                {
                    "id": "nawawi_2",
                    "book_id": "nawawi",
                    "number": 2,
                    "arabic_text": "بني الإسلام على خمس",
                    "transliteration": "Buniyal Islamu 'ala khams",
                    "translation": {
                        "kuliev": "Ислам построен на пяти столпах...",
                        "osmanov": "Ислам зиждется на пяти столпах..."
                    },
                    "narrator": "Абдуллах ибн Умар",
                    "chapter": "Второй хадис",
                    "source": "40 хадисов Ан-Навави, Хадис 2",
                    "tags": ["столпы"],
                    "grade": "сахих",
                    "related_ayahs": []
                }
            ]
        }
    ],
    "translators": [
        {"id": "kuliev", "name": "Эльмир Кулиев"},
        {"id": "osmanov", "name": "Магомед-Нури Османов"}
    ]
}


def get_book_by_id(book_id: str) -> Optional[Dict]:
    """Получить сборник по ID."""
    for book in HADITH_DATA["books"]:
        if book["id"] == book_id:
            return book
    return None


def get_all_books() -> List[Dict]:
    """Получить все сборники."""
    return HADITH_DATA["books"]


def get_hadith_by_id(hadith_id: str) -> Optional[Dict]:
    """Получить хадис по ID."""
    for book in HADITH_DATA["books"]:
        for hadith in book["hadiths"]:
            if hadith["id"] == hadith_id:
                return hadith
    return None


def get_random_hadith(book_id: Optional[str] = None) -> Dict:
    """Получить случайный хадис из указанного сборника или из всех."""
    all_hadiths = []
    for book in HADITH_DATA["books"]:
        if book_id is None or book["id"] == book_id:
            all_hadiths.extend(book["hadiths"])
    if not all_hadiths:
        raise ValueError("Нет доступных хадисов")
    return random.choice(all_hadiths)


def get_hadiths_by_book(book_id: str, page: int = 0, items_per_page: int = 10) -> List[Dict]:
    """Получить страницу хадисов из сборника (для пагинации)."""
    book = get_book_by_id(book_id)
    if not book:
        return []
    hadiths = book["hadiths"]
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    return hadiths[start_idx:end_idx]


def get_total_pages(book_id: str, items_per_page: int = 10) -> int:
    """Получить общее количество страниц для сборника."""
    book = get_book_by_id(book_id)
    if not book:
        return 0
    total = len(book["hadiths"])
    return (total + items_per_page - 1) // items_per_page
