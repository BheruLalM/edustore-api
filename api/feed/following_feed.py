from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.feed_service.following_feed_service import FeedService
from api.feed.schema import DocumentFeedItem
from typing import List

router = APIRouter(prefix="/feed/private", tags=["Feed"])

@router.get("/following", response_model=List[DocumentFeedItem])
def following_feed(
   
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FeedService.get_following_feed(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
