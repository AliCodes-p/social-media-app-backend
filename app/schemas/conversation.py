from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationUser(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LastMessage(BaseModel):
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    other_user: ConversationUser

    last_message: LastMessage | None = None

    model_config = ConfigDict(from_attributes=True)