import hmac
import hashlib
import secrets

from core.redis import redis_client
from core.exceptions import RedisUploadFailed, RedisFetchFailed,OTPCooldownActive
from core.config import mail_setting


OTP_TTL = 300
OTP_COOLDOWN = 60
MAX_ATTEMPTS = 5
SECRET_KEY = mail_setting.SECRET_KEY


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def otp_generator() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def hash_otp(otp: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def save_otp(email: str, otp: str) -> None:
    email = _normalize_email(email)

    otp_key = f"otp:{email}"
    attempt_key = f"otp:attempt:{email}"
    cooldown_key = f"otp:cooldown:{email}"

    try:
        cooldown_set = redis_client.set(
            cooldown_key,
            1,
            ex=OTP_COOLDOWN,
            nx=True
        )

        if not cooldown_set:
            raise OTPCooldownActive()

        hashed_otp = hash_otp(otp)

        redis_client.setex(otp_key, OTP_TTL, hashed_otp)
        redis_client.setex(attempt_key, OTP_TTL, 0)

    except OTPCooldownActive:
        raise

    except Exception as e:
        raise RedisUploadFailed("Failed to save OTP") from e


def verify_otp(email: str, user_otp: str) -> bool:
    email = _normalize_email(email)

    otp_key = f"otp:{email}"
    attempt_key = f"otp:attempt:{email}"

    try:
        attempts = redis_client.get(attempt_key)
        if attempts is not None and int(attempts) >= MAX_ATTEMPTS:
            return False

        stored_hash = redis_client.get(otp_key)
        if stored_hash is None:
            return False

        user_hash = hash_otp(user_otp)

        if hmac.compare_digest(stored_hash, user_hash):
            redis_client.delete(otp_key)
            redis_client.delete(attempt_key)
            redis_client.delete(f"otp:cooldown:{email}")  # Clear cooldown on success
            return True

        redis_client.incr(attempt_key)
        return False

    except Exception as e:
        raise RedisFetchFailed("OTP verification failed") from e
    
def invalidate_otp(email: str) -> None:
    email = _normalize_email(email)

    otp_key = f"otp:{email}"
    attempt_key = f"otp:attempt:{email}"

    try:
        redis_client.delete(otp_key)
        redis_client.delete(attempt_key)
    except Exception:
        pass