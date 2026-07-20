from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FriendRequestCreate(BaseModel):
    receiver_id: int


class FriendRequestUpdate(BaseModel):
    status: str


class FriendRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    receiver_id: int
    status: str
    updated_at: datetime

class FriendStatusResponse(BaseModel):
    status: str