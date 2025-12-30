from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies.widget_auth import WidgetSessionContext, require_widget_session

router = APIRouter()


@router.get("/widget/whoami")
def widget_whoami(session: WidgetSessionContext = Depends(require_widget_session)) -> dict:
    return {
        "tenant_id": str(session.tenant_id),
        "conversation_id": str(session.conversation_id),
    }
