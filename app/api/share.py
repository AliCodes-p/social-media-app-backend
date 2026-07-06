from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.models.user import User
from app.schemas.share import ShareCreate, ShareResponse
from app.services.auth_dependency import get_current_user
from app.services.share_service import share_post, unshare_post

router = APIRouter(
    prefix="/posts",
    tags=["Shares"],
)


# =========================
# SHARE POST
# =========================
@router.post(
    "/{post_id}/share",
    response_model=ShareResponse,
)
def share_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    share_data = ShareCreate(post_id=post_id)

    return share_post(
        db,
        share_data,
        current_user,
    )


# =========================
# UNSHARE POST
# =========================
@router.delete("/{post_id}/share")
def unshare_post_route(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return unshare_post(
        db,
        post_id,
        current_user,
    )