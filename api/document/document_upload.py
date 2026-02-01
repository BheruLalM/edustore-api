from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.exceptions import (
    StorageOperationFailed,
    DocumentNotFound,
    DocumentOwnershipError,
    DownloadUrlGenerationFailed,
)
from models.user import User
from models.document import Document
from dependencies.get_current_user import get_current_user
from dependencies.helper import _validate_document_key
from services.storage.factory import StorageFactory
from services.storage.keys import document_upload_key
from api.document.schema import (
    DocumentUploadRequest,
    DocumentCommitRequest,
    DocumentResponse,
)
from dependencies.content_type import _extension_from_document_content_type
from db.deps import get_db

router = APIRouter(prefix="/documents", tags=["Document"])


# -------------------- Direct Upload (Cloudinary) --------------------
@router.post("/upload", response_model=DocumentResponse)
async def upload_document_direct(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form(...),
    visibility: str = Form("public"),
    content: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Direct upload endpoint for Cloudinary - uploads file and creates document in one step"""
    try:
        # 0. Size Validation (20MB)
        MAX_DOCUMENT_SIZE = 20 * 1024 * 1024
        
        # Check Content-Length header first for optimization
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_DOCUMENT_SIZE:
             raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Document size exceeds 20 MB limit",
            )
            
        # Generate object key
        extension = _extension_from_document_content_type(file.content_type)
        object_key = document_upload_key(
            user_id=current_user.id,
            extension=extension,
        )
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary
        storage = StorageFactory.get_storage()
        storage.upload_file(
            object_key=object_key,
            file_content=file_content,
            content_type=file.content_type,
        )
        
        # Generate download URL
        download_url = storage.generate_download_url(
            object_key=object_key,
            expires_in=300,
        )
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            title=title,
            doc_type=doc_type,
            object_key=object_key,
            original_filename=file.filename,
            content_type=file.content_type,
            file_size=len(file_content),
            visibility=visibility,
            content=content,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return DocumentResponse.from_orm(document).copy(
            update={"doc_url": download_url}
        )
        
    except Exception as e:
        db.rollback()
        raise StorageOperationFailed(f"Upload failed: {str(e)}")


# -------------------- Upload URL --------------------
@router.post("/upload-url")
def upload_document_url(
    data: DocumentUploadRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        extension = _extension_from_document_content_type(data.content_type)
        object_key = document_upload_key(
            user_id=current_user.id,
            extension=extension,
        )

        storage = StorageFactory.get_storage()
        upload_url = storage.generate_upload_url(
            object_key=object_key,
            content_type=data.content_type,
            expires_in=300,
        )

        return {
            "upload_url": upload_url,
            "object_key": object_key,
        }

    except ValueError as e:
        raise StorageOperationFailed(str(e))


# -------------------- Commit Document --------------------
@router.post("/commit", response_model=DocumentResponse)
def commit_document(
    data: DocumentCommitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1️⃣ Validate ownership
    try:
        _validate_document_key(
            object_key=data.object_key,
            user_id=current_user.id,
        )
    except ValueError:
        raise DocumentOwnershipError()

    storage = StorageFactory.get_storage()

    # 2️⃣ Idempotency check
    existing = (
        db.query(Document)
        .filter(
            Document.object_key == data.object_key,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if existing:
        download_url = storage.generate_download_url(
            object_key=existing.object_key,
            expires_in=300,
        )
        return DocumentResponse.from_orm(existing).copy(
            update={"doc_url": download_url}
        )

    # 3️⃣ Validate object exists in storage
    try:
        download_url = storage.generate_download_url(
            object_key=data.object_key,
            expires_in=300,
        )
    except Exception:
        raise DownloadUrlGenerationFailed()

    document = Document(
    user_id=current_user.id,
    title=data.title,
    doc_type=data.doc_type,
    object_key=data.object_key,
    original_filename=data.original_filename,
    content_type=data.content_type,
    file_size=data.file_size,
    visibility=data.visibility,
    content=data.content, 
)

    from services.cache.cache_manager import CacheManager
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Invalidate caches
        CacheManager.invalidate_user_docs(current_user.id)
        CacheManager.invalidate_feed()
    except IntegrityError:
        db.rollback()
        raise StorageOperationFailed("Document already committed")

    return DocumentResponse.from_orm(document).copy(
        update={"doc_url": download_url}
    )


# -------------------- Delete Document --------------------
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if not document:
        raise DocumentNotFound()

    # soft delete
    document.is_deleted = True
    db.commit()

    from services.cache.cache_manager import CacheManager
    CacheManager.invalidate_document(document_id)
    CacheManager.invalidate_user_docs(current_user.id)

    # optional: async/background cleanup
    try:
        storage = StorageFactory.get_storage()
        storage.delete_object(document.object_key)
    except Exception:
        pass

    return {"message": "Document deleted successfully"}
