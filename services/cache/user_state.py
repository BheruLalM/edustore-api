from typing import Set
from services.cache.redis_service import cache
from sqlalchemy.orm import Session
from models.likes import Like
from models.bookmark import Bookmark
from models.follow import Follow

class UserStateCache:
    """
    Manages Redis SETS for user-specific interactions to avoid redundant DB checks.
    Keys:
        user:following:{user_id} -> Set of following user IDs
        user:likes:{user_id}     -> Set of liked document IDs
        user:bookmarks:{user_id} -> Set of bookmarked document IDs
    """

    @staticmethod
    def get_following_ids(db: Session, user_id: int) -> Set[int]:
        if not user_id: return set()
        key = f"user:following:{user_id}"
        
        if cache._client:
            try:
                ids = cache._client.smembers(key)
                if ids:
                    return {int(i) for i in ids if int(i) != -1}
            except Exception:
                pass
        
        query_results = db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()
        id_set = {r[0] for r in query_results}
        
        if cache._client:
            try:
                if id_set:
                    cache._client.sadd(key, *id_set)
                else:
                    cache._client.sadd(key, -1)
                cache._client.expire(key, 3600)
            except Exception:
                pass
        return id_set

    @staticmethod
    def get_liked_ids(db: Session, user_id: int) -> Set[int]:
        if not user_id: return set()
        key = f"user:likes:{user_id}"
        
        if cache._client:
            try:
                ids = cache._client.smembers(key)
                if ids:
                    return {int(i) for i in ids if int(i) != -1}
            except Exception:
                pass
        
        query_results = db.query(Like.document_id).filter(Like.user_id == user_id).all()
        id_set = {r[0] for r in query_results}
        
        if cache._client:
            try:
                if id_set:
                    cache._client.sadd(key, *id_set)
                else:
                    cache._client.sadd(key, -1)
                cache._client.expire(key, 3600)
            except Exception:
                pass
        return id_set

    @staticmethod
    def get_bookmarked_ids(db: Session, user_id: int) -> Set[int]:
        if not user_id: return set()
        key = f"user:bookmarks:{user_id}"
        
        if cache._client:
            try:
                ids = cache._client.smembers(key)
                if ids:
                    return {int(i) for i in ids if int(i) != -1}
            except Exception:
                pass
        
        query_results = db.query(Bookmark.document_id).filter(Bookmark.user_id == user_id).all()
        id_set = {r[0] for r in query_results}
        
        if cache._client:
            try:
                if id_set:
                    cache._client.sadd(key, *id_set)
                else:
                    cache._client.sadd(key, -1)
                cache._client.expire(key, 3600)
            except Exception:
                pass
        return id_set

    @staticmethod
    def clear_user_state(user_id: int):
        if cache._client:
            try:
                cache._client.delete(
                    f"user:following:{user_id}",
                    f"user:likes:{user_id}",
                    f"user:bookmarks:{user_id}"
                )
            except Exception:
                pass
