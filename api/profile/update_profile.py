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
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        student = Student(user_id=current_user.id)
        db.add(student)

    if data.course is not None:
        student.course = data.course

    if data.college is not None:
        student.college = data.college

    if data.semester is not None:
        student.semester = data.semester
    if data.name is not None:
        student.name = data.name 

    db.commit()
    db.refresh(student)
    
    # Invalidate Cache
    from services.cache.redis_service import cache
    cache.delete(f"user_profile_static:{current_user.id}")

    # Resolve profile URL for chat sync
    profile_url_signed = ""
    if student.profile_url:
        if student.profile_url.startswith("http"):
             profile_url_signed = student.profile_url
        else:
            try:
                from services.storage.factory import StorageFactory
                storage = StorageFactory.get_storage()
                profile_url_signed = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                profile_url_signed = ""

    # Sync to Chat
    sync_data = {
        "email": current_user.email,
        "fullName": student.name or current_user.email.split('@')[0],
        "postgresId": str(current_user.id),
        "profilePic": profile_url_signed,
        "bio": "" 
    }
    background_tasks.add_task(sync_user_to_chat, sync_data)

    return {
        "message": "Profile details updated successfully"
    }
