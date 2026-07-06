from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LikeCreate(BaseModel):
    post_id: int


class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int
    created_at: datetime