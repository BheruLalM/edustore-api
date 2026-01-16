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
    """Get all public documents uploaded by a specific user - OPTIMIZED with Caching"""
    import time
    from models.student import Student
    from models.likes import Like
    from models.bookmark import Bookmark
    from models.comments import Comment
    from sqlalchemy import func, case, literal
    from services.cache.redis_service import cache
    from services.storage.url_cache import StorageURLCache

    start_time = time.time()
    limit = min(limit, 50)

    # 1. Try CACHE
    current_user_id = current_user.id if current_user else None
    cache_key = f"user:docs:{user_id}:p{offset}:l{limit}:u{current_user_id or 'anon'}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"⚡ User Docs Cache HIT: {cache_key}")
        return cached_data

    # ------------------------------------------------------------------
    # OPTIMIZED QUERY
    # ------------------------------------------------------------------
    like_sq = db.query(func.count(Like.id)).filter(Like.document_id == Document.id).correlate(Document).scalar_subquery()
    comm_sq = db.query(func.count(Comment.id)).filter(Comment.document_id == Document.id).correlate(Document).scalar_subquery()

    is_liked = literal(False).label("is_liked")
    is_bookmarked = literal(False).label("is_bookmarked")

    if current_user:
        liked_exists = db.query(Like.id).filter(Like.document_id == Document.id, Like.user_id == current_user_id).correlate(Document).exists()
        is_liked = case((liked_exists, True), else_=False).label("is_liked")
        
        bookmarked_exists = db.query(Bookmark.id).filter(Bookmark.document_id == Document.id, Bookmark.user_id == current_user_id).correlate(Document).exists()
        is_bookmarked = case((bookmarked_exists, True), else_=False).label("is_bookmarked")

    results = (
        db.query(Document, User, Student, like_sq, comm_sq, is_liked, is_bookmarked)
        .join(User, Document.user_id == User.id)
        .outerjoin(Student, Student.user_id == User.id)
        .filter(
            Document.user_id == user_id,
            Document.visibility == "public",
            Document.is_deleted.is_(False),
        )
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # ------------------------------------------------------------------
    # RESULT FORMATTING
    # ------------------------------------------------------------------
    response_data = []

    for doc, owner, student, like_cnt, comm_cnt, liked, bookmarked in results:
        owner_avatar = StorageURLCache.get_avatar_url(student.profile_url if student else None)

        response_data.append({
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "file_size": doc.file_size,
            "created_at": doc.created_at,
            "owner_id": doc.user_id,
            "owner_name": student.name if student else owner.email.split("@")[0],
            "owner_email": owner.email,
            "owner_avatar": owner_avatar,
            "content": doc.content,
            "content_type": doc.content_type,
            "like_count": like_cnt or 0,
            "is_liked": bool(liked),
            "comment_count": comm_cnt or 0,
            "is_bookmarked": bool(bookmarked),
        })

    # Cache for 2 minutes
    cache.set(cache_key, response_data, ttl=120)

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{user_id}/documents | db={elapsed:.3f}s | cache=MISS")
    
    return response_data
