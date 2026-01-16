from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, literal, case
from models.document import Document
from models.user import User
from models.student import Student
from models.comments import Comment
from models.likes import Like
from models.bookmark import Bookmark
from services.storage.factory import StorageFactory
from services.cache.redis_service import cache
import json

class DocumentSearchService:

    @staticmethod
    def search_documents(
        *,
        db: Session,
        query: str,
        current_user: User | None,
        limit: int = 20,
        offset: int = 0,
    ):

        if not query or len(query.strip()) < 2:
            return []

        limit = min(limit, 50)
        query_str = query.strip().lower()

        # ------------------------------------------------------------------
        # REDIS CACHE (Public Only)
        # ------------------------------------------------------------------
        cache_key = f"search:docs:{query_str}:{offset}:{limit}"
        use_cache = current_user is None
        
        if use_cache:
            cached_results = cache.get(cache_key)
            if cached_results:
                return cached_results

        # ------------------------------------------------------------------
        # OPTIMIZATION: Subqueries for Counts and Status
        # ------------------------------------------------------------------
        
        # 1. Comment Count
        comment_count_sq = (
            db.query(func.count(Comment.id))
            .filter(Comment.document_id == Document.id)
            .correlate(Document)
            .scalar_subquery()
            .label("comment_count")
        )

        # 2. Like Count
        like_count_sq = (
            db.query(func.count(Like.id))
            .filter(Like.document_id == Document.id)
            .correlate(Document)
            .scalar_subquery()
            .label("like_count")
        )

        # 3. Is Liked & Is Bookmarked (If User Logged In)
        is_liked_col = literal(False).label("is_liked")
        is_bookmarked_col = literal(False).label("is_bookmarked")

        if current_user:
            is_liked_sq = (
                db.query(Like.id)
                .filter(
                    Like.user_id == current_user.id,
                    Like.document_id == Document.id
                )
                .correlate(Document)
                .exists()
            )
            is_liked_col = case((is_liked_sq, True), else_=False).label("is_liked")

            is_bookmarked_sq = (
                db.query(Bookmark.id)
                .filter(
                    Bookmark.user_id == current_user.id,
                    Bookmark.document_id == Document.id
                )
                .correlate(Document)
                .exists()
            )
            is_bookmarked_col = case((is_bookmarked_sq, True), else_=False).label("is_bookmarked")

        # Base Query
        base_query = (
            db.query(
                Document, 
                Student, 
                comment_count_sq,
                like_count_sq,
                is_liked_col,
                is_bookmarked_col
            )
            .outerjoin(Student, Student.user_id == Document.user_id)
            .filter(
                Document.is_deleted.is_(False),
                or_(
                    Document.title.ilike(f"%{query}%"),
                    Document.doc_type.ilike(f"%{query}%"),
                ),
            )
        )

        # Visibility Filter
        if current_user:
            base_query = base_query.filter(
                or_(
                    Document.visibility == "public",
                    and_(
                        Document.visibility == "private",
                        Document.user_id == current_user.id,
                    ),
                )
            )
        else:
            base_query = base_query.filter(
                Document.visibility == "public"
            )

        # Execution
        documents = (
            base_query
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        storage = StorageFactory.get_storage()
        results = []

        for doc, student, comment_count, like_count, is_liked, is_bookmarked in documents:
            # Handle owner avatar
            owner_avatar = None
            if student and student.profile_url:
                try:
                    owner_avatar = storage.generate_download_url(
                        object_key=student.profile_url,
                        expires_in=31536000,
                    )
                except Exception:
                    pass

            results.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "visibility": doc.visibility,
                "owner_id": doc.user_id,
                "created_at": doc.created_at,
                "owner_name": student.name if student else None,
                "owner_avatar": owner_avatar,
                "comment_count": comment_count or 0,
                "like_count": like_count or 0,
                "is_liked": bool(is_liked),
                "is_bookmarked": bool(is_bookmarked),
            })

        # Set Cache
        if use_cache:
            cache.set(cache_key, results, ttl=60)

        return results
