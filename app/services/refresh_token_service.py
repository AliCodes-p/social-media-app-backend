from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from app.core.cookies import base_cookie_params
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.token_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token_for_user,
    generate_tokens,
    verify_token,
)

# user log in onother device so revoke previous token 
def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked.is_(False),
    ).update({"is_revoked": True}, synchronize_session=False)

# used while log out 

def revoke_refresh_token(db: Session, token_value: str) -> None:
    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token_value,
            RefreshToken.is_revoked.is_(False),
        )
        .first()
    )

    if stored_token:
        stored_token.is_revoked = True

 #used to  check whether a refresh token is still valid before using it to create a new access token
def get_valid_refresh_token(
    db: Session,
    token_value: str,
    user_id: int,
) -> RefreshToken:
    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token_value,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        )
        .first()
    )

    if not stored_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    if stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    return stored_token


def parse_token_user_id(payload: dict) -> int:
    sub = payload.get("sub")

    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        return int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

 # used to check is token valid then return the user 
def validate_refresh_token_cookie(
    db: Session,
    token_value: str,
) -> tuple[RefreshToken, User]:
    payload = verify_token(token_value, expected_type="refresh")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = parse_token_user_id(payload)
    stored_token = get_valid_refresh_token(db, token_value, user_id)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return stored_token, user


def set_access_token_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        **base_cookie_params(max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )


def set_auth_cookies(response: Response, tokens: dict) -> None:
    set_access_token_cookie(response, tokens["access_token"])

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        **base_cookie_params(max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
    )


def clear_auth_cookies(response: Response) -> None:
    cookie_params = base_cookie_params()
    response.delete_cookie(key="access_token", **cookie_params)
    response.delete_cookie(key="refresh_token", **cookie_params)


def issue_auth_tokens(response: Response, db: Session, user: User) -> None:
    revoke_all_user_refresh_tokens(db, user.id)

    tokens = generate_tokens(user)

    db.add(
        RefreshToken(
            user_id=user.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    db.commit()
    set_auth_cookies(response, tokens)
