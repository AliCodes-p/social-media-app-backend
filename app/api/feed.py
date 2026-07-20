from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth_dependency import get_current_user

from app.db.dependency import get_db
from app.schemas.feed import FeedPage
from app.services.feed_service import get_feed

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


@router.get("/", response_model=FeedPage)
def get_feed_route(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_feed(
        db,
        current_user,
        limit,
        offset,
    )