from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.deps import get_db
from models.follow import Follow
from models.user import User
from models.student import Student
from dependencies.get_current_user import get_current_user
from services.storage.factory import StorageFactory

router = APIRouter(prefix="/users", tags=["Follow"])


@router.get("/{id}/following")
def my_following(
    id : int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import time
    start_time = time.time()
    
    limit = min(limit, 50) # Enforce max limit

    # Optimize query to select only needed fields
    follows = (
        db.query(
            Follow.created_at,
            User.id,
            User.email,
            Student.name,
            Student.profile_url
        )
        .join(User, Follow.following_id == User.id)
        .outerjoin(Student, Student.user_id == User.id)
        .filter(Follow.follower_id == id)
        .order_by(Follow.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    # ✅ OPTIMIZED: Use cached URL helper
    from services.storage.url_cache import StorageURLCache
    
    result = []
    for created_at, user_id, email, name, profile_url_key in follows:
        # ✅ Cached avatar URL lookup (no storage API call if cached)
        profile_url = StorageURLCache.get_avatar_url(profile_url_key)

        result.append({
            "user_id": user_id,
            "email": email,
            "name": name,
            "profile_url": profile_url,
            "followed_at": created_at,
        })

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{id}/following completed in {elapsed:.3f}s (limit={limit}, offset={offset})")

    return result


@router.get("/{id}/followers")
def my_followers(
    id : int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import time
    start_time = time.time()

    limit = min(limit, 50)

    follows = (
        db.query(
            Follow.created_at,
            User.id,
            User.email,
            Student.name,
            Student.profile_url
        )
        .join(User, Follow.follower_id == User.id)
        .outerjoin(Student, Student.user_id == User.id)
        .filter(Follow.following_id == id)
        .order_by(Follow.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    # ✅ OPTIMIZED: Use cached URL helper
    from services.storage.url_cache import StorageURLCache
    
    result = []
    for created_at, user_id, email, name, profile_url_key in follows:
        # ✅ Cached avatar URL lookup (no storage API call if cached)
        profile_url = StorageURLCache.get_avatar_url(profile_url_key)

        result.append({
            "user_id": user_id,
            "email": email,
            "name": name,
            "profile_url": profile_url,
            "followed_at": created_at,
        })

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{id}/followers completed in {elapsed:.3f}s (limit={limit}, offset={offset})")

    return result
