from uuid import uuid4


BASE = "users"
DOCS = "documents"


def document_upload_key(*, user_id, extension: str | None = None) -> str:
    user_id = int(user_id)
    uid = uuid4().hex

    if extension:
        extension = extension.lstrip(".")
        return f"{BASE}/{user_id}/{DOCS}/{uid}.{extension}"

    return f"{BASE}/{user_id}/{DOCS}/{uid}"


PROFILE = "profile"


def profile_avatar_key(*, user_id: int, extension: str) -> str:
    uid = uuid4().hex
    extension = extension.lstrip(".")
    return f"{BASE}/{user_id}/{PROFILE}/{uid}.{extension}"

