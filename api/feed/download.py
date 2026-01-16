from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.file_service.download import DownloadService

router = APIRouter(prefix="/feed/document", tags=["Feed"])


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    return DownloadService.generate_download_url(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )
