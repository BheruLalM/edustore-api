def _validate_avatar_key(*, object_key: str, user_id: int) -> None:
    if not object_key:
        raise ValueError("object_key required")

    if object_key.startswith("/") or ".." in object_key:
        raise ValueError("invalid object_key")

    expected_prefix = f"users/{user_id}/profile/"
    if not object_key.startswith(expected_prefix):
        raise ValueError("object_key does not belong to user")

def _validate_document_key(*, object_key: str, user_id: int) -> None:
    if not object_key:
        raise ValueError("object_key required")
    if object_key.startswith("/") or ".." in object_key:
        raise ValueError("invalid object_key")
    expected_prefix = f"users/{user_id}/documents/"
    if not object_key.startswith(expected_prefix):
        raise ValueError("object_key does not belong to user's documents")
