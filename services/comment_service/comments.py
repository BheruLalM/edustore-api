from sqlalchemy.orm import Session
from models.comments import Comment
from models.document import Document
from core.exceptions import DocumentNotFound, DocumentAccessDenied


class CommentService:
    @staticmethod
    def create_comment(
        *,
        db: Session,
        document_id: int,
        user_id: int,
        content: str,
        parent_id: int | None = None,
    ) -> Comment:

        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise DocumentNotFound()

        # Example visibility check (update as per your rules)
        if document.visibility == "private" and document.user_id != user_id:
            raise DocumentAccessDenied()

        if parent_id:
            parent = db.query(Comment).filter(
                Comment.id == parent_id,
                Comment.document_id == document_id,
                Comment.is_deleted.is_(False),  # Prevent replies to deleted comments
            ).first()
            if not parent:
                raise DocumentNotFound()  # or custom ParentCommentNotFound()

        comment = Comment(
            document_id=document_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(
        *,
        db: Session,
        comment_id: int,
        user_id: int,
    ) -> bool:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            # Optionally raise custom exception
            return False

        if comment.user_id != user_id:
             # Optionally raise AccessDenied
             return False

        comment.is_deleted = True
        comment.content = None  # GDPR-friendly: truly delete content
        db.commit()
        return True
