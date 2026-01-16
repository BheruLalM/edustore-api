from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from db.deps import get_db
from models.document import Document
from models.user import User
from models.bookmark import Bookmark
from models.comments import Comment
from dependencies.get_current_user import get_current_user_optional
from api.feed.schema import DocumentFeedItem

router = APIRouter(prefix="/users", tags=["Documents"])


@router.get("/{user_id}/documents", response_model=List[DocumentFeedItem])
def get_user_public_documents(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Get all public documents uploaded by a specific user - OPTIMIZED with pagination"""
    import time
    start_time = time.time()
    
    from models.student import Student
    from models.likes import Like
    from services.storage.factory import StorageFactory
    from sqlalchemy import func, case

    # Enforce max limit to prevent abuse
    limit = min(limit, 50)

    # Get current user ID for personalized checks
    current_user_id = current_user.id if current_user else None

    # OPTIMIZED: Single query with JOINs and aggregations
    # This replaces 80+ queries (4 per document) with 1 query
    query = (
        db.query(
            Document,
            User,
            Student,
            func.count(func.distinct(Like.id)).label('like_count'),
            func.count(func.distinct(Comment.id)).label('comment_count'),
            func.max(
                case(
                    (Like.user_id == current_user_id, 1),
                    else_=0
                )
            ).label('is_liked'),
            func.max(
                case(
                    (Bookmark.user_id == current_user_id, 1),
                    else_=0
                )
            ).label('is_bookmarked')
        )
        .join(User, Document.user_id == User.id)
        .outerjoin(Student, Student.user_id == User.id)
        .outerjoin(Like, Like.document_id == Document.id)
        .outerjoin(Comment, Comment.document_id == Document.id)
        .outerjoin(Bookmark, Bookmark.document_id == Document.id)
        .filter(
            Document.user_id == user_id,
            Document.visibility == "public",
            Document.is_deleted.is_(False),
        )
        .group_by(Document.id, User.id, Student.id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    results = query.all()

    # ✅ OPTIMIZED: Use cached URL helper instead of generating in loop
    from services.storage.url_cache import StorageURLCache
    
    response_data = []

    for doc, owner, student, like_count, comment_count, is_liked, is_bookmarked in results:
        # ✅ Cached avatar URL lookup (no storage API call if cached)
        owner_avatar = StorageURLCache.get_avatar_url(
            student.profile_url if student else None
        )

        response_data.append({
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "file_size": doc.file_size,
            "created_at": doc.created_at,
            "owner_id": doc.user_id,
            "owner_name": student.name if student else None,
            "owner_email": owner.email,
            "owner_avatar": owner_avatar,
            "content": doc.content,
            "content_type": doc.content_type,
            "like_count": like_count or 0,
            "is_liked": bool(is_liked),
            "comment_count": comment_count or 0,
            "is_bookmarked": bool(is_bookmarked),
        })

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{user_id}/documents completed in {elapsed:.3f}s ({len(response_data)} documents, limit={limit}, offset={offset})")
    
    return response_data
