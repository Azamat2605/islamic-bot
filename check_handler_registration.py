#!/usr/bin/env python3
"""
Check if knowledge handler is registered.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_handler():
    """Check handler registration."""
    print("Checking handler registration...")
    
    try:
        # Import the main router
        from bot.handlers import get_handlers_router
        main_router = get_handlers_router()
        
        # Count total handlers
        total = 0
        for observer in main_router.observers.values():
            total += len(observer.handlers)
        
        print(f"Total handlers in main router: {total}")
        
        # Check if knowledge router is included
        from bot.handlers.sections import knowledge_router
        print(f"Knowledge router name: {knowledge_router.name}")
        
        # Check handlers in knowledge router
        knowledge_handlers = 0
        for observer in knowledge_router.observers.values():
            knowledge_handlers += len(observer.handlers)
        
        print(f"Handlers in knowledge router: {knowledge_handlers}")
        
        # Check specific handler
        from bot.handlers.sections.knowledge.menu import router as menu_router
        menu_handlers = 0
        for observer in menu_router.observers.values():
            menu_handlers += len(observer.handlers)
        
        print(f"Handlers in knowledge.menu router: {menu_handlers}")
        
        # List message handlers
        if 'message' in menu_router.observers:
            msg_handlers = menu_router.observers['message'].handlers
            print(f"Message handlers in knowledge.menu: {len(msg_handlers)}")
            for i, handler in enumerate(msg_handlers):
                print(f"  Handler {i}: {handler}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if check_handler():
        print("\n✅ Handler check passed!")
    else:
        print("\n❌ Handler check failed!")
        sys.exit(1)
