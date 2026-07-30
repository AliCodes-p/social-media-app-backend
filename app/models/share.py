from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Share(Base):
    __tablename__ = "shares"

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_share"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False
    )

    post_id: Mapped[int] = mapped_column(
    ForeignKey("posts.id", ondelete="CASCADE"),
    nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="shares"
    )

    post = relationship(
        "Post",
        back_populates="shares"
    )