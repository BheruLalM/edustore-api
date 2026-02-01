import secrets
from services.cache.redis_service import cache
from core.config import mail_setting

REFRESH_TOKEN_TTL = mail_setting.REFRESH_TOKEN_EXPIRE_DAYS * 86400
  

def store_refresh_token(user_id: int) -> str:
    token_id = secrets.token_hex(16)
    key = f"refresh:{user_id}:{token_id}"
    cache.set(key, 1, REFRESH_TOKEN_TTL)
    return token_id


def is_refresh_token_valid(user_id: int, token_id: str) -> bool:
    return cache.exists(f"refresh:{user_id}:{token_id}")


def revoke_refresh_token(user_id: int, token_id: str) -> None:
    cache.delete(f"refresh:{user_id}:{token_id}")
