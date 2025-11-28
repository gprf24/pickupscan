# app/core/security.py
"""
Password hashing and verification helpers using passlib.
"""

from passlib.context import CryptContext

# Create a password hashing context.
# bcrypt is a strong, salted password hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Use this when creating or updating a user.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against a stored hash.

    Returns True if the password is correct, False otherwise.
    """
    return pwd_context.verify(password, password_hash)
