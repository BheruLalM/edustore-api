from sqlalchemy.orm import Session
from models.document import Document
from models.user import User
from services.storage.factory import StorageFactory
from core.exceptions import (
    DocumentNotFound,
    DocumentAccessDenied,
    DownloadUrlGenerationFailed,
)


class DownloadService:
    @staticmethod
    def generate_download_url(
        *,
        db: Session,
        document_id: int,
        current_user: User | None,
    ) -> dict:

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.is_deleted.is_(False),
            )
            .first()
        )

        if not document:
            raise DocumentNotFound()

        if document.visibility == "private":
            if not current_user or document.user_id != current_user.id:
                raise DocumentAccessDenied()

        storage = StorageFactory.get_storage()

        try:
            download_url = storage.generate_download_url(
                object_key=document.object_key,
                expires_in=300,
            )
        except Exception:
            raise DownloadUrlGenerationFailed()

        return {
            "download_url": download_url,
            "expires_in": 300,
            "document_id": document.id,
            "filename": document.original_filename,
            "content_type": document.content_type,
        }
