from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth_dependency import get_current_user

from app.db.dependency import get_db
from app.schemas.feed import FeedResponse
from app.services.feed_service import get_feed

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


@router.get("/", response_model=list[FeedResponse])
def get_feed_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_feed(db, current_user)