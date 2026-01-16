from fastapi import APIRouter, Response, Request
from dependencies.refresh_cookie_store import revoke_refresh_token
from dependencies.auth import get_token_payload
from core.exceptions import DomainError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/logout")
def logout(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        # No token, but logout can still succeed 
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return {"message": "Logged out successfully"}

    try:
        payload = get_token_payload(refresh_token)
        user_id = int(payload["sub"])
        refresh_token_id = payload["jti"]
    except Exception:
        payload = None

    if payload:
        revoke_refresh_token(user_id, refresh_token_id)

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return {"message": "Logged out successfully"}
