from datetime import datetime

from pydantic import BaseModel, ConfigDict ,Field

class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    image_url: str | None = None

class PostUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=5000)
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