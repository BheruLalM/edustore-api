from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.student import Student
from db.deps import get_db
from dependencies.get_current_user import get_current_user
from api.profile.schema import profile_update
from models.user import User
from api.profile.schema import ProfileResponse
from services.storage.factory import StorageFactory

router = APIRouter(prefix="/profile", tags=["Profile"])



@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from models.follow import Follow
    
    student = (
        db.query(Student)
        .filter(Student.user_id == current_user.id)
        .first()
    )

    # Get follower and following counts
    followers_count = db.query(Follow).filter(Follow.following_id == current_user.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == current_user.id).count()

    # Handle profile_url (it might be a key or a legacy full URL)
    profile_url = None
    if student and student.profile_url:
        if student.profile_url.startswith("http"):
            profile_url = student.profile_url
        else:
            try:
                storage = StorageFactory.get_storage()
                profile_url = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                profile_url = None

    profile_data = {
        "user_id": current_user.id,
        "email": current_user.email,
        "name": student.name if student else None,
        "college": student.college if student else None,
        "course": student.course if student else None,
        "semester": student.semester if student else None,
        "profile_url": profile_url,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_student": student is not None,
    }
    return ProfileResponse(**profile_data)