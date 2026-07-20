from app.schemas.follows import FollowResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.services.auth_dependency import get_current_user
from app.models.user import User
from app.services.follow_service import (
    follow_user,
    unfollow_user,
    get_following,
    is_following
)


router = APIRouter(
    prefix="/follows",
    tags=["Follows"]
)


# Follow a user
@router.post("/{user_id}",response_model=FollowResponse)
def follow(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return follow_user(
        db,
        current_user,
        user_id
    )


# Unfollow a user
@router.delete("/{user_id}")
def unfollow(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return unfollow_user(
        db,
        current_user,
        user_id
    )


# Get users that current user follows
@router.get("/following")
def following(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_following(
        db,
        current_user.id
    )


# Check follow status
@router.get("/status/{user_id}")
def follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return {
        "is_following": is_following(
            db,
            current_user.id,
            user_id
        )
    }