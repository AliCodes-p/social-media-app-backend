from datetime import datetime
from sqlalchemy import Boolean

from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    image_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String,
        default="active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="posts")
    comments = relationship(
    "Comment",
    back_populates="post",
    cascade="all, delete-orphan"
    )
    likes = relationship(
    "Like",
    back_populates="post",
    cascade="all, delete-orphan"
    )
    shares = relationship(
    "Share",
    back_populates="post",
    cascade="all, delete-orphan"
    )
