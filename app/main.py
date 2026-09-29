import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, settings
from app.routes import router


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered comic story creator using "
        "Gemini and image generation."
    ),
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)


app.include_router(router)