from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.file_service.document_service import DocumentService

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/{document_id}")
def get_document_detail(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    import time
    start_time = time.time()
    
    result = DocumentService.get_document_detail(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )
    
    elapsed = time.time() - start_time 
    
    return result
