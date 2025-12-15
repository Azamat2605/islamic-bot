"""
Мок-данные для модуля Знаний.
Для MVP используем только первые 10 и последние 10 сур.
"""

QURAN_DATA = {
    "surahs": [
        # Первые 10 сур
        {
            "id": 1,
            "name_arabic": "الفاتحة",
            "name_transliteration": "Al-Fatiha",
            "name_translation": "Открывающая",
            "verse_count": 7,
            "revelation_type": "Meccan",
            "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ الرَّحْمَٰنِ الرَّحِيمِ مَالِكِ يَوْمِ الدِّينِ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
            "translations": {
                "kuliev": "Во имя Аллаха, Милостивого, Милосердного! Хвала Аллаху, Господу миров, Милостивому, Милосердному, Властелину Дня воздаяния! Тебе одному мы поклоняемся и Тебя одного молим о помощи. Веди нас прямым путем, путем тех, кого Ты облагодетельствовал, не тех, на кого пал гнев, и не заблудших.",
                "osmanov": "Во имя Аллаха, Милостивого, Милосердного! Хвала Аллаху, Господу миров, Милостивому, Милосердному, Царю в День суд! Тебе мы поклоняемся и у Тебя просим помощи. Веди нас по дороге прямой, по дороге тех, которых Ты облагодетельствовал, не тех, что под гневом, и не заблудших."
            }
        },
        {
            "id": 2,
            "name_arabic": "البقرة",
            "name_transliteration": "Al-Baqarah",
            "name_translation": "Корова",
            "verse_count": 286,
            "revelation_type": "Medinan",
            "arabic_text": "الم ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ",
            "translations": {
                "kuliev": "Алиф. Лам. Мим. Это Писание, в котором нет сомнения, является верным руководством для богобоязненных.",
                "osmanov": "Алиф, лам, мим. Это - Писание, в котором нет сомнения, - руководство для богобоязненных."
            }
        },
        {
            "id": 3,
            "name_arabic": "آل عمران",
            "name_transliteration": "Ali 'Imran",
            "name_translation": "Семейство Имрана",
            "verse_count": 200,
            "revelation_type": "Medinan",
            "arabic_text": "الم اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
            "translations": {
                "kuliev": "Алиф. Лам. Мим. Аллах - нет божества, кроме Него, Живого, Вседержителя.",
                "osmanov": "Алиф, лам, мим. Аллах - нет божества, кроме Него, живого, сущего."
            }
        },
        {
            "id": 4,
            "name_arabic": "النساء",
            "name_transliteration": "An-Nisa",
            "name_translation": "Женщины",
            "verse_count": 176,
            "revelation_type": "Medinan",
            "arabic_text": "يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ الَّذِي خَلَقَكُمْ مِنْ نَفْسٍ وَاحِدَةٍ",
            "translations": {
                "kuliev": "О люди! Бойтесь вашего Господа, Который сотворил вас из одной души.",
                "osmanov": "О люди! Бойтесь вашего Господа, который создал вас из одной души."
            }
        },
        {
            "id": 5,
            "name_arabic": "المائدة",
            "name_transliteration": "Al-Ma'idah",
            "name_translation": "Трапеза",
            "verse_count": 120,
            "revelation_type": "Medinan",
            "arabic_text": "يَا أَيُّهَا الَّذِينَ آمَنُوا أَوْفُوا بِالْعُقُودِ",
            "translations": {
                "kuliev": "О те, которые уверовали! Будьте верны обязательствам.",
                "osmanov": "О вы, которые уверовали! Будьте верны договорам."
            }
        },
        {
            "id": 6,
            "name_arabic": "الأنعام",
            "name_transliteration": "Al-An'am",
            "name_translation": "Скот",
            "verse_count": 165,
            "revelation_type": "Meccan",
            "arabic_text": "الْحَمْدُ لِلَّهِ الَّذِي خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ",
            "translations": {
                "kuliev": "Хвала Аллаху, Который сотворил небеса и землю.",
                "osmanov": "Хвала Аллаху, который создал небеса и землю."
            }
        },
        {
            "id": 7,
            "name_arabic": "الأعراف",
            "name_transliteration": "Al-A'raf",
            "name_translation": "Ограды",
            "verse_count": 206,
            "revelation_type": "Meccan",
            "arabic_text": "المص كِتَابٌ أُنْزِلَ إِلَيْكَ فَلَا يَكُنْ فِي صَدْرِكَ حَرَجٌ مِنْهُ",
            "translations": {
                "kuliev": "Алиф. Лам. Мим. Сад. Это Писание ниспослано тебе, и пусть твое сердце не испытывает стеснения от него.",
                "osmanov": "Алиф, лам, мим, сад. Книга ниспослана тебе, - пусть же не будет в твоей груди стеснения от нее."
            }
        },
        {
            "id": 8,
            "name_arabic": "الأنفال",
            "name_transliteration": "Al-Anfal",
            "name_translation": "Трофеи",
            "verse_count": 75,
            "revelation_type": "Medinan",
            "arabic_text": "يَسْأَلُونَكَ عَنِ الْأَنْفَالِ قُلِ الْأَنْفَالُ لِلَّهِ وَالرَّسُولِ",
            "translations": {
                "kuliev": "Они спрашивают тебя о трофеях. Скажи: «Трофеи принадлежат Аллаху и Посланнику».",
                "osmanov": "Они спрашивают тебя о трофеях. Скажи: «Трофеи принадлежат Аллаху и посланнику»."
            }
        },
        {
            "id": 9,
            "name_arabic": "التوبة",
            "name_transliteration": "At-Tawbah",
            "name_translation": "Покаяние",
            "verse_count": 129,
            "revelation_type": "Medinan",
            "arabic_text": "بَرَاءَةٌ مِنَ اللَّهِ وَرَسُولِهِ إِلَى الَّذِينَ عَاهَدْتُمْ مِنَ الْمُشْرِكِينَ",
            "translations": {
                "kuliev": "Отречение Аллаха и Его Посланника к тем многобожникам, с которыми вы заключили союз.",
                "osmanov": "Освобождение от Аллаха и Его посланника к тем многобожникам, с которыми вы заключили союз."
            }
        },
        {
            "id": 10,
            "name_arabic": "يونس",
            "name_transliteration": "Yunus",
            "name_translation": "Юнус",
            "verse_count": 109,
            "revelation_type": "Meccan",
            "arabic_text": "الر ۚ تِلْكَ آيَاتُ الْكِتَابِ الْحَكِيمِ",
            "translations": {
                "kuliev": "Алиф. Лам. Ра. Это - аяты мудрого Писания.",
                "osmanov": "Алиф, лам, ра. Это - знамения книги мудрой."
            }
        },
        # Последние 10 сур (105-114)
        {
            "id": 105,
            "name_arabic": "الفيل",
            "name_transliteration": "Al-Fil",
            "name_translation": "Слон",
            "verse_count": 5,
            "revelation_type": "Meccan",
            "arabic_text": "أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ",
            "translations": {
                "kuliev": "Разве ты не видел, как поступил твой Господь с владельцами слона?",
                "osmanov": "Разве ты не знаешь, как поступил Господь твой с владельцами слона?"
            }
        },
        {
            "id": 106,
            "name_arabic": "قريش",
            "name_transliteration": "Quraysh",
            "name_translation": "Курайшиты",
            "verse_count": 4,
            "revelation_type": "Meccan",
            "arabic_text": "لِإِيلَافِ قُرَيْشٍ",
            "translations": {
                "kuliev": "Ради единения курайшитов.",
                "osmanov": "За союз курайшитов."
            }
        },
        {
            "id": 107,
            "name_arabic": "الماعون",
            "name_transliteration": "Al-Ma'un",
            "name_translation": "Подаяние",
            "verse_count": 7,
            "revelation_type": "Meccan",
            "arabic_text": "أَرَأَيْتَ الَّذِي يُكَذِّبُ بِالدِّينِ",
            "translations": {
                "kuliev": "Видел ли ты того, кто считает ложью воздаяние?",
                "osmanov": "Видел ли ты того, кто ложью считает религию?"
            }
        },
        {
            "id": 108,
            "name_arabic": "الكوثر",
            "name_transliteration": "Al-Kawthar",
            "name_translation": "Изобилие",
            "verse_count": 3,
            "revelation_type": "Meccan",
            "arabic_text": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
            "translations": {
                "kuliev": "Воистину, Мы даровали тебе изобилие.",
                "osmanov": "Мы даровали тебе аль-Каусар."
            }
        },
        {
            "id": 109,
            "name_arabic": "الكافرون",
            "name_transliteration": "Al-Kafirun",
            "name_translation": "Неверующие",
            "verse_count": 6,
            "revelation_type": "Meccan",
            "arabic_text": "قُلْ يَا أَيُّهَا الْكَافِرُونَ",
            "translations": {
                "kuliev": "Скажи: «О неверующие!»",
                "osmanov": "Скажи: «О вы, неверные!»"
            }
        },
        {
            "id": 110,
            "name_arabic": "النصر",
            "name_transliteration": "An-Nasr",
            "name_translation": "Помощь",
            "verse_count": 3,
            "revelation_type": "Medinan",
            "arabic_text": "إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ",
            "translations": {
                "kuliev": "Когда придет помощь Аллаха и настанет победа.",
                "osmanov": "Когда придет помощь Аллаха и победа."
            }
        },
        {
            "id": 111,
            "name_arabic": "المسد",
            "name_transliteration": "Al-Masad",
            "name_translation": "Пальмовые волокна",
            "verse_count": 5,
            "revelation_type": "Meccan",
            "arabic_text": "تَبَّتْ يَدَا أَبِي لَهَبٍ وَتَبَّ",
            "translations": {
                "kuliev": "Да пропадут руки Абу Лахаба, и сам он пропал!",
                "osmanov": "Да пропадут руки Абу Лахаба, и сам он пропал!"
            }
        },
        {
            "id": 112,
            "name_arabic": "الإخلاص",
            "name_transliteration": "Al-Ikhlas",
            "name_translation": "Очищение веры",
            "verse_count": 4,
            "revelation_type": "Meccan",
            "arabic_text": "قُلْ هُوَ اللَّهُ أَحَدٌ",
            "translations": {
                "kuliev": "Скажи: «Он - Аллах Единый».",
                "osmanov": "Скажи: «Он - Аллах, единый»."
            }
        },
        {
            "id": 113,
            "name_arabic": "الفلق",
            "name_transliteration": "Al-Falaq",
            "name_translation": "Рассвет",
            "verse_count": 5,
            "revelation_type": "Meccan",
            "arabic_text": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
            "translations": {
                "kuliev": "Скажи: «Прибегаю к защите Господа рассвета».",
                "osmanov": "Скажи: «Прибегаю к Господу рассвета»."
            }
        },
        {
            "id": 114,
            "name_arabic": "الناس",
            "name_transliteration": "An-Nas",
            "name_translation": "Люди",
            "verse_count": 6,
            "revelation_type": "Meccan",
            "arabic_text": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ مَلِكِ النَّاسِ إِلَٰهِ النَّاسِ",
            "translations": {
                "kuliev": "Скажи: «Прибегаю к защите Господа людей, Царя людей, Бога людей»",
                "osmanov": "Скажи: «Прибегаю к Господу людей, царю людей, Богу людей»"
            }
        }
    ],
    "translators": [
        {"id": "kuliev", "name": "Эльмир Кулиев"},
        {"id": "osmanov", "name": "Магомед-Нури Османов"}
    ]
}


