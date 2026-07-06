from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like import LikeCreate


# =========================
# LIKE POST
# =========================
def like_post(db: Session, like_data: LikeCreate, current_user: User):

    # check if post exists
    post = (
    db.query(Post)
        .filter(
            Post.id == like_data.post_id,
            Post.status == "active"
        )
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # check if already liked
    existing_like = db.query(Like).filter(
        Like.post_id == like_data.post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked this post")

    new_like = Like(
        post_id=like_data.post_id,
        user_id=current_user.id
    )

    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like


# =========================
# UNLIKE POST
# =========================
def unlike_post(db: Session, post_id: int, current_user: User):

    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()

    return {"message": "Post unliked successfully"}