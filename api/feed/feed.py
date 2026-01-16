from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user_optional, get_current_user
from models.user import User
from services.feed_service.feed_service import FeedService
from services.feed_service.following_feed_service import FeedService as FollowingFeedService
from api.feed.schema import DocumentFeedItem

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/public", response_model=List[DocumentFeedItem])
def public_document_feed(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    limit: int = 20,
    offset: int = 0,
):
    return FeedService.get_public_feed(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )

@router.get("/private/following", response_model=List[DocumentFeedItem])
def following_document_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    """
    Get feed of documents from users the current user follows.
    Requires strict authentication.
    """
    return FollowingFeedService.get_following_feed(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
