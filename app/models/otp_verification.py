from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.db.database import Base

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    otp_code = Column(String, nullable=False)

    purpose = Column(String, nullable=False)  # register / reset_password

    expires_at = Column(DateTime, nullable=False)

    is_used = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)