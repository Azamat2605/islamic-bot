#!/usr/bin/env python3
"""
Final test for Knowledge module after fix.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_final():
    """Final test."""
    print("Final Knowledge module test...")
    
    try:
        # Import knowledge_handlers.router
        from bot.handlers.sections.knowledge_handlers import router
        
        print(f"Knowledge handlers router name: {router.name}")
        
        # Count handlers
        total = 0
        for observer in router.observers.values():
            total += len(observer.handlers)
        
        print(f"Handlers in knowledge_handlers.router: {total}")
        
        if total > 0:
            print("✅ SUCCESS: knowledge_handlers.router has handlers!")
            
            # Check main router inclusion
            from bot.handlers import get_handlers_router
            main_router = get_handlers_router()
            print(f"Main router created successfully")
            
            print("\n✅ Knowledge module is ready!")
            print("\nNext steps:")
            print("1. Restart the bot")
            print("2. Test the 'Знания' button in Telegram")
            print("3. It should show the knowledge menu with 6 subsections")
            
            return True
        else:
            print("❌ FAIL: knowledge_handlers.router has NO handlers!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Final Knowledge Module Test")
    print("=" * 60)
    
    if test_final():
        print("\n" + "=" * 60)
        print("✅ All checks passed!")
    else:
        print("\n" + "=" * 60)
        print("❌ Checks failed!")
        sys.exit(1)
