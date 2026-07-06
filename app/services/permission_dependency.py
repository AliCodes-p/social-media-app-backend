from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Post, User

def verify_post_owner(
    db: Session,
    post_id: int,
    current_user: User
) -> Post:

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return post