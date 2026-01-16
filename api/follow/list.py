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
    from services.cache.redis_service import cache
    start_time = time.time()
    
    limit = min(limit, 50)

    # 1. Try CACHE
    cache_key = f"user:following:{id}:p{offset}:l{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        elapsed = time.time() - start_time
        print(f"⚡ Following Cache HIT: {cache_key} ({elapsed:.3f}s)")
        return cached_data

    # 2. DB Query
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

    from services.storage.url_cache import StorageURLCache
    
    result = []
    for created_at, user_id, email, name, profile_url_key in follows:
        profile_url = StorageURLCache.get_avatar_url(profile_url_key)
        result.append({
            "user_id": user_id,
            "email": email,
            "name": name,
            "profile_url": profile_url,
            "followed_at": created_at,
        })

    # 3. Cache for 60s
    cache.set(cache_key, result, ttl=60)

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{id}/following completed in {elapsed:.3f}s (limit={limit}, offset={offset}) [MISS]")

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
    from services.cache.redis_service import cache
    start_time = time.time()

    limit = min(limit, 50)

    # 1. Try CACHE
    cache_key = f"user:followers:{id}:p{offset}:l{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        elapsed = time.time() - start_time
        print(f"⚡ Followers Cache HIT: {cache_key} ({elapsed:.3f}s)")
        return cached_data

    # 2. DB Query
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

    from services.storage.url_cache import StorageURLCache
    
    result = []
    for created_at, user_id, email, name, profile_url_key in follows:
        profile_url = StorageURLCache.get_avatar_url(profile_url_key)
        result.append({
            "user_id": user_id,
            "email": email,
            "name": name,
            "profile_url": profile_url,
            "followed_at": created_at,
        })

    # 3. Cache for 60s
    cache.set(cache_key, result, ttl=60)

    elapsed = time.time() - start_time
    print(f"⏱️  GET /users/{id}/followers completed in {elapsed:.3f}s (limit={limit}, offset={offset}) [MISS]")

    return result
