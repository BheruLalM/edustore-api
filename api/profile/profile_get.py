from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.student import Student
from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from api.profile.schema import ProfileResponse

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile - Optimized with caching"""
    from services.cache.redis_service import cache
    from services.storage.url_cache import StorageURLCache
    from models.follow import Follow
    from sqlalchemy import func, case
    
    # 1. Try Cache
    cache_key = f"user_profile_static:{current_user.id}"
    cached_profile = cache.get(cache_key)
    if cached_profile:
        # Ensure is_following is provided for schema if needed
        cached_profile["is_following"] = False
        return ProfileResponse(**cached_profile)

    # 2. Get student info
    student = (
        db.query(Student)
        .filter(Student.user_id == current_user.id)
        .first()
    )

    # 3. Optimized Count Query (Single trip)
    counts = db.query(
        func.sum(case((Follow.following_id == current_user.id, 1), else_=0)).label('followers'),
        func.sum(case((Follow.follower_id == current_user.id, 1), else_=0)).label('following')
    ).filter(
        (Follow.following_id == current_user.id) | (Follow.follower_id == current_user.id)
    ).first()
    
    followers_count = int(counts.followers or 0)
    following_count = int(counts.following or 0)

    # 4. Centralized Avatar Logic (Handles defaults)
    profile_url = StorageURLCache.get_avatar_url(student.profile_url if student else None)

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
    
    # 5. Cache for 5 minutes
    cache.set(cache_key, profile_data, ttl=300)
    
    profile_data["is_following"] = False
    
    return ProfileResponse(**profile_data)