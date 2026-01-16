from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from models.user import User
from dependencies.get_current_user import get_current_user
from api.profile.schema import AvatarUploadRequest, AvatarCommitRequest
from services.file_service.avatar_service import AvatarService

router = APIRouter(prefix="/profile/avatar", tags=["Profile"])


@router.post("/upload-url")
def upload_avatar_url(
    data: AvatarUploadRequest,
    current_user: User = Depends(get_current_user),
):
    return AvatarService.generate_upload_url(
        current_user=current_user,
        content_type=data.content_type,
    )


@router.patch("/commit")
def commit_avatar(
    data: AvatarCommitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AvatarService.commit_avatar(
        db=db,
        current_user=current_user,
        object_key=data.object_key,
    )


@router.delete("/delete")
def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AvatarService.delete_avatar(
        db=db,
        current_user=current_user,
    )
