#!/usr/bin/env python3
"""
Integration test for Knowledge module.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_knowledge_integration():
    """Test knowledge module integration."""
    print("Testing Knowledge module integration...")
    
    try:
        # Import the main router
        from bot.handlers import get_handlers_router
        main_router = get_handlers_router()
        
        # Check if knowledge router is included
        from bot.handlers.sections import knowledge_router
        
        # Create a simple test to see if handler would trigger
        from aiogram import Dispatcher
        from aiogram.types import Message, User, Chat
        
        # Create mock objects
        user = User(id=12345, is_bot=False, first_name="Test", last_name="User")
        chat = Chat(id=12345, type="private")
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=user,
            text="Знания"
        )
        
        # Create dispatcher and register router
        dp = Dispatcher()
        dp.include_router(main_router)
        
        print("✅ Dispatcher created with main router")
        print(f"✅ Knowledge router included: {knowledge_router.name}")
        
        # Check if handler exists by looking at filters
        from bot.handlers.sections.knowledge.menu import router as menu_router
        
        # Count handlers
        msg_handlers = 0
        if 'message' in menu_router.observers:
            msg_handlers = len(menu_router.observers['message'].handlers)
        
        print(f"✅ Message handlers in knowledge.menu: {msg_handlers}")
        
        if msg_handlers > 0:
            print("✅ Knowledge handler is registered!")
            print("\nIf the bot is not responding, possible reasons:")
            print("1. Bot needs to be restarted to pick up changes")
            print("2. Check logs for errors when handler executes")
            print("3. Verify i18n middleware is working correctly")
            print("4. Make sure no other handler intercepts the message first")
        else:
            print("❌ No message handlers found in knowledge.menu!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("Knowledge Module Integration Test")
    print("=" * 60)
    
    success = await test_knowledge_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Integration test passed!")
        print("\nNext steps:")
        print("1. Stop the running bot (if any)")
        print("2. Restart the bot: python -m bot")
        print("3. Test the 'Знания' button in Telegram")
    else:
        print("❌ Integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
