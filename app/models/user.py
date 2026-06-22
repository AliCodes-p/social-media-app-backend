from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from app.db.database import Base
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    