from datetime import datetime

from pydantic import BaseModel, ConfigDict ,Field

class PostCreate(BaseModel):
    content: str = Field(default="", max_length=5000)
    image_url: str | None = None

    
class PostUpdate(BaseModel):
    content: str | None = Field(default=None, max_length=5000)
    image_url: str | None = None
    status: str | None = None

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    content: str
    image_url: str | None
    status: str

    created_at: datetime
    updated_at: datetime

class ProfilePostResponse(BaseModel):
    id: str
    type: str

    post_id: int
    user_id: int

    content: str
    image_url: str | None
    status: str

    created_at: datetime
    updated_at: datetime

    is_shared: bool
    shared_by_user_id: int | None
    shared_at: datetime | None

    likes_count: int
    comments_count: int
    liked_by_me: bool