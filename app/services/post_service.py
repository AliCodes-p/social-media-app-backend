from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.like import Like
from app.models.comment import Comment

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
from app.models.like import Like
from app.models.comment import Comment


def get_all_posts(db: Session, current_user: User):
    posts = (
        db.query(Post)
        .filter(Post.status == "active")
        .order_by(Post.created_at.desc())
        .all()
    )

    # Load all likes once
    likes = db.query(Like).all()

    likes_count_map = {}
    liked_by_me_set = set()

    for like in likes:
        likes_count_map[like.post_id] = (
            likes_count_map.get(like.post_id, 0) + 1
        )

        if like.user_id == current_user.id:
            liked_by_me_set.add(like.post_id)

    # Load all comments once
    comments = db.query(Comment).all()

    comments_count_map = {}

    for comment in comments:
        comments_count_map[comment.post_id] = (
            comments_count_map.get(comment.post_id, 0) + 1
        )

    result = []

    for post in posts:
        result.append({
            "id": f"post_{post.id}",
            "type": "post",

            "post_id": post.id,
            "user_id": post.user_id,

            "content": post.content,
            "image_url": post.image_url,
            "status": post.status,

            "created_at": post.created_at,
            "updated_at": post.updated_at,

            "is_shared": False,
            "shared_by_user_id": None,
            "shared_at": None,

            "likes_count": likes_count_map.get(post.id, 0),
            "comments_count": comments_count_map.get(post.id, 0),
            "liked_by_me": post.id in liked_by_me_set,
        })

    return result


# =========================
# GET SINGLE POST
# =========================
def get_post_by_id(
    db: Session,
    post_id: int,
    current_user: User,
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Total likes
    likes_count = (
        db.query(Like)
        .filter(Like.post_id == post.id)
        .count()
    )

    # Total comments
    comments_count = (
        db.query(Comment)
        .filter(Comment.post_id == post.id)
        .count()
    )

    # Has the current user liked this post?
    liked_by_me = (
        db.query(Like)
        .filter(
            Like.post_id == post.id,
            Like.user_id == current_user.id,
        )
        .first()
        is not None
    )
    return {
     "id": f"post_{post.id}",
     "type": "post",

     "post_id": post.id,
     "user_id": post.user_id,

     "content": post.content,
     "image_url": post.image_url,
     "status": post.status,

     "created_at": post.created_at,
     "updated_at": post.updated_at,

     "likes_count": likes_count,
     "comments_count": comments_count,
     "liked_by_me": liked_by_me,

     "is_shared": False,
     "shared_by_user_id": None,
     "shared_at": None,
    }

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