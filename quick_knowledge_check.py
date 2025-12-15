#!/usr/bin/env python3
"""
Quick check for knowledge handler registration.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_check():
    """Quick check."""
    print("Quick check for Knowledge handler...")
    
    try:
        # Import knowledge_router
        from bot.handlers.sections.knowledge import knowledge_router
        
        # Count handlers
        total = 0
        for observer in knowledge_router.observers.values():
            total += len(observer.handlers)
        
        print(f"Handlers in knowledge_router: {total}")
        
        if total > 0:
            print("✅ SUCCESS: knowledge_router has handlers!")
            return True
        else:
            print("❌ FAIL: knowledge_router has NO handlers!")
            print("\nTroubleshooting:")
            print("1. Check that menu.router is properly imported")
            print("2. Check that knowledge_router.include_router(menu_router) is called")
            print("3. Check for circular imports")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if quick_check():
        print("\n✅ Knowledge module should work after bot restart!")
        print("\nNext: Restart the bot and test the 'Знания' button.")
    else:
        print("\n❌ Knowledge module needs fixing!")
        sys.exit(1)
