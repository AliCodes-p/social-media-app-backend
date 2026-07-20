from datetime import datetime
from pydantic import BaseModel, ConfigDict

class FollowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    follower_id: int
    following_id: int
    created_at: datetime