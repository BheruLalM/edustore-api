from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import time
from pathlib import Path

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from models.student import Student
from services.storage.factory import StorageFactory
from services.chat.sync_service import sync_user_to_chat

router = APIRouter(prefix="/profile", tags=["Profile"])

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


from db.session import SessionLocal

async def _bg_upload_avatar(
    user_id: int,
    user_email: str,
    object_key: str,
    content: bytes,
    content_type: str,
):
    """Background task to upload avatar and update database"""
    db = SessionLocal()
    try:
        # 1. Upload to Cloudinary
        storage = StorageFactory.get_storage()
        avatar_url = storage.upload_file(
            object_key=object_key,
            file_content=content,
            content_type=content_type,
        )
        
        # 2. Update student profile
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            student = Student(user_id=user_id)
            db.add(student)
        
        student.profile_url = avatar_url
        db.commit()
        
        # 3. Invalidate Cache
        from services.cache.redis_service import cache
        cache.delete(f"user_profile_static:{user_id}")
        
        # 4. Sync to Chat
        sync_data = {
            "email": user_email,
            "fullName": student.name or user_email.split('@')[0],
            "postgresId": str(user_id),
            "profilePic": avatar_url,
            "bio": "" 
        }
        await sync_user_to_chat(sync_data)
        print(f"✅ Background avatar upload complete for user {user_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Background avatar upload failed for user {user_id}: {str(e)}")
    finally:
        db.close()


@router.post("/avatar/upload")
async def upload_avatar(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload user avatar image - Now Optimized with Background Tasks"""
    
    # 1. Faster Validation (extension only)
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # 2. Read content (necessary to pass to background)
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large (Max 5MB)",
        )
    
    # 3. Predict / Generate Key
    timestamp = int(time.time())
    object_key = f"avatars/{current_user.id}_{timestamp}{file_ext}"
    
    # 4. Offload heavy work to background
    background_tasks.add_task(
        _bg_upload_avatar,
        current_user.id,
        current_user.email,
        object_key,
        content,
        file.content_type
    )
    
    # 5. Instant Response
    return {
        "message": "Avatar upload started. Your profile will update in a few seconds.",
        "status": "processing",
        "predicted_key": object_key
    }
