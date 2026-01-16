

def _extension_from_content_type(content_type: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
    }

    if content_type not in mapping:
        raise ValueError("unsupported content type")

    return mapping[content_type]

def _extension_from_document_content_type(content_type: str) -> str:
    mapping = {
        "application/pdf": "pdf",
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "text/plain": "txt",
    }

    if content_type not in mapping:
        raise ValueError("unsupported document content type")

    return mapping[content_type]
