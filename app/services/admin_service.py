from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.user import User
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from datetime import datetime, timedelta 
from fastapi import HTTPException
from app.schemas.post import (
    PostUpdate,
    AdminPostResponse,
)

from app.schemas.admin import (
    AdminDashboardResponse,
    AdminUserResponse,
    AdminUserUpdate,
    
)


def get_dashboard_stats(db: Session) -> AdminDashboardResponse:
    total_users = db.query(func.count(User.id)).scalar() or 0

    total_posts = db.query(func.count(Post.id)).scalar() or 0

    active_posts = (
        db.query(func.count(Post.id))
        .filter(Post.status == "active")
        .scalar()
        or 0
    )

    archived_posts = (
        db.query(func.count(Post.id))
        .filter(Post.status == "archived")
        .scalar()
        or 0
    )

    one_week_ago = datetime.utcnow() - timedelta(days=7)

    new_users = (
    db.query(func.count(User.id))
    .filter(User.created_at >= one_week_ago)
    .scalar()
    or 0
    )

    total_likes = db.query(func.count(Like.id)).scalar() or 0

    total_comments = db.query(func.count(Comment.id)).scalar() or 0

    return AdminDashboardResponse(
        total_users=total_users,
        total_posts=total_posts,
        active_posts=active_posts,
        archived_posts=archived_posts,
        new_users=new_users,
        total_likes=total_likes,
        total_comments=total_comments,
    )

def get_all_users(db: Session):
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return users

def get_user_by_id(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

def update_user(
    db: Session,
    user_id: int,
    data: AdminUserUpdate,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items(): #upadting the model object 
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

def delete_user(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }

def block_user(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.is_blocked = True

    db.commit()
    db.refresh(user)

    return {
        "message": "User blocked successfully"
    }

def unblock_user(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.is_blocked = False

    db.commit()
    db.refresh(user)

    return {
        "message": "User unblocked successfully"
    }
#Post management 

def get_all_posts(db: Session):

    posts = (
        db.query(Post)
        .options(
            selectinload(Post.user),
            selectinload(Post.likes),
            selectinload(Post.comments),
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    return [
        AdminPostResponse(
            id=post.id,
            user_id=post.user_id,

            username=post.user.username,

            content=post.content,
            image_url=post.image_url,
            status=post.status,

            likes_count=len(post.likes),
            comments_count=len(post.comments),

            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        for post in posts
    ]

def get_post_by_id(
    db: Session,
    post_id: int,
):

    post = (
        db.query(Post)
        .options(
            selectinload(Post.user),  #loading the data erlier so it shoul dnot exexute multiple queries while looping
            selectinload(Post.likes),
            selectinload(Post.comments),
        )
        .filter(Post.id == post_id)
        .first()
    )


    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )


    return AdminPostResponse(
        id=post.id,
        user_id=post.user_id,

        username=post.user.username,

        content=post.content,
        image_url=post.image_url,
        status=post.status,

        likes_count=len(post.likes),
        comments_count=len(post.comments),

        created_at=post.created_at,
        updated_at=post.updated_at,
    )

def admin_update_post(
    db: Session,
    post_id: int,
    post_data: PostUpdate,
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    if post_data.content is not None:
        post.content = post_data.content

    if post_data.image_url is not None:
        post.image_url = post_data.image_url

    if post_data.status is not None:
        post.status = post_data.status

    db.commit()
    db.refresh(post)

    return post

def admin_delete_post(
    db: Session,
    post_id: int,
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }