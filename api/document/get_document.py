from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.storage.factory import StorageFactory
from core.exceptions import DocumentNotFound,DownloadUrlGenerationFailed,DocumentAccessDenied
from models.document import Document
from models.user import User
from db.deps import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter(prefix="/documents", tags=["Document"])


@router.get("/")
def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from models.student import Student
    
    # Query Document and Student to get full details for the current user
    results = (
        db.query(Document, Student)
        .outerjoin(Student, Student.user_id == Document.user_id)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    storage = StorageFactory.get_storage()
    response_data = []

    for d, student in results:
        owner_avatar = None
        if student and student.profile_url:
            try:
                owner_avatar = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                pass

        # Calculate Like Count
        from models.likes import Like
        like_count = db.query(Like).filter(Like.document_id == d.id).count()

        # Check if Liked by Current User
        is_liked = (
            db.query(Like)
            .filter(Like.document_id == d.id, Like.user_id == current_user.id)
            .first()
            is not None
        )

        response_data.append({
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "visibility": d.visibility,
            "file_size": d.file_size,
            "content": d.content,
            "created_at": d.created_at,
            "owner_id": d.user_id,
            "owner_name": student.name if student else None,
            "owner_email": current_user.email,
            "owner_avatar": owner_avatar,
            "like_count": like_count,
            "is_liked": is_liked,
            "is_owner": True, # Always true for this endpoint
        })

    return response_data






@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
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

    # 🔒 Access control
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
