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
    def invalidate_document(document_id: int):
        """Clear document detail cache"""
        cache.delete(f"doc:detail:static:{document_id}")
        cache.delete_pattern("feed:*") # Counts might have changed globally
        print(f"🧹 Document {document_id} cache invalidated")

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
