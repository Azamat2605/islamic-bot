#!/usr/bin/env python3
"""
Simple test to verify Knowledge module files exist and can be imported.
"""
import os
import sys

def check_files():
    """Check that all required files exist."""
    print("Checking Knowledge module files...")
    
    files = [
        ("bot/handlers/sections/knowledge/__init__.py", True),
        ("bot/handlers/sections/knowledge/menu.py", True),
        ("bot/keyboards/inline/knowledge/__init__.py", True),
        ("bot/keyboards/inline/knowledge/main_kb.py", True),
        ("bot/handlers/sections/knowledge_handlers.py", True),
    ]
    
    all_exist = True
    for file_path, required in files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            if required:
                all_exist = False
    
    return all_exist

def check_imports():
    """Check that modules can be imported."""
    print("\nChecking imports...")
    
    try:
        # Try to import knowledge_handlers
        from bot.handlers.sections.knowledge_handlers import router
        print("✓ knowledge_handlers imported")
        
        # Try to import knowledge router from submodule
        from bot.handlers.sections.knowledge import knowledge_router
        print(f"✓ knowledge_router imported (name: {knowledge_router.name})")
        
        # Try to import menu router
        from bot.handlers.sections.knowledge.menu import router as menu_router
        print(f"✓ knowledge.menu.router imported (name: {menu_router.name})")
        
        # Check handler count
        import inspect
        from bot.handlers.sections.knowledge.menu import knowledge_entry
        print(f"✓ knowledge_entry function: {inspect.isfunction(knowledge_entry)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    print("=" * 60)
    print("Knowledge Module File Check")
    print("=" * 60)
    
    files_ok = check_files()
    imports_ok = check_imports()
    
    print("\n" + "=" * 60)
    if files_ok and imports_ok:
        print("✅ All files exist and imports work!")
        print("\nIf the bot is not responding to 'Знания' button:")
        print("1. Make sure the bot has been restarted after changes")
        print("2. Check that knowledge_router is included in get_handlers_router()")
        print("3. Verify the Reply Keyboard shows 'Знания' (not '📖 Знания')")
        print("4. The handler matches both 'Знания' and localized version")
    else:
        print("❌ Some checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
