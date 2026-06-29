from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.email import send_otp_email
from app.core.oauth import handle_oauth_callback, start_oauth_flow
from app.db.dependency import get_db
from app.models.otp_verification import OTPVerification
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResendOtpRequest,
    VerifyOtpRequest,
)
from app.services.auth_dependency import get_current_user
from app.services.auth_service import (
    create_otp,
    register_user,
    validate_login_credentials,
)
from app.services.refresh_token_service import (
    clear_auth_cookies,
    issue_auth_tokens,
    revoke_refresh_token,
    set_access_token_cookie,
    validate_refresh_token_cookie,
)
from app.services.token_service import (
    create_access_token_for_user,
    create_reset_token_for_user,
    verify_token,
)
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import hash_password
from app.services.refresh_token_service import revoke_all_user_refresh_tokens

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/oauth/{provider}")
async def oauth_start(provider: str, response: Response):
    return await start_oauth_flow(provider, response)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    code: str | None = None,
    state: str | None = None,
):
    return await handle_oauth_callback(provider, code, state, request, response, db)


def get_latest_otp(db: Session, user_id: int, purpose: str) -> OTPVerification | None:
    return (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
        )
        .order_by(OTPVerification.id.desc())
        .first()
    )


def validate_otp_entry(otp_entry: OTPVerification | None, otp: str) -> None:
    if not otp_entry:
        raise HTTPException(status_code=404, detail="OTP not found")

    if otp_entry.is_used:
        raise HTTPException(status_code=400, detail="OTP already used")

    if otp_entry.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")


# -------------------------
# REGISTER
# -------------------------
@router.post("/register")
async def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
):
    user = register_user(db, body.username, body.email, body.password)

    otp_entry = get_latest_otp(db, user.id, "register")

    if not otp_entry:
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to create OTP. Please try again.")

    try:
        await send_otp_email(body.email, otp_entry.otp_code)
    except Exception:
        db.delete(otp_entry)
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    return {
        "message": "User created. OTP sent to email.",
        "user_id": user.id,
    }


# -------------------------
# LOGIN (sends OTP)
# -------------------------
@router.post("/login")
async def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    user, error = validate_login_credentials(db, body.email, body.password)

    if error == "invalid_credentials":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if error == "unverified":
        raise HTTPException(status_code=403, detail="Please verify your email first")

    if user is None:
        raise HTTPException(status_code=500, detail="Unable to process login request")

    otp_entry = create_otp(db, user.id, "login")

    try:
        await send_otp_email(body.email, otp_entry.otp_code)
    except Exception:
        db.delete(otp_entry)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    return {"message": "OTP sent to your email."}


# -------------------------
# VERIFY OTP
# -------------------------
@router.post("/verify-otp")
def verify_otp(
    body: VerifyOtpRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    if body.purpose not in ("register", "login"):
        raise HTTPException(status_code=400, detail="Invalid OTP purpose")

    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.purpose == "login" and not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    otp_entry = get_latest_otp(db, user.id, body.purpose)
    validate_otp_entry(otp_entry, body.otp)

    if otp_entry is None:
        raise HTTPException(status_code=404, detail="OTP not found")

    otp_entry.is_used = True

    if body.purpose == "register":
        user.is_verified = True

    db.commit()

    issue_auth_tokens(response, db, user)

    return {"message": "Verification successful"}


# -------------------------
# RESEND OTP
# -------------------------
@router.post("/resend-otp")
async def resend_otp(
    body: ResendOtpRequest,
    db: Session = Depends(get_db),
):
    if body.purpose not in ("register", "login"):
        raise HTTPException(status_code=400, detail="Invalid OTP purpose")

    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.purpose == "register" and user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    if body.purpose == "login" and not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    otp_entry = create_otp(db, user.id, body.purpose)

    try:
        await send_otp_email(body.email, otp_entry.otp_code)
    except Exception:
        db.delete(otp_entry)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    return {"message": "OTP resent to your email."}


# -------------------------
# GET CURRENT USER
# -------------------------
@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_verified": user.is_verified,
    }


# -------------------------
# REFRESH TOKEN
# -------------------------
@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="No refresh token")

    _, user = validate_refresh_token_cookie(db, refresh_token_value)

    set_access_token_cookie(response, create_access_token_for_user(user))

    return {"message": "Token refreshed"}


# -------------------------
# LOGOUT
# -------------------------
@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token_value = request.cookies.get("refresh_token")

    if refresh_token_value:
        revoke_refresh_token(db, refresh_token_value)
        db.commit()

    clear_auth_cookies(response)

    return {"message": "Logged out successfully"}


# -------------------------
# FORGOT PASSWORD
# -------------------------
@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")

    # Create OTP for reset_password
    otp_entry = create_otp(db, user.id, "reset_password")

    try:
        await send_otp_email(body.email, otp_entry.otp_code)
    except Exception:
        db.delete(otp_entry)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    return {"message": "Reset password OTP sent to your email."}


# -------------------------
# VERIFY RESET OTP
# -------------------------
@router.post("/verify-reset-otp")
def verify_reset_otp(
    body: VerifyResetOTPRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_entry = get_latest_otp(db, user.id, "reset_password")
    validate_otp_entry(otp_entry, body.otp_code)

    if otp_entry is None:
        raise HTTPException(status_code=404, detail="OTP not found")

    otp_entry.is_used = True
    db.commit()

    # Generate a short-lived reset token (JWT)
    reset_token = create_reset_token_for_user(user)

    return {
        "message": "OTP verified successfully.",
        "reset_token": reset_token,
    }


# -------------------------
# RESET PASSWORD
# -------------------------
@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    # Verify the reset token
    payload = verify_token(body.reset_token, expected_type="reset")

    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    user.hashed_password = hash_password(body.new_password)
    
    # Revoke all active refresh tokens for the user for security
    revoke_all_user_refresh_tokens(db, user.id)

    db.commit()

    return {"message": "Password has been reset successfully"}
