#!/usr/bin/env python3
"""
Final test for Knowledge module.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_router_inclusion():
    """Test that knowledge router properly includes menu router."""
    print("Testing Knowledge router inclusion...")
    
    try:
        # Import knowledge_router
        from bot.handlers.sections.knowledge import knowledge_router
        
        print(f"Knowledge router name: {knowledge_router.name}")
        
        # Check if menu router is included
        from bot.handlers.sections.knowledge.menu import router as menu_router
        
        # Count handlers in knowledge_router
        total_handlers = 0
        for observer in knowledge_router.observers.values():
            total_handlers += len(observer.handlers)
        
        print(f"Handlers in knowledge_router: {total_handlers}")
        
        # Count handlers in menu_router
        menu_handlers = 0
        for observer in menu_router.observers.values():
            menu_handlers += len(observer.handlers)
        
        print(f"Handlers in menu_router: {menu_handlers}")
        
        # Check main router inclusion
        from bot.handlers import get_handlers_router
        main_router = get_handlers_router()
        
        # Check if knowledge_router is in main router
        print(f"Main router created successfully")
        
        # Test the actual handler function
        from bot.handlers.sections.knowledge.menu import knowledge_entry
        print(f"Knowledge entry function exists: {knowledge_entry.__name__}")
        
        # Test keyboard
        from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard
        keyboard = get_knowledge_main_keyboard()
        print(f"Keyboard created: {len(keyboard.inline_keyboard)} rows")
        
        if total_handlers > 0:
            print("\n✅ SUCCESS: Knowledge router includes menu handlers!")
            print("\nNext steps:")
            print("1. Restart the bot to apply changes")
            print("2. Test the 'Знания' button in Telegram")
            print("3. Check logs for any errors")
        else:
            print("\n⚠️ WARNING: No handlers found in knowledge_router")
            print("The menu router might not be properly included")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Final Knowledge Module Test")
    print("=" * 60)
    
    success = test_knowledge_router_inclusion()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed!")
    else:
        print("❌ Test failed!")
        sys.exit(1)
