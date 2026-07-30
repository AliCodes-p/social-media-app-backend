from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="user"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    @property
    def avatar_url(self) -> str | None:
        return self.profile.avatar_url if self.profile else None

    @property
    def bio(self) -> str | None:
        return self.profile.bio if self.profile else None

    @property
    def cover_url(self) -> str | None:
        return self.profile.cover_url if self.profile else None

    # =========================
    # Relationships
    # =========================

    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    shares = relationship(
        "Share",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    sent_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    received_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    oauth_accounts = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    otp_verifications = relationship(
        "OTPVerification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    conversation_participants = relationship(
        "ConversationParticipant",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    sent_messages = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
        passive_deletes=True
    )