#!/usr/bin/env python3
"""
Debug keyboard creation.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_keyboard():
    """Test keyboard creation."""
    print("Testing knowledge keyboard creation...")
    
    try:
        # Mock i18n to avoid context errors
        import aiogram.utils.i18n.context
        
        class MockI18n:
            def gettext(self, message, **kwargs):
                return message
        
        # Patch the i18n context
        import aiogram.utils.i18n.context as i18n_context
        original_get_i18n = i18n_context.get_i18n
        
        def mock_get_i18n():
            return MockI18n()
        
        i18n_context.get_i18n = mock_get_i18n
        
        # Now import and test
        from bot.keyboards.inline.knowledge.main_kb import get_knowledge_main_keyboard
        
        keyboard = get_knowledge_main_keyboard()
        print(f"✅ Keyboard created: {type(keyboard)}")
        print(f"✅ Inline keyboard rows: {len(keyboard.inline_keyboard)}")
        
        for i, row in enumerate(keyboard.inline_keyboard):
            print(f"  Row {i}: {len(row)} buttons")
            for j, button in enumerate(row):
                print(f"    Button {j}: text='{button.text}', callback='{button.callback_data}'")
        
        # Restore original
        i18n_context.get_i18n = original_get_i18n
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_keyboard():
        print("\n✅ Keyboard test passed!")
    else:
        print("\n❌ Keyboard test failed!")
        sys.exit(1)
