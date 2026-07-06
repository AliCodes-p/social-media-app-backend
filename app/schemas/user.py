from pydantic import BaseModel,Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# ==========================
# Response Schemas
# ==========================

class UserCardResponse(BaseModel):
    id: int
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    bio: str | None = Field(default=None, max_length=500)