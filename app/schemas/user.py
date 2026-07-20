from pydantic import ConfigDict
from pydantic import BaseModel,Field

from app.schemas.post import ProfilePostResponse
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# ==========================
# Response Schemas
# ==========================

class UserCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None
    posts: list[ProfilePostResponse] = []


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    bio: str | None = Field(default=None, max_length=500)