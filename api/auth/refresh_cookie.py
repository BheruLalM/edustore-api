from fastapi import APIRouter, Response, Request
from jose import JWTError
from core.exceptions import DomainError
from dependencies.rotate_refresh_token import rotate_refresh_token
from services.auth.jwt import create_access_token, create_refresh_token
from dependencies.auth import get_token_payload
from dependencies.refresh_cookie_store import is_refresh_token_valid
<<<<<<< HEAD
from core.config import mail_setting
=======
from core.config import mail_setting, app_settings
>>>>>>> 5cfc842 (new version of it)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/refresh")
def refresh_session(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise DomainError("Not Authenticated")

    try:
        payload = get_token_payload(refresh_token)
    except JWTError:
        raise DomainError("Invalid refresh token")

    if payload.get("typ") != "refresh":
        raise DomainError("Wrong token type")

    user_id = int(payload["sub"])
    refresh_token_id = payload["jti"]

    if not is_refresh_token_valid(user_id, refresh_token_id):
        raise DomainError("Session expired")

    new_refresh_token_id = rotate_refresh_token(user_id, refresh_token_id)

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id, new_refresh_token_id)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
<<<<<<< HEAD
        secure=False,
        samesite="strict",
=======
        secure=app_settings.is_production,  # True in production, False in dev
        samesite="lax",  # Allow OAuth redirects
>>>>>>> 5cfc842 (new version of it)
        max_age=mail_setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
<<<<<<< HEAD
        secure=False,
        samesite="strict",
=======
        secure=app_settings.is_production,  # True in production, False in dev
        samesite="lax",  # Allow OAuth redirects
>>>>>>> 5cfc842 (new version of it)
        max_age=mail_setting.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {"message": "Session refreshed"}
