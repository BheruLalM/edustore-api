from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.likes import Like
from models.document import Document
from models.user import User
from models.student import Student
from fastapi import HTTPException, status


class LikeService:

    @staticmethod
    def like_document(
        *,
        db: Session,
        document_id: int,
        current_user: User,
    ) -> bool:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Atomic toggle: try to insert, if conflict then delete
        try:
            like = Like(
                user_id=current_user.id,
                document_id=document_id,
            )
            db.add(like)
            db.commit()
            from services.cache.cache_manager import CacheManager
            CacheManager.invalidate_document(document_id)
            return True  # Successfully liked
        except IntegrityError:
            # Like already exists, remove it (unlike)
            db.rollback()
            db.query(Like).filter(
                Like.user_id == current_user.id,
                Like.document_id == document_id,
            ).delete()
            db.commit()
            from services.cache.cache_manager import CacheManager
            CacheManager.invalidate_document(document_id)
            return False  # Successfully unliked

    @staticmethod
    def unlike_document(
        *,
        db: Session,
        document_id: int,
        current_user: User,
    ) -> bool:
        like = db.query(Like).filter(
            Like.user_id == current_user.id,
            Like.document_id == document_id,
        ).first()

        if like:
            db.delete(like)
            db.commit()

        return False  # idempotent: already unliked

    @staticmethod
    def get_like_info(
        *,
        db: Session,
        document_id: int,
        current_user: User,
    ):
        like_count = db.query(Like).filter(
            Like.document_id == document_id
        ).count()

        is_liked = db.query(Like).filter(
            Like.document_id == document_id,
            Like.user_id == current_user.id,
        ).first() is not None

        return like_count, is_liked

    @staticmethod
    def get_like_users(
        *,
        db: Session,
        document_id: int,
        limit: int,
        offset: int,
    ):
        limit = min(limit, 50)

        
        likes = (
            db.query(Like, Student)
            .join(User, User.id == Like.user_id)
            .join(Student, Student.user_id == User.id)
            .filter(Like.document_id == document_id)
            .order_by(Like.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        total = db.query(Like).filter(
            Like.document_id == document_id
        ).count()

        items = [
            {
                "user": {
                    "id": student.user_id,
                    "name": student.name,
                },
                "liked_at": like.created_at,
            }
            for like, student in likes
        ]

        return items, total
