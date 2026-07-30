from datetime import datetime
from pydantic import BaseModel,ConfigDict


class MessageCreate(BaseModel):
    conversation_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    