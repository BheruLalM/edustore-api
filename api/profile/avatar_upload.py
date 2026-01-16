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


@router.post("/avatar/upload")
async def upload_avatar(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload user avatar image to Supabase storage"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )
    
    # Generate unique filename
    timestamp = int(time.time())
    object_key = f"avatars/{current_user.id}_{timestamp}{file_ext}"
    
    try:
        # Upload to Supabase storage
        storage = StorageFactory.get_storage()
        storage.upload_file(
            object_key=object_key,
            file_content=content,
            content_type=file.content_type,
        )
        
        # Generate public URL
        avatar_url = storage.generate_download_url(
            object_key=object_key,
            expires_in=31536000,  # 1 year
        )
        
        # Update student profile with new avatar URL
        student = db.query(Student).filter(
            Student.user_id == current_user.id
        ).first()
        
        if not student:
            student = Student(user_id=current_user.id)
            db.add(student)
        
        # STORE THE OBJECT KEY, NOT THE SIGNED URL
        student.profile_url = object_key
        db.commit()
        db.refresh(student)
        
        # Invalidate Cache
        from services.cache.redis_service import cache
        cache.delete(f"user_profile_static:{current_user.id}")
        
        # Sync to Chat
        sync_data = {
            "email": current_user.email,
            "fullName": student.name or current_user.email.split('@')[0],
            "postgresId": str(current_user.id),
            "profilePic": avatar_url,
            "bio": "" 
        }
        background_tasks.add_task(sync_user_to_chat, sync_data)
        
        return {
            "message": "Avatar uploaded successfully",
            "profile_url": avatar_url,
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}",
        )
