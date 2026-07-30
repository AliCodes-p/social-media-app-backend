from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base



class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
    ForeignKey(
        "conversations.id",
        ondelete="CASCADE"
    ),
    nullable=False
    )

    sender_id = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
    String,
    default="sent",
    nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    conversation = relationship(
    "Conversation",
    back_populates="messages"
    )
    
    sender = relationship(
    "User",
    foreign_keys=[sender_id],
    back_populates="sent_messages"
    )