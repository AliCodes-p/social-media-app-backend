from datetime import datetime
from pydantic import BaseModel


class FeedResponse(BaseModel):
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
    shared_by_user_id: int |None
    shared_at: datetime | None
    

    # NEW
    likes_count: int
    liked_by_me: bool