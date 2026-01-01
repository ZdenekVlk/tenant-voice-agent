from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import routers
from app.middleware.payload_limit import PayloadLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PayloadLimitMiddleware)

    for router in routers:
        app.include_router(router)

    return app


app = create_app()
