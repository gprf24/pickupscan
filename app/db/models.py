# app/db/models.py
"""
Database models for the pickupscan application.
Includes:
- Admin users
- Regions
- Pharmacies
- Scan events (every QR scan)
"""

import secrets
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

# ---------------------------------------------------------------------------
# Generate secure random public IDs
# ---------------------------------------------------------------------------


def generate_public_id() -> str:
    """
    Generate a short, URL-safe public identifier.
    Used for pharmacy.public_id and region.public_id.
    Example output: "cfc2J4gkTqE"

    These IDs are intended to be:
    - non-human-readable
    - not reversible back to internal names
    - safe to embed in QR codes
    """
    return secrets.token_urlsafe(8)


# ---------------------------------------------------------------------------
# USER (Admin)
# ---------------------------------------------------------------------------


class UserBase(SQLModel):
    """
    Shared fields for the User model.
    """

    login: str = Field(index=True)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    """
    Admin user stored in the database.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str


# ---------------------------------------------------------------------------
# REGION
# ---------------------------------------------------------------------------


class RegionBase(SQLModel):
    """
    Business region (e.g., "NRW West").
    Stores both:
    - a human-readable code ("NW1", "Berlin")
    - a public_id for use in QR codes (random, opaque)
    """

    name: str
    code: str  # human readable internal code
    public_id: str = Field(
        default_factory=generate_public_id,
        index=True,
        description="Opaque public region code used in QR payloads",
    )
    is_active: bool = True


class Region(RegionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pharmacies: list["Pharmacy"] = Relationship(back_populates="region")


# ---------------------------------------------------------------------------
# PHARMACY
# ---------------------------------------------------------------------------


class PharmacyBase(SQLModel):
    """
    Pharmacy entity.
    public_id is auto-generated and used in QR codes.
    """

    name: str
    address: Optional[str] = None
    public_id: str = Field(
        default_factory=generate_public_id,
        index=True,
        description="Opaque public pharmacy code for QR payload",
    )
    is_active: bool = True


class Pharmacy(PharmacyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    region_id: Optional[int] = Field(default=None, foreign_key="region.id")

    # Relations
    region: Optional[Region] = Relationship(back_populates="pharmacies")
    scan_events: list["ScanEvent"] = Relationship(back_populates="pharmacy")


# ---------------------------------------------------------------------------
# SCAN EVENT
# ---------------------------------------------------------------------------


class ScanEventBase(SQLModel):
    """
    Data submitted from a QR scan.
    These come from the phone of the courier.
    """

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw_qr: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class ScanEvent(ScanEventBase, table=True):
    """
    Saved QR scan event.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    scanned_at: datetime = Field(default_factory=datetime.utcnow)

    pharmacy_id: int = Field(foreign_key="pharmacy.id")
    region_id: Optional[int] = Field(default=None, foreign_key="region.id")

    # Relations to fetch full objects
    pharmacy: Pharmacy = Relationship(back_populates="scan_events")
    region: Optional[Region] = Relationship()
