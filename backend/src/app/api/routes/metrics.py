from fastapi import APIRouter, Response

from app.core.metrics import metrics

router = APIRouter()


@router.get("/metrics")
def get_metrics() -> Response:
    payload = metrics.render_prometheus()
    return Response(content=payload, media_type="text/plain; version=0.0.4")
