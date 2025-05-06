from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.choices import Environment
from src.settings.general import general_settings
from src.utils.exceptions import http_exception_handler

root_router = APIRouter()


@root_router.get(
    "/",
    summary="Application info",
)
def root() -> dict[str, Any]:
    return {
        "message": "Welcome to the Quiz API!",
        "app": general_settings.app_name,
        "version": general_settings.version,
        "docs_url": "/docs",
    }


@root_router.get(
    "/healthz",
    summary="K8S liveness probe",
)
def healthz() -> dict[str, Any]:
    return {
        "status": "ok",
    }


@root_router.get(
    "/readyz",
    summary="K8S readiness probe",
)
def readyz() -> dict[str, Any]:
    return {
        "status": "ok",
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title=general_settings.app_name,
        summary=general_settings.app_description,
        debug=(general_settings.environment == Environment.DEV),
        version=general_settings.version,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    app.add_exception_handler(
        HTTPException,
        http_exception_handler
    )  # type: ignore[arg-type]

    # Include routers
    app.include_router(root_router)
    app.include_router(api_router)

    return app
