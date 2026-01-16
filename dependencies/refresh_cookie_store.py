import secrets
from core.redis import redis_client
from core.config import mail_setting

REFRESH_TOKEN_TTL = mail_setting.REFRESH_TOKEN_EXPIRE_DAYS * 86400
  


def store_refresh_token(user_id: int) -> str:
    token_id = secrets.token_hex(16)
    key = f"refresh:{user_id}:{token_id}"
    redis_client.setex(key, REFRESH_TOKEN_TTL, 1)
    return token_id


def is_refresh_token_valid(user_id: int, token_id: str) -> bool:
    return redis_client.exists(f"refresh:{user_id}:{token_id}") == 1


def revoke_refresh_token(user_id: int, token_id: str) -> None:
    redis_client.delete(f"refresh:{user_id}:{token_id}")
