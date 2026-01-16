from sqlalchemy.orm import Session
from sqlalchemy import func, case, exists, literal
from models.document import Document
from models.likes import Like
from models.comments import Comment
from models.user import User
from models.student import Student
from models.bookmark import Bookmark
from services.storage.factory import StorageFactory
from services.cache.redis_service import cache

class FeedService:
    @staticmethod
    def get_public_feed(
        *,
        db: Session,
        limit: int,
        offset: int,
        current_user: User | None = None,
    ) -> list[dict]:
        import time
        start_time = time.time()

        limit = min(limit, 50)
        
        # 1. Try SHARED BASE CACHE (No user-specific data)
        base_cache_key = f"feed:public:base:p{offset}:l{limit}"
        base_feed = cache.get(base_cache_key)
        
        if base_feed:
            # Cache HIT: Hydrate user-specific fields
            if current_user:
                from services.cache.user_state import UserStateCache
                liked_ids = UserStateCache.get_liked_ids(db, current_user.id)
                bookmarked_ids = UserStateCache.get_bookmarked_ids(db, current_user.id)
                
                for item in base_feed:
                    item["is_liked"] = item["id"] in liked_ids
                    item["is_bookmarked"] = item["id"] in bookmarked_ids
            
            elapsed = time.time() - start_time
            print(f"⚡ Feed Cache HIT: {base_cache_key} | hydrated in {elapsed:.3f}s")
            return base_feed

        # ------------------------------------------------------------------
        # CACHE MISS: Query DB
        # ------------------------------------------------------------------
        
        # Subqueries for stats
        like_sq = db.query(func.count(Like.id)).filter(Like.document_id == Document.id).correlate(Document).scalar_subquery()
        comm_sq = db.query(func.count(Comment.id)).filter(Comment.document_id == Document.id).correlate(Document).scalar_subquery()

        # Main Query execution (NO user-specific fields)
        results = (
            db.query(Document, User, Student, like_sq, comm_sq)
            .join(User, Document.user_id == User.id)
            .outerjoin(Student, Student.user_id == User.id)
            .filter(Document.visibility == "public", Document.is_deleted.is_(False))
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        from services.storage.url_cache import StorageURLCache
        
        response_data = []
        for doc, owner, student, l_cnt, c_cnt in results:
            owner_avatar = StorageURLCache.get_avatar_url(student.profile_url) if student else StorageURLCache.get_avatar_url(None)
            
            response_data.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at,
                "owner_id": doc.user_id,
                "content": doc.content,
                "content_type": doc.content_type,
                "like_count": l_cnt or 0,
                "comment_count": c_cnt or 0,
                "is_liked": False,  # Default, will be hydrated
                "is_bookmarked": False,  # Default, will be hydrated
                "owner_name": student.name if student else owner.email.split("@")[0],
                "owner_email": owner.email,
                "owner_avatar": owner_avatar,
            })

        # Cache the BASE feed (shared by all users)
        cache.set(base_cache_key, response_data, ttl=120)
        
        # Hydrate user-specific fields for current request
        if current_user:
            from services.cache.user_state import UserStateCache
            liked_ids = UserStateCache.get_liked_ids(db, current_user.id)
            bookmarked_ids = UserStateCache.get_bookmarked_ids(db, current_user.id)
            
            for item in response_data:
                item["is_liked"] = item["id"] in liked_ids
                item["is_bookmarked"] = item["id"] in bookmarked_ids

        elapsed = time.time() - start_time
        print(f"⏱️  GET /feed/public | db={elapsed:.3f}s | cache=MISS")

        return response_data

    @staticmethod
    def clear_feed_cache():
        """Invalidate all feed caches"""
        cache.delete_pattern("feed:public:*")
        print("🧹 Public feed cache invalidated")
