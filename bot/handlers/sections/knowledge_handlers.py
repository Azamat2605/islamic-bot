"""
Knowledge module handlers.
This file serves as the main entry point for the Knowledge module.
It imports and includes routers from the knowledge submodule.
"""
from aiogram import Router

# Import the knowledge router from the knowledge submodule
from .knowledge import knowledge_router

# Create main router for knowledge module
router = Router(name="knowledge")

# Include the knowledge submodule router
router.include_router(knowledge_router)
