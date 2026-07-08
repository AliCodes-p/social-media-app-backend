from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.post import Post
from app.models.share import Share
from app.models.like import Like
from app.models.user import User


def get_feed(db: Session, current_user: User):
    """
    Unified feed:
    - posts (original)
    - shares (reshare events)
    """

    # 🔥 IMPORTANT: load fresh data
    posts = (
        db.query(Post)
        .filter(Post.status == "active")
        .all()
    )

    shares = (
        db.query(Share)
        .join(Post)
        .filter(Post.status == "active")
        .all()
    )

    feed = []

    # ======================
    # ORIGINAL POSTS
    # ======================
    for post in posts:
     likes_count = (
        db.query(Like)
       .filter(Like.post_id == post.id)
       .count()
     )

     liked_by_me = (
      db.query(Like)
      .filter(
        Like.post_id == post.id,
        Like.user_id == current_user.id,
      )
       .first()
       is not None
     )
     feed.append({
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
            "likes_count": likes_count,
            "liked_by_me": liked_by_me,
        })

    # ======================
    # SHARES (RESHARES)
    # ======================
    for share in shares:
        post = share.post

        if not post or post.status != "active":
            continue
        likes_count = (
        db.query(Like)
        .filter(Like.post_id == post.id)
        .count()
      )

        liked_by_me = (
        db.query(Like)
        .filter(
          Like.post_id == post.id,
          Like.user_id == current_user.id,
      )
      .first()
      is not None
     )
        feed.append({
            "id": f"share_{share.id}",
            "type": "share",

            "post_id": post.id,
            "user_id": post.user_id,

            "content": post.content,
            "image_url": post.image_url,
            "status": post.status,

            "created_at": share.created_at,
            "updated_at": post.updated_at,

            "is_shared": True,
            "shared_by_user_id": share.user_id,
            "shared_at": share.created_at,
            "likes_count": likes_count,
            "liked_by_me": liked_by_me,
    })

    # sort newest first
    feed.sort(key=lambda x: x["created_at"], reverse=True)

    return feed