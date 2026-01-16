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
    def get_following_feed(*, db: Session, user_id: int, limit: int = 20, offset: int = 0):
        """Get feed of users you follow - Optimized"""
        import time
        start_time = time.time()
        
        limit = min(limit, 50)

        # 1. Try CACHE (Per-user)
        cache_key = f"feed:following:u{user_id}:p{offset}:l{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"⚡ Following Feed Cache HIT: {cache_key}")
            return cached_data

        # 2. Check if following anyone (SHORT-CIRCUIT)
        # This is faster than joining first
        following_exists = db.query(Follow.id).filter(Follow.follower_id == user_id).first()
        if not following_exists:
            print("ℹ️ User follows no one, returning empty feed.")
            return []

        # ------------------------------------------------------------------
        # OPTIMIZED QUERY
        # ------------------------------------------------------------------
        
        # Subqueries for stats
        like_sq = db.query(func.count(Like.id)).filter(Like.document_id == Document.id).correlate(Document).scalar_subquery()
        comm_sq = db.query(func.count(Comment.id)).filter(Comment.document_id == Document.id).correlate(Document).scalar_subquery()

        # User interaction flags
        liked_exists = db.query(Like.id).filter(Like.document_id == Document.id, Like.user_id == user_id).correlate(Document).exists()
        is_liked = case((liked_exists, True), else_=False).label("is_liked")
        
        bookmarked_exists = db.query(Bookmark.id).filter(Bookmark.document_id == Document.id, Bookmark.user_id == user_id).correlate(Document).exists()
        is_bookmarked = case((bookmarked_exists, True), else_=False).label("is_bookmarked")

        # Main Query execution
        results = (
            db.query(Document, User, Student, like_sq, comm_sq, is_liked, is_bookmarked)
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
        from services.storage.url_cache import StorageURLCache
        
        response_data = []

        for doc, owner, student, l_cnt, c_cnt, liked, bookmarked in results:
            owner_avatar = StorageURLCache.get_avatar_url(student.profile_url) if student else StorageURLCache.get_avatar_url(None)

            response_data.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at,
                "owner_id": doc.user_id,
                "owner_name": student.name if student else owner.email.split("@")[0],
                "owner_avatar": owner_avatar,
                "owner_email": owner.email,
                "comment_count": c_cnt or 0,
                "content": doc.content,  
                "content_type": doc.content_type,
                "like_count": l_cnt or 0,
                "is_liked": bool(liked),
                "is_bookmarked": bool(bookmarked),
            })

        # Cache for 1 minute for this user
        cache.set(cache_key, response_data, ttl=60)

        elapsed = time.time() - start_time
        print(f"⏱️  GET /feed/private/following | db={elapsed:.3f}s | cache=MISS")

        return response_data
