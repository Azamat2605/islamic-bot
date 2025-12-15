#!/usr/bin/env python3
"""
Test knowledge/__init__.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_init():
    """Test knowledge init."""
    print("Testing knowledge/__init__.py...")
    
    try:
        # Import knowledge_router
        from bot.handlers.sections.knowledge import knowledge_router
        
        print(f"Knowledge router name: {knowledge_router.name}")
        
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
            print("\nDebug info:")
            
            # Check if menu_router is imported
            from bot.handlers.sections.knowledge.menu import router as menu_router
            menu_total = 0
            for observer in menu_router.observers.values():
                menu_total += len(observer.handlers)
            print(f"Handlers in menu_router: {menu_total}")
            
            # Check if knowledge_router includes menu_router
            print(f"knowledge_router.observers keys: {list(knowledge_router.observers.keys())}")
            print(f"menu_router.observers keys: {list(menu_router.observers.keys())}")
            
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_knowledge_init():
        print("\n✅ knowledge/__init__.py works!")
    else:
        print("\n❌ knowledge/__init__.py has issues!")
        sys.exit(1)
