from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.comment_service.comments import CommentService
from services.comment_service.tree_creation import get_document_comments
from api.comments.schema import CommentCreate, CommentResponse

router = APIRouter(tags=["Comments"])

@router.post("/documents/{document_id}/comments", response_model=CommentResponse)
def add_comment(
    document_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentService.create_comment(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        content=payload.content,
        parent_id=payload.parent_id,
    )

    # Get student data if available
    from models.student import Student
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    
    return {
        "id": comment.id,
        "content": None if comment.is_deleted else comment.content,
        "is_deleted": comment.is_deleted,
        "user": {
            "id": current_user.id,
            "name": student.name if student else None,
            "email": getattr(current_user, "email", None),
            "username": (student.name if student else None) or getattr(current_user, "email", None),
            "avatar_url": student.profile_url if student else None,
        },
        "created_at": comment.created_at,
        "replies": [],
    }

@router.get("/documents/{document_id}/comments", response_model=List[CommentResponse])
def get_comments(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import time
    start_time = time.time()
    
    # Verify document access before returning comments
    from models.document import Document
    from core.exceptions import DocumentNotFound, DocumentAccessDenied
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted.is_(False),
    ).first()
    
    if not document:
        raise DocumentNotFound()
    
    # Enforce visibility rules
    if document.visibility == "private" and document.user_id != current_user.id:
        raise DocumentAccessDenied()
    
    result = get_document_comments(db=db, document_id=document_id)
    
    elapsed = time.time() - start_time
    print(f"⏱️  GET /documents/{document_id}/comments completed in {elapsed:.3f}s ({len(result)} comments)")
    
    return result

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from models.comments import Comment
    from fastapi import HTTPException

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    success = CommentService.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
    )
    return {"success": success}
