from core.config import redis_setting
import redis

redis_client = redis.Redis(
    host=redis_setting.REDIS_HOST,
    port=redis_setting.REDIS_PORT,
    db = redis_setting.REDIS_DB,
    decode_responses= True
)
redis_client.ping()