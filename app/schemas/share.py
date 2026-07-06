from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShareCreate(BaseModel):
    post_id: int


class ShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int
    created_at: datetime