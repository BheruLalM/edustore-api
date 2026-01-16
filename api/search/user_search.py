from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user, get_current_user_optional
from models.user import User
from services.search_service.user_search import UserSearchService
from api.search.schema import (
    UserSearchRequest,
    UserSearchResponse,
)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/users",
    response_model=UserSearchResponse,
)
def search_users(
    params: UserSearchRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional), 
):
    users = UserSearchService.search_users(
        db=db,
        query=params.query,
        current_user=current_user,
        limit=params.limit,
        offset=params.offset,
    )

    return {"results": users}
