from sqlalchemy.orm import Session
from sqlalchemy import func, case, exists
from models.document import Document
from models.follow import Follow
from models.likes import Like
from models.comments import Comment
from models.user import User
from models.student import Student
from models.bookmark import Bookmark
from services.storage.factory import StorageFactory
from services.cache.redis_service import cache

class FeedService:
    @staticmethod
    def _get_avatar_url(object_key: str) -> str | None:
        """Get avatar URL with caching"""
        if not object_key:
            return None
            
        if object_key.startswith("http"):
            return object_key
            
        # Try cache first
        cache_key = f"avatar_url:{object_key}"
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url
        
        # Generate new URL
        try:
            storage = StorageFactory.get_storage()
            avatar_url = storage.generate_download_url(
                object_key=object_key,
                expires_in=31536000,  # 1 year
            )
            # Cache for 1 hour
            cache.set(cache_key, avatar_url, ttl=3600)
            return avatar_url
        except Exception:
            return None

    @staticmethod
    def get_following_feed(*, db: Session, user_id: int, limit: int = 20, offset: int = 0):
        import time
        start_time = time.time()
        
        limit = min(limit, 50)  # enforce max limit

        # ------------------------------------------------------------------
        # OPTIMIZED QUERY (Eliminates N+1)
        # ------------------------------------------------------------------
        
        # 1. Subquery for Like Count
        like_count_sq = (
            db.query(func.count(Like.id))
            .filter(Like.document_id == Document.id)
            .correlate(Document)
            .scalar_subquery()
            .label("like_count")
        )

        # 2. Subquery for Comment Count
        comment_count_sq = (
            db.query(func.count(Comment.id))
            .filter(Comment.document_id == Document.id)
            .correlate(Document)
            .scalar_subquery()
            .label("comment_count")
        )

        # 3. Subquery for Is Liked (by current user)
        # For following feed, user_id is always present
        is_liked_sq = (
            db.query(Like.id)
            .filter(
                Like.document_id == Document.id,
                Like.user_id == user_id
            )
            .correlate(Document)
            .exists()
        )
        is_liked_col = case((is_liked_sq, True), else_=False).label("is_liked")

        # 4. Subquery for Is Bookmarked (by current user)
        is_bookmarked_sq = (
            db.query(Bookmark.id)
            .filter(
                Bookmark.document_id == Document.id,
                Bookmark.user_id == user_id
            )
            .correlate(Document)
            .exists()
        )
        is_bookmarked_col = case((is_bookmarked_sq, True), else_=False).label("is_bookmarked")

        # Main Query execution
        results = (
            db.query(Document, User, Student, like_count_sq, comment_count_sq, is_liked_col, is_bookmarked_col)
            .join(Follow, Follow.following_id == Document.user_id)
            .join(User, Document.user_id == User.id)
            .outerjoin(Student, Student.user_id == User.id)
            .filter(
                Follow.follower_id == user_id,
                Document.visibility == "public",
                Document.is_deleted.is_(False)
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

        for doc, owner, student, like_count, comment_count, is_liked, is_bookmarked in results:
            # Get cached avatar URL
            owner_avatar = None
            if student and student.profile_url:
                owner_avatar = FeedService._get_avatar_url(student.profile_url)

            response_data.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at,
                "owner_id": doc.user_id,
                "owner_name": student.name if student else None,
                "owner_avatar": owner_avatar,
                "owner_email": owner.email,
                "comment_count": comment_count or 0,
                "content": doc.content,  
                "content_type": doc.content_type,
                "like_count": like_count or 0,
                "is_liked": bool(is_liked),
                "is_bookmarked": bool(is_bookmarked),
            })

        elapsed = time.time() - start_time
        print(f"⏱️  GET /feed/private/following completed in {elapsed:.3f}s (limit={limit}, offset={offset})")

        return response_data
