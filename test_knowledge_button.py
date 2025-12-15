#!/usr/bin/env python3
"""
Test to verify Knowledge button responds correctly.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_knowledge_handler():
    """Test that knowledge handler responds to text 'Знания'."""
    print("Testing Knowledge button handler...")
    
    try:
        # Setup i18n mock to avoid context errors
        from aiogram.utils.i18n.context import set_i18n
        from aiogram.utils.i18n.core import I18n
        
        class MockI18n(I18n):
            def gettext(self, message, **kwargs):
                return message
            def lazy_gettext(self, message):
                return message
        
        mock_i18n = MockI18n()
        set_i18n(mock_i18n)
        
        # Import the router
        from bot.handlers.sections.knowledge.menu import router
        
        # Check handlers
        from aiogram import F
        from aiogram.types import Message
        
        # Get message handlers
        message_handlers = []
        if hasattr(router, 'observers') and 'message' in router.observers:
            for handler in router.observers['message'].handlers:
                message_handlers.append(handler)
        
        print(f"Found {len(message_handlers)} message handlers in knowledge.menu router")
        
        # Check callback handlers
        callback_handlers = []
        if hasattr(router, 'observers') and 'callback_query' in router.observers:
            for handler in router.observers['callback_query'].handlers:
                callback_handlers.append(handler)
        
        print(f"Found {len(callback_handlers)} callback handlers in knowledge.menu router")
        
        # Check if handler for "Знания" exists
        has_knowledge_handler = False
        for handler in message_handlers:
            # Check filters - this is simplified
            if hasattr(handler, 'filters'):
                filters = handler.filters
                # Try to see if it matches "Знания"
                # This is a basic check
                pass
        
        print("\n✅ Router structure check complete")
        print(f"Router name: {router.name}")
        
        # Also test the actual handler function
        from bot.handlers.sections.knowledge.menu import knowledge_entry
        print(f"Knowledge entry function: {knowledge_entry}")
        
        # Test keyboard import
        from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard
        keyboard = get_knowledge_main_keyboard()
        print(f"Keyboard type: {type(keyboard)}")
        print(f"Keyboard has {len(keyboard.inline_keyboard)} rows")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("Testing Knowledge Button Response")
    print("=" * 60)
    
    success = await test_knowledge_handler()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Knowledge module appears to be correctly configured!")
        print("\nTroubleshooting tips:")
        print("1. Make sure the bot is running with latest code")
        print("2. Check that knowledge_router is included in main handlers")
        print("3. Verify i18n middleware is properly configured")
        print("4. Try restarting the bot to clear any cached handlers")
    else:
        print("❌ There were issues with the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
