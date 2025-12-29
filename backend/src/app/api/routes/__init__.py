from app.api.routes.health import router as health_router
from app.api.routes.widget_session import router as widget_session_router

routers = [health_router, widget_session_router]
