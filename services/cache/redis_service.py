from upstash_redis import Redis
from typing import Any, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

from core.config import redis_setting

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
                url = redis_setting.UPSTASH_REDIS_REST_URL
                token = redis_setting.UPSTASH_REDIS_REST_TOKEN
                
                if url and token:
                    self._client = Redis(url=url, token=token)
                    # Test connection
                    self._client.ping()
                    print("✅ Upstash Redis connected - caching enabled")
                else:
                    print("⚠️  Upstash Redis credentials missing - caching disabled")
                    self._client = None
            except Exception as e:
                print(f"❌ Upstash Redis connection error: {e}")
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
