from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
    Integer,
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False
    )
    provider = Column(String, nullable=False)  # google, github

    provider_user_id = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship(
    "User",
    back_populates="oauth_accounts"
    )