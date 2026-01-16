from core.config import redis_setting
from upstash_redis import Redis

redis_client = None

if redis_setting.UPSTASH_REDIS_REST_URL and redis_setting.UPSTASH_REDIS_REST_TOKEN:
    try:
        redis_client = Redis(
            url=redis_setting.UPSTASH_REDIS_REST_URL,
            token=redis_setting.UPSTASH_REDIS_REST_TOKEN
        )
        redis_client.ping()
    except Exception:
        redis_client = None