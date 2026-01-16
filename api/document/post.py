from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from api.document.schema import CreateTextPostSchema
from services.file_service.post import CreatePostService

router = APIRouter(prefix="/documents", tags=["Document"])


@router.post(
    "/post",
    status_code=status.HTTP_201_CREATED,
)
def create_text_post(
    payload: CreateTextPostSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = CreatePostService.create_post(
        db=db,
        user=current_user,
        title=payload.title,
        content=payload.content,
        visibility=payload.visibility,
    )

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "doc_type": post.doc_type,
        "visibility": post.visibility,
        "created_at": post.created_at,
    }
