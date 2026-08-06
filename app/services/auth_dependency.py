from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.services.token_service import verify_token
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    print("=" * 60)
    print("PATH:", request.url.path)
    print("COOKIE HEADER:", request.headers.get("cookie"))
    print("ACCESS COOKIE:", request.cookies.get("access_token"))
    print("REFRESH COOKIE:", request.cookies.get("refresh_token"))

    token = request.cookies.get("access_token")

    if not token:
        print("NO ACCESS TOKEN")
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token, expected_type="access")

    print("PAYLOAD:", payload)

    if not payload:
        print("INVALID TOKEN")
        raise HTTPException(status_code=401, detail="Invalid token")

    
    sub = payload.get("sub")

    try:
        user_id = int(sub)  # type: ignore
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # ✅ Add this check
    if user.is_blocked:
        raise HTTPException(
            status_code=403,
            detail="Your account has been blocked."
        )

    return user