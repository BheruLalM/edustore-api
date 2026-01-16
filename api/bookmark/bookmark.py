# api/bookmark/bookmark.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.bookmark.bookmark_service import BookmarkService
from api.bookmark.schema import ToggleResponse, BookmarkListResponse

router = APIRouter(prefix="/documents", tags=["Bookmark"])


@router.post(
    "/{document_id}/bookmark",
    response_model=ToggleResponse,
    status_code=status.HTTP_200_OK,
)
def bookmark_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookmarkService.add_bookmark(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )


@router.delete(
    "/{document_id}/bookmark",
    response_model=ToggleResponse,
    status_code=status.HTTP_200_OK,
)
def remove_bookmark(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookmarkService.remove_bookmark(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )


@router.get(
    "/bookmarks/me",
    response_model=BookmarkListResponse,
    status_code=status.HTTP_200_OK,
)
def my_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    return BookmarkService.get_my_bookmarks(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/users/{user_id}/bookmarks",
    response_model=BookmarkListResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_bookmarks(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    """View public bookmarks of a user (currently returns empty/private for privacy)"""
    # For now, we return empty as bookmarks are private. 
    # If we want public bookmarks, we'd add a visibility flag to Bookmark model.
    return {"items": [], "total": 0}
