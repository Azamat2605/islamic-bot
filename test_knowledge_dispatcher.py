#!/usr/bin/env python3
"""
Test knowledge dispatcher integration.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_dispatcher():
    """Test dispatcher integration."""
    print("Testing dispatcher integration...")
    
    try:
        from aiogram import Dispatcher
        from aiogram.types import Message, User, Chat
        from datetime import datetime
        
        # Import main router
        from bot.handlers import get_handlers_router
        main_router = get_handlers_router()
        
        # Create dispatcher
        dp = Dispatcher()
        dp.include_router(main_router)
        
        print(f"Dispatcher created with main router")
        
        # Check if knowledge router is included
        from bot.handlers.sections import knowledge_router
        print(f"Knowledge router name: {knowledge_router.name}")
        
        # Create mock message
        user = User(id=12345, is_bot=False, first_name="Test", last_name="User")
        chat = Chat(id=12345, type="private")
        message = Message(
            message_id=1,
            date=datetime.now(),
            chat=chat,
            from_user=user,
            text="Знания"
        )
        
        # Try to get handler for this message
        from aiogram.dispatcher.event.handler import HandlerObject
        from aiogram.filters import Command
        
        # Check handlers in dispatcher
        handlers = dp.message.handlers
        print(f"Total message handlers in dispatcher: {len(handlers)}")
        
        # Check knowledge handlers specifically
        from bot.handlers.sections.knowledge.menu import router as menu_router
        menu_handlers = 0
        if 'message' in menu_router.observers:
            menu_handlers = len(menu_router.observers['message'].handlers)
        
        print(f"Message handlers in menu_router: {menu_handlers}")
        
        if menu_handlers > 0:
            print("✅ Knowledge handlers are registered!")
            print("\nThe bot should work after restart.")
            print("\nNext steps:")
            print("1. Stop any running bot instance")
            print("2. Restart the bot: python -m bot")
            print("3. Test the 'Знания' button in Telegram")
            return True
        else:
            print("❌ No message handlers in menu_router!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("Knowledge Dispatcher Integration Test")
    print("=" * 60)
    
    success = await test_dispatcher()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All checks passed!")
    else:
        print("❌ Checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
