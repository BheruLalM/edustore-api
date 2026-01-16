from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError

from core.config import mail_setting


ISSUER = "auth-service"
AUDIENCE = "auth-client"


def _now_ts() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp())


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "typ": "access",
        "iat": _now_ts(),
        "exp": _now_ts() + mail_setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    return jwt.encode(
        payload,
        mail_setting.SECRET_KEY,
        algorithm=mail_setting.ALGORITHM,
    )


def create_refresh_token(user_id: int, token_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "jti": token_id,
        "typ": "refresh",
        "iat": _now_ts(),
        "exp": _now_ts() + mail_setting.REFRESH_TOKEN_EXPIRE_DAYS* 86400 ,
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    return jwt.encode(payload, mail_setting.SECRET_KEY, algorithm=mail_setting.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        mail_setting.SECRET_KEY,
        algorithms=[mail_setting.ALGORITHM],
        audience=AUDIENCE,
        issuer=ISSUER,
    )
    

