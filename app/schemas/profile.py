from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bio: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime