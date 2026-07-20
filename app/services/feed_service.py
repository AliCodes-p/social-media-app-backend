from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.share import Share
from app.models.like import Like
from app.models.user import User
from app.models.comment import Comment



def get_feed(
    db: Session,
    current_user: User,
    limit: int,
    offset: int,
):
    """
    Unified feed:
    - Original posts
    - Shared posts (reshare events)

    Optimized to avoid the N+1 query problem by loading
    likes and comments once and computing counts in memory.
    """

    # ======================
    # FIND FOLLOWING USERS
    # ======================

    following_ids = []

    for follow in current_user.following:
        following_ids.append(
        follow.following_id
    )

    # include my own posts
    following_ids.append(current_user.id)


    # ======================
    # LOAD FEED POSTS
    # ======================

    posts = (
        db.query(Post)
        .filter(
            Post.status == "active",
            Post.user_id.in_(following_ids)
        )
        .all()
    )
    post_ids = [   #extracting post id because later you want like and coment for only these posts
    post.id   
    for post in posts
    ]

    shares = (
    db.query(Share)
    .filter(
        Share.user_id.in_(following_ids)
    )
    .join(Post)
    .filter(
        Post.status == "active"
    )
    .all()
    )

    # ======================
    # LOAD ALL LIKES ONCE
    # ======================
    likes = (
    db.query(Like)
    .filter(
        Like.post_id.in_(post_ids)
    )
    .all()
    )

    likes_count_map = {}
    liked_by_me_set = set()

    for like in likes:
        likes_count_map[like.post_id] = (
            likes_count_map.get(like.post_id, 0) + 1
        )

        if like.user_id == current_user.id:
            liked_by_me_set.add(like.post_id)

    # ======================
    # LOAD ALL COMMENTS ONCE
    # ======================
    comments = (
        db.query(Comment)
        .filter(
            Comment.post_id.in_(post_ids)
        )
        .all()
    )

    comments_count_map = {}

    for comment in comments:
        comments_count_map[comment.post_id] = (
            comments_count_map.get(comment.post_id, 0) + 1
        )

    feed = []

    # ======================
    # ORIGINAL POSTS
    # ======================
    for post in posts:
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

            "likes_count": likes_count_map.get(post.id, 0),
            "liked_by_me": post.id in liked_by_me_set,

            "comments_count": comments_count_map.get(post.id, 0),
        })

    # ======================
    # SHARED POSTS
    # ======================
    for share in shares:
        post = share.post

        if not post or post.status != "active":
            continue

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

            "likes_count": likes_count_map.get(post.id, 0),
            "liked_by_me": post.id in liked_by_me_set,

            "comments_count": comments_count_map.get(post.id, 0),
        })

    # ======================
    # SORT NEWEST FIRST
    # ======================
    
    feed.sort(key=lambda x: x["created_at"], reverse=True)

    # ======================
    # PAGINATION
    # ======================
    total = len(feed)

    items = feed[offset:offset + limit]

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    }