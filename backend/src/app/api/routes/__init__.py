from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.widget_auth import router as widget_auth_router
from app.api.routes.widget_assistant import router as widget_assistant_router
from app.api.routes.widget_messages import router as widget_messages_router
from app.api.routes.widget_session import router as widget_session_router

routers = [
    health_router,
    metrics_router,
    widget_session_router,
    widget_auth_router,
    widget_messages_router,
    widget_assistant_router,
]
