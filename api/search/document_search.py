from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.search_service.document_search import DocumentSearchService
from api.search.schema import (
    DocumentSearchRequest,
    DocumentSearchResponse,
)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/documents",
    response_model=DocumentSearchResponse,
)
def search_documents(
    params: DocumentSearchRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
    
):
    documents = DocumentSearchService.search_documents(
        db=db,
        query=params.query,
        current_user=current_user,
        limit=params.limit,
        offset=params.offset,
    )

    return {"results": documents}
