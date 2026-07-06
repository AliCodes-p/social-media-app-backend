from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.share import Share
from app.models.post import Post
from app.models.user import User
from app.schemas.share import ShareCreate


# =========================
# SHARE POST
# =========================
def share_post(db: Session, share_data: ShareCreate, current_user: User):

    # check if post exists
    # Check if post exists and is active
    post = (
    db.query(Post)
    .filter(
        Post.id == share_data.post_id,
        Post.status == "active",
    )
    .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found or is archived",
        )
    # optional: prevent duplicate share (because you used UniqueConstraint)
    existing_share = db.query(Share).filter(
        Share.post_id == share_data.post_id,
        Share.user_id == current_user.id
    ).first()

    if existing_share:
     return existing_share
    new_share = Share(
        post_id=share_data.post_id,
        user_id=current_user.id
    )

    db.add(new_share)
    db.commit()
    db.refresh(new_share)

    return new_share

# =========================
# UNSHARE POST
# =========================
def unshare_post(
    db: Session,
    post_id: int,
    current_user: User,
):
    share = (
        db.query(Share)
        .filter(
            Share.post_id == post_id,
            Share.user_id == current_user.id,
        )
        .first()
    )

    if not share:
     return {"message": "Already unshared"}

    db.delete(share)
    db.commit()

    return {
        "message": "Post unshared successfully"
    }