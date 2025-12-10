from .admin_panel import router as admin_panel_router
from .test_prayer import router as test_prayer_router

# Для обратной совместимости
admin_panel = admin_panel_router
test_prayer = test_prayer_router

__all__ = ["admin_panel", "test_prayer", "admin_panel_router", "test_prayer_router"]
