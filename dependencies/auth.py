from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError

from services.auth.jwt import decode_token


def get_token_payload(token: str) -> dict:
    try:
        return decode_token(token)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
        
def require_access_token(payload: dict):
    if payload.get("typ") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )