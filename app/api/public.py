# app/api/public.py
"""
Public routes:
- "/" → scanner page
- "/api/scan" → receives scan data from the frontend
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.core.deps import get_session
from app.db.models import Pharmacy, Region, ScanEvent

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def show_scanner(request: Request):
    """
    Landing page:
    Shows the QR scanner immediately.
    No login required.
    """
    return templates.TemplateResponse("scan.html", {"request": request})


@router.post("/api/scan")
async def api_scan(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Receives POST data from the browser after QR detection.

    Expected JSON payload:
      {
        "pharmacy_public_id": "...",   # required, opaque token from QR
        "latitude": 53.55,
        "longitude": 10.00,
        "raw_qr": "full QR text"
      }

    The system:
    1. Finds the pharmacy via its public_id (random token, not name).
    2. Fetches the associated region.
    3. Logs the scan event.
    """
    data = await request.json()
    pharmacy_public_id = data.get("pharmacy_public_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    raw_qr = data.get("raw_qr")

    # Public ID must be present
    if not pharmacy_public_id:
        return JSONResponse(
            {"ok": False, "error": "Missing pharmacy_public_id"}, status_code=400
        )

    # Find pharmacy by its opaque public code
    stmt = select(Pharmacy).where(Pharmacy.public_id == pharmacy_public_id)
    pharmacy = session.exec(stmt).first()
    if not pharmacy:
        return JSONResponse({"ok": False, "error": "Unknown pharmacy"}, status_code=400)

    # Determine region automatically (if pharmacy is linked to one)
    region = session.get(Region, pharmacy.region_id) if pharmacy.region_id else None

    # Additional metadata
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Create and store event
    scan = ScanEvent(
        pharmacy_id=pharmacy.id,
        region_id=region.id if region else None,
        latitude=latitude,
        longitude=longitude,
        raw_qr=raw_qr,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(scan)
    session.commit()
    session.refresh(scan)

    return {"ok": True, "scan_id": scan.id}