def get_surah_by_id(surah_id: int) -> dict | None:
    """Получить суру по ID"""
    for surah in QURAN_DATA["surahs"]:
        if surah["id"] == surah_id:
            return surah
    return None


def get_surahs_page(page: int, items_per_page: int = 8) -> list[dict]:
    """Получить страницу сур для пагинации"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    return QURAN_DATA["surahs"][start_idx:end_idx]


def get_total_pages(items_per_page: int = 8) -> int:
    """Получить общее количество страниц"""
    total = len(QURAN_DATA["surahs"])
    return (total + items_per_page - 1) // items_per_page


def get_surah_ids() -> list[int]:
    """Получить список всех ID сур"""
    return [surah["id"] for surah in QURAN_DATA["surahs"]]


def get_next_surah_id(current_id: int) -> int | None:
    """Получить ID следующей суры"""
    ids = get_surah_ids()
    try:
        idx = ids.index(current_id)
        if idx + 1 < len(ids):
            return ids[idx + 1]
        return None
    except ValueError:
        return None


def get_prev_surah_id(current_id: int) -> int | None:
    """Получить ID предыдущей суры"""
    ids = get_surah_ids()
    try:
        idx = ids.index(current_id)
        if idx - 1 >= 0:
            return ids[idx - 1]
        return None
    except ValueError:
        return None
