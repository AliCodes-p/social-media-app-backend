from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from app.schemas.user import UserUpdate
from fastapi import UploadFile, File
from app.services.user_service import upload_avatar , get_my_profile, get_my_archived_posts
from app.services.auth_dependency import get_current_user

from app.models.user import User

from app.services.auth_dependency import get_current_user

from app.models.user import User

from app.db.dependency import get_db
from app.schemas.user import (
    UserCardResponse,
    UserProfileResponse,
)

from app.services.user_service import (
    get_all_users,
    get_user_by_username,
    search_users,
    update_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# GET ALL USERS
# =========================
@router.get("/", response_model=list[UserCardResponse])
def get_all_users_route(
    db: Session = Depends(get_db)
):
    return get_all_users(db)


# =========================
# SEARCH USERS
# =========================
@router.get("/search", response_model=list[UserCardResponse])
def search_users_route(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return search_users(db, query)

# =========================
# GET MY PROFILE
 
@router.get("/me", response_model=UserProfileResponse)
def get_my_profile_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_profile(db, current_user)

#========================
# GET MY ARCHIVED POSTS

@router.get("/me/posts/archived")
def get_my_archived_posts_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_archived_posts(db, current_user)



# =========================
# GET USER BY USERNAME
# =========================
@router.get("/{username}", response_model=UserProfileResponse)
def get_user_by_username_route(
    
    username: str,
    db: Session = Depends(get_db)
):
    
    return get_user_by_username(db, username)

# =========================
# UPDATE CURRENT USER
# =========================
@router.patch("/me", response_model=UserProfileResponse)
def update_current_user_route(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(
        db,
        current_user,
        user_data,
    )

# =========================
# UPLOAD AVATAR
# =========================
@router.post("/upload_avatar")
def upload_avatar_route(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return upload_avatar(
        db,
        current_user,
        avatar,
    )



