from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.models.user import User
from app.schemas.like import LikeCreate, LikeResponse
from app.services.auth_dependency import get_current_user
from app.services.like_service import (
    like_post,
    unlike_post,
)

router = APIRouter(
    tags=["Likes"],
)


# =========================
# LIKE POST
# =========================
@router.post(
    "/posts/{post_id}/like",
    response_model=LikeResponse,
)
def like_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like_data = LikeCreate(post_id=post_id)

    return like_post(
        db,
        like_data,
        current_user,
    )


# =========================
# UNLIKE POST
# =========================
@router.delete("/posts/{post_id}/like")
def unlike_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return unlike_post(
        db,
        post_id,
        current_user,
    )