from datetime import datetime
from pydantic import BaseModel,ConfigDict,EmailStr
from typing import Optional


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_posts: int
    active_posts: int
    archived_posts: int
    new_users: int
    total_likes: int
    total_comments: int


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_verified: bool
    is_blocked: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

