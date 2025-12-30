from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import routers


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    for router in routers:
        app.include_router(router)

    return app


app = create_app()
