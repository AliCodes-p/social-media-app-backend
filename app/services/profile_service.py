from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileUpdate


# =========================
# GET MY PROFILE
# =========================
def get_my_profile(db: Session, current_user: User):

    profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# =========================
# CREATE PROFILE (optional - usually auto created)
# =========================
def create_profile(db: Session, current_user: User):

    existing_profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = Profile(
        user_id=current_user.id
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


# =========================
# UPDATE PROFILE
# =========================
def update_profile(db: Session, profile_data: ProfileUpdate, current_user: User):

    profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile_data.bio is not None:
        profile.bio = profile_data.bio

    if profile_data.avatar_url is not None:
        profile.avatar_url = profile_data.avatar_url

    db.commit()
    db.refresh(profile)

    return profile