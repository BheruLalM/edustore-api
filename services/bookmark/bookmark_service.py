# services/bookmark/bookmark_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.bookmark import Bookmark
from models.document import Document
from models.user import User

from core.exceptions import (
    DocumentNotFound,
    DocumentAccessDenied,
    AlreadyBookmarked,
)


class BookmarkService:

    @staticmethod
    def _get_accessible_document(
        *,
        db: Session,
        document_id: int,
        user: User,
    ) -> Document:
        """Fetch document and enforce access rules"""
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        ).first()

        if not document:
            raise DocumentNotFound()

        if document.visibility == "private" and document.user_id != user.id:
            raise DocumentAccessDenied()

        return document

    @staticmethod
    def add_bookmark(
        *,
        db: Session,
        document_id: int,
        current_user: User,
    ):
        document = BookmarkService._get_accessible_document(
            db=db,
            document_id=document_id,
            user=current_user,
        )

        # Atomic toggle: try to insert, if conflict then delete
        try:
            bookmark = Bookmark(
                user_id=current_user.id,
                document_id=document.id,
            )
            db.add(bookmark)
            db.commit()
            return {
                "document_id": document.id,
                "is_bookmarked": True,
            }
        except IntegrityError:
            # Bookmark already exists, remove it (unbookmark)
            db.rollback()
            db.query(Bookmark).filter(
                Bookmark.user_id == current_user.id,
                Bookmark.document_id == document.id,
            ).delete()
            db.commit()
            return {
                "document_id": document.id,
                "is_bookmarked": False,
            }

    @staticmethod
    def remove_bookmark(
        *,
        db: Session,
        document_id: int,
        current_user: User,
    ):
        bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.document_id == document_id,
        ).first()

        if bookmark:
            db.delete(bookmark)
            db.commit()

        return {
            "document_id": document_id,
            "is_bookmarked": False,
        }

    @staticmethod
    def is_bookmarked_by_user(
        *,
        db: Session,
        document_id: int,
        user_id: int,
    ) -> bool:
        return (
            db.query(Bookmark.id)
            .filter(
                Bookmark.user_id == user_id,
                Bookmark.document_id == document_id,
            )
            .first()
            is not None
        )

    @staticmethod
    def get_my_bookmarks(
        *,
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ):
        """Get user's bookmarked documents with optimized queries (no N+1)"""
        import time
        from sqlalchemy import func, case
        from models.student import Student
        from models.likes import Like
        from models.comments import Comment
        from services.storage.factory import StorageFactory
        from services.cache.redis_service import cache
        
        start_time = time.time()
        limit = min(limit, 50)

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

        # Main Query execution
        query = (
            db.query(Document, User, Student, Bookmark, like_count_sq, comment_count_sq, is_liked_col)
            .join(Bookmark, Bookmark.document_id == Document.id)
            .join(User, Document.user_id == User.id)
            .outerjoin(Student, Student.user_id == User.id)
            .filter(
                Bookmark.user_id == user_id,
                Document.is_deleted.is_(False),
            )
            .order_by(Bookmark.created_at.desc())
        )

        total = query.count()
        rows = query.offset(offset).limit(limit).all()

        # ------------------------------------------------------------------
        # RESULT FORMATTING
        # ------------------------------------------------------------------
        
        items = []

        for doc, owner, student, bookmark, like_count, comment_count, is_liked in rows:
            # Get cached avatar URL
            owner_avatar = None
            if student and student.profile_url:
                if student.profile_url.startswith("http"):
                    owner_avatar = student.profile_url
                else:
                    # Try cache first
                    cache_key = f"avatar_url:{student.profile_url}"
                    cached_url = cache.get(cache_key)
                    if cached_url:
                        owner_avatar = cached_url
                    else:
                        try:
                            storage = StorageFactory.get_storage()
                            owner_avatar = storage.generate_download_url(
                                object_key=student.profile_url,
                                expires_in=31536000,  # 1 year
                            )
                            # Cache for 1 hour
                            cache.set(cache_key, owner_avatar, ttl=3600)
                        except Exception:
                            pass

            items.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.file_size,
                "content": doc.content,
                "content_type": doc.content_type,
                "created_at": doc.created_at,
                "owner_id": doc.user_id,
                "owner_name": student.name if student else None,
                "owner_email": owner.email,
                "owner_avatar": owner_avatar,
                "visibility": doc.visibility,
                "bookmarked_at": bookmark.created_at,
                "like_count": like_count or 0,
                "is_liked": bool(is_liked),
                "comment_count": comment_count or 0,
                "is_bookmarked": True,  # Always true for bookmarks list
            })

        elapsed = time.time() - start_time
        print(f"⏱️  GET /documents/bookmarks/me completed in {elapsed:.3f}s (limit={limit}, offset={offset}, total={total})")

        return {
            "items": items,
            "total": total,
        }
