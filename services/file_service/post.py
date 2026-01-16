from sqlalchemy.orm import Session
from models.document import Document
from models.user import User


class CreatePostService:
    @staticmethod
    def create_post(
        *,
        db: Session,
        user: User,
        title: str,
        content: str,
        visibility: str,
    ) -> Document:

        if not content.strip():
            raise ValueError("Post content cannot be empty")

        post = Document(
            user_id=user.id,
            title=title,
            doc_type="post",
            content=content,
            content_type="text/plain",
            object_key=None,
            visibility=visibility,
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        return post

