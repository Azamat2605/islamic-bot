"""
Knowledge module routers.
"""
from aiogram import Router

# Create main router for knowledge module
knowledge_router = Router(name="knowledge")

# Import routers after creating knowledge_router to avoid circular imports
from .quran import quran_router
from .menu import router as menu_router
from .hadith import catalog_router as hadith_router

# Import books router
from bot.handlers.sections.books import books_router

# Import streams router
from bot.handlers.sections.streams import router as streams_router

# Import new hadiths router (topic-based)
from bot.handlers.sections.hadiths import router as hadiths_router

# Import articles router
from bot.handlers.sections.articles import router as articles_router

# Include routers in correct order: specific routers FIRST, then menu_router
# This ensures specific callbacks are handled before menu_router
knowledge_router.include_router(quran_router)
knowledge_router.include_router(hadith_router)
knowledge_router.include_router(hadiths_router)  # New topic-based hadiths
knowledge_router.include_router(books_router)
knowledge_router.include_router(streams_router)
knowledge_router.include_router(articles_router)  # New articles module
knowledge_router.include_router(menu_router)

# Note: Handlers are registered via decorators in their respective modules
