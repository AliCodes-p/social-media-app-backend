from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from fastapi import UploadFile
from app.models.post import Post

from app.services.upload_service import upload_image

from app.schemas.user import UserUpdate
from app.models.user import User
from app.models.profile import Profile


def get_all_users(db: Session):
    """
    Returns all users with their profile information.
    """

    users = (
        db.query(User, Profile)
        .join(User.profile)
        .all()
    )

    result = []

    for user, profile in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "cover_url": profile.cover_url,
        })

    return result
def get_user_by_username(db: Session, username: str):

    user = (
        db.query(User, Profile)
        .join(User.profile)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user, profile = user

    return {
        "id": user.id,
        "username": user.username,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "cover_url": profile.cover_url,
    }
def search_users(db: Session, query: str):

    users = (
        db.query(User, Profile)
        .join(User.profile)
        .filter(User.username.ilike(f"%{query}%"))
        .all()
    )

    result = []

    for user, profile in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "cover_url": profile.cover_url,
        })

    return result

def update_user(
    db: Session,
    current_user: User,
    user_data: UserUpdate,
):

    # Get current user's profile
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    # Update username
    if user_data.username is not None:

        existing_user = (
            db.query(User)
            .filter(
                User.username == user_data.username,
                User.id != current_user.id,
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        current_user.username = user_data.username

    # Update bio
    if user_data.bio is not None:
        profile.bio = user_data.bio

    db.commit()
    db.refresh(current_user)
    db.refresh(profile)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "cover_url": profile.cover_url,
    }

#UPLOAD AVATAR


def upload_avatar(
    db: Session,
    current_user: User,
    avatar: UploadFile,
):
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    avatar_url = upload_image(avatar)

    profile.avatar_url = avatar_url

    db.commit()
    db.refresh(profile)

    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": profile.avatar_url,
    }

def get_my_profile(db: Session, current_user: User):

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    active_posts = (
        db.query(Post)
        .filter(
            Post.user_id == current_user.id,
            Post.status == "active"
        )
        .all()
    )

    return {
        "id": current_user.id,
        "username": current_user.username,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "cover_url": profile.cover_url,
        "posts": active_posts
    }
#=========================Get my archived posts==========================

def get_my_archived_posts(db: Session, current_user: User):

    return (
        db.query(Post)
        .filter(
            Post.user_id == current_user.id,
            Post.status == "archived"
        )
        .all()
    )