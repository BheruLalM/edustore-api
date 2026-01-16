import redis
from typing import Any, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    _instance = None
    _client = None
    _connection_attempted = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None and not self._connection_attempted:
            self._connection_attempted = True
            try:
                self._client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0)),
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self._client.ping()
                print("✅ Redis connected - caching enabled")
            except:
                # Silently disable caching if Redis is not available
                self._client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._client:
            return None
        
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL in seconds"""
        if not self._client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._client:
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern"""
        if not self._client:
            return False
        
        try:
            keys = self._client.keys(pattern)
            if keys:
                self._client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis delete pattern error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._client:
            return False
        
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

# Singleton instance
cache = RedisService()
