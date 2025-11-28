# app/core/deps.py
"""
Shared dependencies:
- database session
- current admin user
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, create_engine, select

from app.core.config import get_settings
from app.db.models import User

settings = get_settings()

# Global SQLAlchemy/SQLModel engine.
# echo=False to avoid noisy SQL logs; set True for debugging.
engine = create_engine(settings.database_url, echo=False)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.

    Usage: session: Session = Depends(get_session)
    """
    with Session(engine) as session:
        yield session


def get_current_admin(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    """
    FastAPI dependency: returns the currently logged-in admin user.

    - Reads user_id from the session cookie.
    - Loads the user from the DB.
    - Ensures the user is active and is_superuser = True.
    """
    user_id: Optional[int] = request.session.get("user_id")
    if not user_id:
        # No user in session → not authenticated.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = session.get(User, user_id)
    if not user or not user.is_active or not user.is_superuser:
        # Found user is not valid admin.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user
