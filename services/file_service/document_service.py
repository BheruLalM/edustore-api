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
    def get_document_detail(
        *,
        db: Session,
        document_id: int,
        current_user: User | None,
    ) -> dict:

        from models.student import Student
        
        result = (
            db.query(Document, Student)
            .outerjoin(Student, Student.user_id == Document.user_id)
            .filter(
                Document.id == document_id,
                Document.is_deleted.is_(False),
            )
            .first()
        )

        if not result:
            raise DocumentNotFound()
        
        document, student = result

        if document.visibility == "private":
            if not current_user or document.user_id != current_user.id:
                raise DocumentAccessDenied()
        
        # Only generate download URL for files (not text posts)
        download_url = None
        if document.object_key:
            storage = StorageFactory.get_storage()
            try:
                download_url = storage.generate_download_url(
                    object_key=document.object_key,
                    expires_in=300,
                )
            except Exception:
                raise DownloadUrlGenerationFailed()

        # Handle owner avatar
        owner_avatar = None
        if student and student.profile_url:
            try:
                storage = StorageFactory.get_storage()
                owner_avatar = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                pass
        
        from models.likes import Like
        from models.comments import Comment
        from models.bookmark import Bookmark
        from sqlalchemy import func

        # Like Count
        like_count = db.query(func.count(Like.id)).filter(Like.document_id == document_id).scalar() or 0
        
        # Comment Count
        comment_count = db.query(func.count(Comment.id)).filter(Comment.document_id == document_id).scalar() or 0
        
        # Interaction status
        is_liked = False
        is_bookmarked = False
        if current_user:
            is_liked = db.query(Like).filter(Like.document_id == document_id, Like.user_id == current_user.id).exists()
            is_liked = db.query(is_liked).scalar()
            
            is_bookmarked = db.query(Bookmark).filter(Bookmark.document_id == document_id, Bookmark.user_id == current_user.id).exists()
            is_bookmarked = db.query(is_bookmarked).scalar()

        return {
            "id": document.id,
            "title": document.title,
            "doc_type": document.doc_type,
            "file_size": document.file_size,
            "content_type": document.content_type,
            "visibility": document.visibility,
            "created_at": document.created_at,
            "owner_id": document.user_id,
            "owner_name": student.name if student else None,
            "owner_avatar": owner_avatar,
            "content": document.content,  
            "file_url": download_url,
            "like_count": like_count,
            "comment_count": comment_count,
            "is_liked": is_liked,
            "is_bookmarked": is_bookmarked,
            "is_owner": bool(
                current_user and current_user.id == document.user_id
            ),
        }
