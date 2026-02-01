from services.cache.redis_service import cache

class CacheManager:
    """Centralized cache invalidation logic"""
    
    @staticmethod
    def invalidate_feed():
        """Clear all feed caches"""
        cache.delete_pattern("feed:*")
        print("🧹 All feed caches invalidated")

    @staticmethod
    def invalidate_user_docs(user_id: int):
        """Clear document list for a specific user"""
        cache.delete_pattern(f"user:docs:{user_id}:*")
        print(f"🧹 User {user_id} docs cache invalidated")

    @staticmethod
    def invalidate_document(document_id: int, owner_id: int = None, current_user_id: int = None):
        """Clear document detail and related lists"""
        # 1. Document Detail
        cache.delete(f"doc:detail:static:{document_id}")
        
        # 2. Public Feeds (Global)
        cache.delete_pattern("feed:*")
        
        # 3. Owner's Document List (Profile)
        if owner_id:
            cache.delete_pattern(f"user:docs:{owner_id}:*")
            
        # 4. Current User's Bookmarks (If they interact, status might update)
        if current_user_id:
            cache.delete_pattern(f"user:bookmarks:{current_user_id}:*")
            
        print(f"🧹 Document {document_id} cache invalidated (Owner: {owner_id}, Actor: {current_user_id})")

    @staticmethod
    def invalidate_profile(user_id: int):
        """Clear profile cache"""
        cache.delete(f"user_profile_static:{user_id}")
        print(f"🧹 User {user_id} profile cache invalidated")

    @staticmethod
    def invalidate_user_bookmarks(user_id: int):
        """Clear bookmarks cache for a specific user"""
        cache.delete_pattern(f"user:bookmarks:{user_id}:*")
        print(f"🧹 User {user_id} bookmarks cache invalidated")
