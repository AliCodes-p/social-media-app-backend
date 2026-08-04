from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.follows import Follow
from fastapi import HTTPException

def follow_user(
    db: Session,
    current_user: User,
    user_id: int
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot follow yourself."
        )

    user_to_follow = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    if user_to_follow is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    existing_follow = (
    db.query(Follow)
    .filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    )
    .first()
    )

    if existing_follow:
        raise HTTPException(
            status_code=400,
            detail="You are already following this user."
        )

    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )
    db.add(follow)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="You are already following this user.",
        )

    db.refresh(follow)
    return follow

def unfollow_user(
    db: Session,
    current_user: User,
    user_id: int
):
    follow = (
    db.query(Follow)
    .filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    )
    .first()
    )
    if not follow:
        raise HTTPException(
            status_code=404,
            detail="You are not following this user."
        )
        
    db.delete(follow)
    db.commit()
    return {"message": "User unfollowed successfully."}

#USE SO THAT WE CAN DISPLAY ALL THE USER FOLLOWED IN PROFILE PAGE

def get_following(
    db: Session,
    user_id: int
):
    """
    Get all users that a user is following
    """

    return (
        db.query(User)
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == user_id)
        .all()
    )


# USE TO DECIDE WHETHER TO SHOW FOLLOWING OR NOT ON FRONTEND 

def is_following(
    db: Session,
    follower_id: int,
    following_id: int
):
    """
    Check if follower_id is following following_id
    """

    return (
        db.query(Follow)
        .filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
        )
        .first()
        is not None
    )