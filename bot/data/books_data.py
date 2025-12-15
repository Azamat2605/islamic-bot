"""
Мок-данные для модуля Книги.
Для MVP используем hardcoded данные по требованиям.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class BookCategory(str, Enum):
    """Категории книг"""
    AQIDAH = "aqidah"      # Акыда
    FIQH = "fiqh"          # Фикх
    TASAWWUF = "tasawwuf"  # Тасаввуф
    HISTORY = "history"    # История
    BIOGRAPHY = "biography" # Биографии


@dataclass
class Book:
    """Модель книги"""
    id: str  # Строковый ID, например "book_1"
    category: BookCategory
    title: str
    author: str
    description: str
    cover_url: str  # URL обложки
    page_images: List[str]  # Список URL изображений страниц
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.page_images:
            raise ValueError("Книга должна содержать хотя бы одну страницу")
        if not self.cover_url:
            self.cover_url = self.page_images[0] if self.page_images else ""


# Hardcoded данные книг согласно требованиям
BOOKS_DATA: List[Book] = [
    # Акыда (2 книги)
    Book(
        id="book_1",
        category=BookCategory.AQIDAH,
        title="Китаб ат-Таухид",
        author="Мухаммад ибн Абд аль-Ваххаб",
        description="Фундаментальный труд по исламскому единобожию (таухиду), "
                   "разъясняющий основы вероубеждения и очищения веры от ширка.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+4",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+5",
        ]
    ),
    Book(
        id="book_2",
        category=BookCategory.AQIDAH,
        title="Акыда ат-Тахавия",
        author="Имам Абу Джафар ат-Тахави",
        description="Классический текст по вероубеждению ахлю-с-сунна валь-джамаа, "
                   "принятый всеми исламскими мазхабами как эталон правильной акыды.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
        ]
    ),
    
    # Фикх (2 книги)
    Book(
        id="book_3",
        category=BookCategory.FIQH,
        title="Мухтасар аль-Кудури",
        author="Абу-ль-Хусейн аль-Кудури (Ханафитский мазхаб)",
        description="Один из основных текстов ханафитского фикха, охватывающий "
                   "все разделы исламского права от очищения до торговли.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+4",
        ]
    ),
    Book(
        id="book_4",
        category=BookCategory.FIQH,
        title="Сады праведных (избранное)",
        author="Имам ан-Навави",
        description="Избранные хадисы из сборника 'Рийад ас-Салихин', касающиеся "
                   "фикха, нравственности и поклонения.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
        ]
    ),
    
    # Тасаввуф (1 книга)
    Book(
        id="book_5",
        category=BookCategory.TASAWWUF,
        title="Благонравие праведников (избранное)",
        author="Абу Хамид аль-Газали",
        description="Избранные главы из 'Ихья улюм ад-дин', посвященные очищению "
                   "души, искренности и духовному совершенствованию.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
        ]
    ),
    
    # История (1 книга)
    Book(
        id="book_6",
        category=BookCategory.HISTORY,
        title="Истории пророков",
        author="Ибн Касир",
        description="Подробное изложение историй пророков от Адама до Мухаммада ﷺ "
                   "на основе Корана и достоверных хадисов.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+4",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+5",
        ]
    ),
    
    # Биографии (1 книга)
    Book(
        id="book_7",
        category=BookCategory.BIOGRAPHY,
        title="Жизнь Пророка (Ar-Raheeq Al-Makhtum)",
        author="Сафи ар-Рахман аль-Мубаракфури",
        description="Полная биография Пророка Мухаммада ﷺ, удостоенная первой "
                   "премии на конкурсе биографии Пророка в 1979 году.",
        cover_url="https://placehold.co/600x800/228B22/FFFFFF?text=Book+Cover",
        page_images=[
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+1",
            "https://placehold.co/600x800/006400/FFFFFF?text=Page+2",
            "https://placehold.co/600x800/3CB371/FFFFFF?text=Page+3",
            "https://placehold.co/600x800/008000/FFFFFF?text=Page+4",
        ]
    ),
]


# Вспомогательные функции
def get_all_books() -> List[Book]:
    """Получить все книги"""
    return BOOKS_DATA


def get_book_by_id(book_id: str) -> Optional[Book]:
    """Получить книгу по ID (строковому)"""
    for book in BOOKS_DATA:
        if book.id == book_id:
            return book
    return None


def get_books_by_category(category: BookCategory) -> List[Book]:
    """Получить все книги категории"""
    return [book for book in BOOKS_DATA if book.category == category]


def get_all_categories() -> List[BookCategory]:
    """Получить все уникальные категории"""
    return list(set(book.category for book in BOOKS_DATA))


def get_category_name(category: BookCategory) -> str:
    """Получить русское название категории"""
    category_names = {
        BookCategory.AQIDAH: "Акыда",
        BookCategory.FIQH: "Фикх",
        BookCategory.TASAWWUF: "Тасаввуф",
        BookCategory.HISTORY: "История",
        BookCategory.BIOGRAPHY: "Биографии",
    }
    return category_names.get(category, category.value)


def get_category_description(category: BookCategory) -> str:
    """Получить описание категории"""
    descriptions = {
        BookCategory.AQIDAH: "Книги по исламскому вероубеждению и единобожию",
        BookCategory.FIQH: "Книги по исламскому праву и jurisprudence",
        BookCategory.TASAWWUF: "Книги по духовному очищению и нравственности",
        BookCategory.HISTORY: "Исторические труды и хроники",
        BookCategory.BIOGRAPHY: "Биографии пророков и выдающихся мусульман",
    }
    return descriptions.get(category, "")
