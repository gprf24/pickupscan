# app/main.py
"""
FastAPI application factory and setup:
- static files
- sessions
- routers
- DB table creation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

from app.api import admin_auth, admin_views, public
from app.core.config import get_settings
from app.core.deps import engine

settings = get_settings()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(title=settings.app_name)

    # Serve static files (CSS, JS, images) from /static.
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Session middleware for admin login.
    # Uses the secret key to sign session cookies.
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

    # Basic CORS configuration (relaxed for MVP / internal use).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: restrict in production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach routers
    app.include_router(public.router)
    app.include_router(admin_auth.router)
    app.include_router(admin_views.router)

    # Create database tables on startup (simple MVP solution).
    # In production you would use Alembic migrations instead.
    @app.on_event("startup")
    def on_startup() -> None:
        SQLModel.metadata.create_all(engine)

    return app


# Uvicorn entrypoint: "app.main:app"
app = create_app()
