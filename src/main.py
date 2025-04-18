from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException

from src.choices import Environment
from src.settings.general import general_settings
from src.utils.exceptions import http_exception_handler

root_router = APIRouter()


@root_router.get(
    "/",
    summary="Application info",
)
async def root() -> dict[str, Any]:
    return {
        "app": general_settings.app_name,
        "version": general_settings.version,
    }


@root_router.get(
    "/healthz",
    summary="K8S liveness probe",
)
async def healthz() -> dict[str, Any]:
    return {
        "message": "OK",
    }


@root_router.get(
    "/readyz",
    summary="K8S readiness probe",
)
async def readyz() -> dict[str, Any]:
    return {
        "message": "OK",
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title=general_settings.app_name,
        summary=general_settings.app_description,
        debug=(general_settings.environment == Environment.DEV),
        version=general_settings.version,
    )
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]

    router = APIRouter(
        prefix="/api/v1",
    )

    app.include_router(root_router)
    app.include_router(router)

    return app
