# app/api/admin_auth.py
"""
Admin authentication:
- /admin/login (GET + POST)
- /admin/logout
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.core.deps import get_session
from app.core.security import verify_password
from app.db.models import User

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/login")
def admin_login_form(request: Request):
    """
    Render the admin login form.
    """
    return templates.TemplateResponse(
        "admin_login.html", {"request": request, "error": None}
    )


@router.post("/admin/login")
def admin_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """
    Handle login POST from the admin login form.

    Steps:
    1. Look up user by login.
    2. Verify password.
    3. Check that user is_superuser.
    4. Store user_id in the session.
    """
    stmt = select(User).where(User.login == login)
    user = session.exec(stmt).first()

    if (
        not user
        or not verify_password(password, user.password_hash)
        or not user.is_superuser
    ):
        # Generic error message to avoid leaking which part failed.
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )

    # Store user id in session cookie (signed by SessionMiddleware).
    request.session["user_id"] = user.id

    # Redirect to /admin (which will redirect further to /admin/scans)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/logout")
def admin_logout(request: Request):
    """
    Clear the session and redirect back to login.
    """
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)
