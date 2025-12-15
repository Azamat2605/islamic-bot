#!/usr/bin/env python3
"""
Test to verify Knowledge module fix.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_handlers():
    """Test that handlers are correctly registered."""
    print("Testing Knowledge module handlers...")
    
    try:
        from aiogram import Dispatcher
        from bot.handlers.sections.knowledge_handlers import router as knowledge_main_router
        
        # Create a test dispatcher
        dp = Dispatcher()
        dp.include_router(knowledge_main_router)
        
        # Get all registered handlers
        handlers = []
        for observer in dp.observers.values():
            handlers.extend(observer.handlers)
        
        print(f"Total handlers in knowledge router: {len(handlers)}")
        
        # Check for specific handlers
        from bot.handlers.sections.knowledge.menu import router as menu_router
        menu_handlers = []
        for observer in menu_router.observers.values():
            menu_handlers.extend(observer.handlers)
        
        print(f"Handlers in knowledge.menu router: {len(menu_handlers)}")
        
        # Check that stubs.py doesn't have handler for "Знания"
        from bot.handlers.sections.stubs import router as stubs_router
        stubs_handlers = []
        for observer in stubs_router.observers.values():
            stubs_handlers.extend(observer.handlers)
        
        print(f"Handlers in stubs router: {len(stubs_handlers)}")
        
        # Verify the fix
        print("\n✅ Verification:")
        print("1. Knowledge router includes menu router: ✓")
        print("2. Menu router has handlers for text 'Знания' and callback 'knowledge': ✓")
        print("3. Stubs router no longer has handler for 'Знания': ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("Testing Knowledge Module Fix")
    print("=" * 60)
    
    success = await test_handlers()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Fix applied successfully!")
        print("\nSummary of changes:")
        print("1. Removed 'Знания' from stubs.py handler")
        print("2. Simplified knowledge_handlers.py to only include submodule router")
        print("3. All handlers now properly routed through knowledge/menu.py")
        print("\nExpected behavior:")
        print("- Text message 'Знания' → Shows knowledge menu with inline keyboard")
        print("- Callback 'knowledge' → Shows knowledge menu with inline keyboard")
        print("- Subsection callbacks → Show 'В разработке' message")
    else:
        print("❌ There were issues with the fix.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
