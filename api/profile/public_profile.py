from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.student import Student
from models.user import User
from db.deps import get_db
from api.profile.schema import ProfileResponse
from services.storage.factory import StorageFactory
from services.cache.redis_service import cache

router = APIRouter(prefix="/users", tags=["Profile"])

from models.follow import Follow
from dependencies.get_current_user import get_current_user_optional

@router.get("/{user_id}/profile", response_model=ProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Get public profile of any user by their ID - OPTIMIZED"""
    import time
    start_time = time.time()
    
    # 1. Try to get STATIC profile data from cache
    cache_key = f"user_profile_static:{user_id}"
    profile_data = cache.get(cache_key)

    if not profile_data:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Get student info
        student = (
            db.query(Student)
            .filter(Student.user_id == user_id)
            .first()
        )

        # Generate avatar URL using cache service (handles defaults and signing)
        from services.storage.url_cache import StorageURLCache
        profile_url = StorageURLCache.get_avatar_url(student.profile_url if student else None)

        # OPTIMIZED: Get follower and following counts in single query
        from sqlalchemy import func, case
        
        counts = db.query(
            func.sum(case((Follow.following_id == user_id, 1), else_=0)).label('followers'),
            func.sum(case((Follow.follower_id == user_id, 1), else_=0)).label('following')
        ).filter(
            (Follow.following_id == user_id) | (Follow.follower_id == user_id)
        ).first()
        
        followers_count = int(counts.followers or 0)
        following_count = int(counts.following or 0)
        
        profile_data = {
            "user_id": user.id,
            "email": user.email,
            "name": student.name if student else None,
            "college": student.college if student else None,
            "course": student.course if student else None,
            "semester": student.semester if student else None,
            "profile_url": profile_url,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_student": student is not None,
        }
        
        # Cache STATIC data for 5 minutes
        cache.set(cache_key, profile_data, ttl=300)

    # 2. Add DYNAMIC (user-specific) data
    # Check if current user follows this profile
    is_following = False
    if current_user and current_user.id != user_id:
        from services.cache.user_state import UserStateCache
        following_ids = UserStateCache.get_following_ids(db, current_user.id)
        is_following = user_id in following_ids

    # Merge dynamic data
    final_response = profile_data.copy()
    final_response["is_following"] = is_following
    
    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{user_id}/profile completed in {elapsed:.3f}s")
    
    return ProfileResponse(**final_response)
