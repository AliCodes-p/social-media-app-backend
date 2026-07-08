from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.services.permission_dependency import verify_post_owner





# =========================
# CREATE POST
# =========================
def create_post(db: Session, post_data: PostCreate, current_user: User):
    if not post_data.content.strip() and not post_data.image_url:
     raise HTTPException(
        status_code=400,
        detail="Post must contain text or an image."
    )
    new_post = Post(
        content=post_data.content,
        image_url=post_data.image_url,
        user_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# =========================
# GET ALL POSTS NOT ARCHIVED
# =========================
def get_all_posts(db: Session):
    return (
        db.query(Post)
        .filter(Post.status == "active")
        .order_by(Post.created_at.desc())
        .all()
    )


# =========================
# GET SINGLE POST
# =========================
def get_post_by_id(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


# =========================
# UPDATE POST
# =========================
def update_post(
    db: Session,
    post_id: int,
    post_data: PostUpdate,
    current_user: User
):
    post = verify_post_owner(db, post_id, current_user)

    if post_data.content is not None:
        post.content = post_data.content

    if post_data.image_url is not None:
        post.image_url = post_data.image_url

    if post_data.status is not None:
        post.status = post_data.status

    db.commit()
    db.refresh(post)

    return post


# =========================
# DELETE POST
# =========================
def delete_post(db: Session, post_id: int, current_user: User):

    post = verify_post_owner(db, post_id, current_user)
    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}


# =========================
# ARCHIVE POST
# =========================
def archive_post(db: Session, post_id: int, current_user: User):
    
    post = verify_post_owner(db, post_id, current_user)

    post.status = "archived"

    db.commit()
    db.refresh(post)

    return post


# =========================
# UNARCHIVE POST
# =========================
def unarchive_post(db: Session, post_id: int, current_user: User):
    
    post = verify_post_owner(db, post_id, current_user)

    post.status = "active"

    db.commit()
    db.refresh(post)

    return post