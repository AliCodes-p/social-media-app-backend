from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate


# =========================
# CREATE COMMENT
# =========================
def create_comment(
    db: Session,
    comment_data: CommentCreate,
    current_user: User,
):
    # Check if post exists and is active
    post = (
        db.query(Post)
        .filter(
            Post.id == comment_data.post_id,
            Post.status == "active",
        )
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found or is archived",
        )

    new_comment = Comment(
        content=comment_data.content,
        post_id=comment_data.post_id,
        user_id=current_user.id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# =========================
# GET COMMENTS FOR POST
# =========================
def get_comments_for_post(
    db: Session,
    post_id: int,
):
    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .all()
    )


# =========================
# UPDATE COMMENT
# =========================
def update_comment(
    db: Session,
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User,
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Only the comment owner can edit
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed",
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


# =========================
# DELETE COMMENT
# =========================
def delete_comment(
    db: Session,
    comment_id: int,
    current_user: User,
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )
    #chekc to see if post is valid

    post = (
      db.query(Post)
      .filter(Post.id == comment.post_id)
      .first()
       )

    if not post:
      raise HTTPException(
        status_code=404,
        detail="Post not found",
        )

    if (
     comment.user_id != current_user.id
     and post.user_id != current_user.id
    ):
     raise HTTPException(
        status_code=403,
        detail="Not allowed",
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }