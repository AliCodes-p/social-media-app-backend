from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.db.dependency import get_db

from app.services.auth_service import (
    register_user,
    authenticate_user
)

from app.services.token_service import (
    generate_tokens,
    verify_token
)

from app.models.user import User
from app.models.otp_verification import OTPVerification
from app.models.refresh_token import RefreshToken

from app.core.email import send_otp_email
from app.services.auth_dependency import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# -------------------------
# REGISTER
# -------------------------
@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    user = register_user(db, username, email, password)

    otp_entry = (
        db.query(OTPVerification)
        .filter(OTPVerification.user_id == user.id)
        .order_by(OTPVerification.id.desc())
        .first()
    )

    if not otp_entry:
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to create OTP. Please try again.")

    try:
        await send_otp_email(email, otp_entry.otp_code)

    except Exception:
        db.delete(otp_entry)
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    return {
        "message": "User created. OTP sent to email.",
        "user_id": user.id
    }


# -------------------------
# VERIFY OTP
# -------------------------
@router.post("/verify-otp")
def verify_otp(
    email: str,
    otp: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Already verified"}

    otp_entry = (
        db.query(OTPVerification)
        .filter(OTPVerification.user_id == user.id)
        .order_by(OTPVerification.id.desc())
        .first()
    )

    if not otp_entry:
        raise HTTPException(status_code=404, detail="OTP not found")

    if otp_entry.is_used:
        raise HTTPException(status_code=400, detail="OTP already used")

    if otp_entry.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    otp_entry.is_used = True
    user.is_verified = True

    db.commit()

    return {"message": "Email verified successfully"}


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
def login(
    response: Response,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    user = authenticate_user(db, email, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    tokens = generate_tokens(user)
    refresh_token = tokens["refresh_token"]

    # Store refresh token in DB
    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
    )
    db.commit()

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"message": "Login successful"}


# -------------------------
# GET CURRENT USER
# -------------------------
@router.get("/me")
def get_me(user: User = Depends(get_current_user)):

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_verified": user.is_verified
    }


# -------------------------
# REFRESH TOKEN (DB VERIFIED)
# -------------------------
@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = verify_token(refresh_token, expected_type="refresh")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 🔥 DB CHECK (IMPORTANT)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    # 🔥 EXPIRY CHECK
    if stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_tokens = generate_tokens(user)

    response.set_cookie(
        key="access_token",
        value=new_tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Token refreshed"}