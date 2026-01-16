from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from models.follow import Follow
from models.user import User
from dependencies.get_current_user import get_current_user
from services.cache.redis_service import cache

router = APIRouter(prefix="/users", tags=["Follow"])


@router.get("/{user_id}/follow-status")
def get_follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if current user is following the specified user"""
    # Try cache first
    cache_key = f"follow_status:{user_id}:{current_user.id}"
    cached_status = cache.get(cache_key)
    if cached_status:
        return cached_status
    
    is_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    ).first() is not None
    
    # Get follower and following counts
    follower_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    
    status_data = {
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count,
    }
    
    # Cache for 2 minutes
    cache.set(cache_key, status_data, ttl=120)
    
    return status_data
