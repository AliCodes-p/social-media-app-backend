from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# -------------------------
# ACCESS TOKEN
# -------------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------
# REFRESH TOKEN
# -------------------------
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------
# PASSWORD RESET TOKEN
# -------------------------
RESET_TOKEN_EXPIRE_MINUTES = 15

def create_reset_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
        "type": "reset"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_reset_token_for_user(user) -> str:
    return create_reset_token({"sub": str(user.id)})


# -------------------------
# VERIFY TOKEN
# -------------------------
def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != expected_type:
            return None

        return payload

    except JWTError:
        return None


# -------------------------
# GENERATE TOKENS
# -------------------------
def create_access_token_for_user(user) -> str:
    return create_access_token({"sub": str(user.id)})


def create_refresh_token_for_user(user) -> str:
    return create_refresh_token({"sub": str(user.id)})


def generate_tokens(user):
    return {
        "access_token": create_access_token_for_user(user),
        "refresh_token": create_refresh_token_for_user(user),
    }