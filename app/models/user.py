from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean

from app.db.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")

    # =========================
    # Relationships (Milestone 2)
    # =========================

    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    shares = relationship(
        "Share",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )

    followers = relationship(
        "Follow", #just tell that there is a table of follow with which we have a releation 
        foreign_keys="Follow.following_id", #swl alchemy wat reference to the mapped column
        back_populates="following",
        cascade="all, delete-orphan"
    )

    sent_friend_requests = relationship(
    "FriendRequest",
    foreign_keys="FriendRequest.sender_id",
    back_populates="sender",
    cascade="all, delete-orphan",
    )

    received_friend_requests = relationship(
    "FriendRequest",
    foreign_keys="FriendRequest.receiver_id",
    back_populates="receiver",
    cascade="all, delete-orphan",
    )