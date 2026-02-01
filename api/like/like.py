from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.like.like_service import LikeService
from api.like.schema import (
    LikeToggleResponse,
    LikeCountResponse,
    LikeListResponse,
)

router = APIRouter(prefix="/documents", tags=["Like"])


@router.post(
    "/{document_id}/like",
    response_model=LikeToggleResponse,
    status_code=status.HTTP_200_OK,
)
def like_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_liked = LikeService.like_document(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )

    # Get updated count
    updated_count, _ = LikeService.get_like_info(
        db=db,
        document_id=document_id,
        current_user=current_user
    )

    return {
        "document_id": document_id,
        "is_liked": is_liked,
        "like_count": updated_count,
    }


@router.delete(
    "/{document_id}/like",
    response_model=LikeToggleResponse,
    status_code=status.HTTP_200_OK,
)
def unlike_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_liked = LikeService.unlike_document(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )

    # Get updated count
    updated_count, _ = LikeService.get_like_info(
        db=db,
        document_id=document_id,
        current_user=current_user
    )

    return {
        "document_id": document_id,
        "is_liked": is_liked,
        "like_count": updated_count,
    }


@router.get(
    "/{document_id}/likes",
    response_model=LikeCountResponse,
    status_code=status.HTTP_200_OK,
)
def get_like_info(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like_count, is_liked = LikeService.get_like_info(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )

    return {
        "document_id": document_id,
        "like_count": like_count,
        "is_liked": is_liked,
    }


@router.get(
    "/{document_id}/likes/users",
    response_model=LikeListResponse,
    status_code=status.HTTP_200_OK,
)
def get_like_users(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    items, total = LikeService.get_like_users(
        db=db,
        document_id=document_id,
        limit=limit,
        offset=offset,
    )

    return {
        "items": items,
        "total": total,
    }
