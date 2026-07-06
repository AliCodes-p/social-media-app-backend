import profile

from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import random
from app.models.profile import Profile

from app.models.user import User
from app.models.otp_verification import OTPVerification


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------------
# AUTHENTICATE USER
# -------------------------
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not user.is_verified:
        return None

    # OAuth-only user check
    if user.hashed_password is None:
        return None

    if not verify_password(password, user.hashed_password):
       return None

    return user


def validate_login_credentials(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None, "invalid_credentials"

    # OAuth-only account
    if user.hashed_password is None:
        return user, "oauth_user"

    if not verify_password(password, user.hashed_password):
        return None, "invalid_credentials"

    if not user.is_verified:
        return None, "unverified"

    return user, None


def create_otp(db: Session, user_id: int, purpose: str) -> OTPVerification:
    otp_entry = OTPVerification(
        user_id=user_id,
        otp_code=generate_otp(),
        purpose=purpose,
        expires_at=get_otp_expiry(),
        is_used=False,
    )
    db.add(otp_entry)
    db.commit()
    db.refresh(otp_entry)
    return otp_entry


# -------------------------
# PASSWORD HASHING
# -------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------
# OTP GENERATION
# -------------------------
def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def get_otp_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=5)


# -------------------------
# REGISTER USER (FIXED - OTP TABLE VERSION)
# -------------------------
def register_user(db: Session, username: str, email: str, password: str):

    existing_user = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # 1. Create user
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    profile = Profile(
    user_id=user.id
    )

    db.add(profile)
    db.commit()

    # 2. Create OTP in separate table
    otp = generate_otp()
    expiry = get_otp_expiry()

    otp_entry = OTPVerification(
        user_id=user.id,
        otp_code=otp,
        purpose="register",
        expires_at=expiry,
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    return user