from sqlalchemy.orm import Session
from services.storage.factory import StorageFactory

from models.document import Document
from models.user import User
from core.exceptions import (
    DocumentNotFound,
    DocumentAccessDenied,
    DownloadUrlGenerationFailed,
)


class DocumentService:
    @staticmethod
    @staticmethod
    def get_document_detail(
        *,
        db: Session,
        document_id: int,
        current_user: User | None,
    ) -> dict:
        import time
        from sqlalchemy import func, case
        from models.student import Student
        from models.likes import Like
        from models.comments import Comment
        from models.bookmark import Bookmark
        from services.cache.redis_service import cache
        from services.feed_service.feed_service import FeedService

        start_time = time.time()

        # 1. Try CACHE (Static data)
        cache_key = f"doc:detail:static:{document_id}"
        doc_static = cache.get(cache_key)

        if not doc_static:
            # Subqueries for counts
            like_sq = db.query(func.count(Like.id)).filter(Like.document_id == document_id).scalar_subquery()
            comm_sq = db.query(func.count(Comment.id)).filter(Comment.document_id == document_id).scalar_subquery()

            result = (
                db.query(Document, Student, like_sq, comm_sq)
                .outerjoin(Student, Student.user_id == Document.user_id)
                .filter(Document.id == document_id, Document.is_deleted.is_(False))
                .first()
            )

            if not result:
                raise DocumentNotFound()
            
            doc, student, like_cnt, comm_cnt = result

            # Generate owner avatar
            from services.storage.url_cache import StorageURLCache
            owner_avatar = StorageURLCache.get_avatar_url(student.profile_url) if student else StorageURLCache.get_avatar_url(None)

            doc_static = {
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "content_type": doc.content_type,
                "visibility": doc.visibility,
                "created_at": doc.created_at,
                "owner_id": doc.user_id,
                "owner_name": student.name if student else None,
                "owner_avatar": owner_avatar,
                "content": doc.content,
                "object_key": doc.object_key,
                "like_count": like_cnt or 0,
                "comment_count": comm_cnt or 0,
            }
            # Cache for 10 minutes
            cache.set(cache_key, doc_static, ttl=600)
        else:
            print(f"⚡ Doc Detail Static HIT: {document_id}")

        # 2. Privacy Check
        if doc_static["visibility"] == "private":
            if not current_user or doc_static["owner_id"] != current_user.id:
                raise DocumentAccessDenied()

        # 3. Dynamic Data (User interaction)
        is_liked = False
        is_bookmarked = False
        if current_user:
            is_liked = db.query(Like.id).filter(Like.document_id == document_id, Like.user_id == current_user.id).exists()
            is_liked = db.query(is_liked).scalar()
            
            is_bookmarked = db.query(Bookmark.id).filter(Bookmark.document_id == document_id, Bookmark.user_id == current_user.id).exists()
            is_bookmarked = db.query(is_bookmarked).scalar()

        # 4. Ephemeral Download and Preview URLs
        download_url = None
        preview_url = None
        if doc_static["object_key"]:
            storage = StorageFactory.get_storage()
            try:
                # Full download URL
                download_url = storage.generate_download_url(
                    object_key=doc_static["object_key"],
                    expires_in=3600, # 1 hour for detailed view
                )
                
                # Preview URL (first page for PDFs)
                if doc_static["doc_type"] == "pdf":
                    preview_url = storage.generate_download_url(
                        object_key=doc_static["object_key"],
                        expires_in=3600,
                        page=1
                    )
                else:
                    preview_url = download_url
                    
            except Exception:
                pass # Don't crash details if URL fails

        elapsed = time.time() - start_time
        print(f"⏱️  GET /feed/{document_id} | db={elapsed:.3f}s")

        return {
            **doc_static,
            "file_url": download_url,
            "preview_url": preview_url,
            "is_liked": is_liked,
            "is_bookmarked": is_bookmarked,
            "is_owner": bool(current_user and current_user.id == doc_static["owner_id"]),
        }
