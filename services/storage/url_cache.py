"""
Storage URL Caching Service
Caches avatar and file URLs to avoid repeated storage API calls
"""
from services.cache.redis_service import cache
from services.storage.factory import StorageFactory


class StorageURLCache:
    """Centralized caching for storage URLs"""
    
    @staticmethod
    def get_avatar_url(object_key: str | None) -> str | None:
        """
        Get avatar URL with Redis caching
        
        Args:
            object_key: Storage object key or full URL
            
        Returns:
            Signed URL or None if not found
        """
        if not object_key:
            return None
            
        # If already a full URL, return as-is
        if object_key.startswith("http"):
            return object_key
        
        # Check cache first
        cache_key = f"avatar_url:{object_key}"
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url
        
        # Generate new URL
        try:
            storage = StorageFactory.get_storage()
            avatar_url = storage.generate_download_url(
                object_key=object_key,
                expires_in=31536000,  # 1 year (avatars don't change often)
            )
            # Cache for 1 hour
            cache.set(cache_key, avatar_url, ttl=3600)
            return avatar_url
        except Exception:
            return None
    
    @staticmethod
    def get_file_url(object_key: str | None, expires_in: int = 3600) -> str | None:
        """
        Get file URL with caching
        
        Args:
            object_key: Storage object key
            expires_in: URL expiry time in seconds
            
        Returns:
            Signed URL or None if not found
        """
        if not object_key:
            return None
        
        # Files expire faster, so use shorter cache with expiry in key
        cache_key = f"file_url:{object_key}:{expires_in}"
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url
        
        try:
            storage = StorageFactory.get_storage()
            file_url = storage.generate_download_url(
                object_key=object_key,
                expires_in=expires_in,
            )
            # Cache for half the expiry time to be safe
            cache.set(cache_key, file_url, ttl=expires_in // 2)
            return file_url
        except Exception:
            return None
    
    @staticmethod
    def invalidate_avatar(object_key: str) -> None:
        """Invalidate cached avatar URL (e.g., after profile update)"""
        cache_key = f"avatar_url:{object_key}"
        cache.delete(cache_key)
    
    @staticmethod
    def invalidate_file(object_key: str) -> None:
        """Invalidate all cached file URLs for a given object"""
        # Delete all variations with different expiry times
        pattern = f"file_url:{object_key}:*"
        # Note: This requires Redis SCAN, implement if needed
        # For now, just delete common expiry times
        for expires_in in [300, 600, 3600, 7200]:
            cache_key = f"file_url:{object_key}:{expires_in}"
            cache.delete(cache_key)
