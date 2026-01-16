from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from models.student import Student
from db.deps import get_db
from dependencies.get_current_user import get_current_user
from api.profile.schema import profile_update
from models.user import User
from services.chat.sync_service import sync_user_to_chat


router = APIRouter(prefix="/profile", tags=["Profile"])


@router.patch("/update")
def update_profile_details(
    data: profile_update,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile details - Optimized with background sync"""
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        student = Student(user_id=current_user.id)
        db.add(student)

    # 1. Update fields
    update_sync_needed = False
    if data.course is not None: student.course = data.course; update_sync_needed = True
    if data.college is not None: student.college = data.college; update_sync_needed = True
    if data.semester is not None: student.semester = data.semester; update_sync_needed = True
    if data.name is not None: student.name = data.name; update_sync_needed = True

    db.commit()
    db.refresh(student)
    
    # 2. Invalidate Profile Cache
    from services.cache.redis_service import cache
    cache.delete(f"user_profile_static:{current_user.id}")

    # 3. Offload Chat Sync & URL Signing to Background
    if update_sync_needed:
        background_tasks.add_task(
            _bg_sync_profile_to_chat,
            current_user.id,
            current_user.email,
            student.name,
            student.profile_url
        )

    return {
        "message": "Profile details updated successfully",
        "status": "success"
    }

async def _bg_sync_profile_to_chat(user_id: int, email: str, name: str, profile_url: str):
    """Helper to handle signing and syncing in background"""
    from services.storage.url_cache import StorageURLCache
    
    # Use the centralized helper which handles defaults and caching
    final_profile_url = StorageURLCache.get_avatar_url(profile_url)
    
    sync_data = {
        "email": email,
        "fullName": name or email.split('@')[0],
        "postgresId": str(user_id),
        "profilePic": final_profile_url,
        "bio": "" 
    }
    await sync_user_to_chat(sync_data)
