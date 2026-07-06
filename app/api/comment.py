from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.services.auth_dependency import get_current_user
from app.services.comment_service import (
    create_comment,
    get_comments_for_post,
    update_comment,
    delete_comment,
)

router = APIRouter(
    tags=["Comments"],
)


# =========================
# CREATE COMMENT
# =========================
@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
)
def create_comment_route(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment_data.post_id = post_id

    return create_comment(
        db,
        comment_data,
        current_user,
    )


# =========================
# GET COMMENTS FOR POST
# =========================
@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommentResponse],
)
def get_comments_route(
    post_id: int,
    db: Session = Depends(get_db),
):
    return get_comments_for_post(
        db,
        post_id,
    )


# =========================
# UPDATE COMMENT
# =========================
@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment_route(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_comment(
        db,
        comment_id,
        comment_data,
        current_user,
    )


# =========================
# DELETE COMMENT
# =========================
@router.delete("/comments/{comment_id}")
def delete_comment_route(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_comment(
        db,
        comment_id,
        current_user,
    )