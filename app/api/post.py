from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import UploadFile, File, Form
from app.services.upload_service import upload_image


from app.db.dependency import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse, ProfilePostResponse
from app.services.post_service import (
    create_post,
    update_post,
    delete_post,
    archive_post,
    unarchive_post
)

from app.services.auth_dependency import get_current_user


router = APIRouter(prefix="/posts", tags=["Posts"])


# =========================
# CREATE POST
# =========================
@router.post("/", response_model=PostResponse)
def create_post_route(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_post(db, post_data, current_user)

#========================
# CREATE POST WITH IMAGE

@router.post("/upload", response_model=PostResponse)
def create_post_with_image(
    content: str = Form(""),   #Because we are uploading files, the request type is
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = upload_image(image)

    post_data = PostCreate(
        content=content,
        image_url=image_url,
    )

    return create_post(db, post_data, current_user)





# =========================
# UPDATE POST
# =========================
@router.patch("/{post_id}", response_model=PostResponse)
def update_post_route(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_post(db, post_id, post_data, current_user)


# =========================
# DELETE POST
# =========================
@router.delete("/{post_id}")
def delete_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_post(db, post_id, current_user)


# =========================
# ARCHIVE POST
# =========================
@router.patch("/{post_id}/archive", response_model=PostResponse)
def archive_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return archive_post(db, post_id, current_user)


# =========================
# UNARCHIVE POST
# =========================
@router.patch("/{post_id}/unarchive", response_model=PostResponse)
def unarchive_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return unarchive_post(db, post_id, current_user)