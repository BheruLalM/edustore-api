# api/bookmark/schema.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ToggleResponse(BaseModel):
    document_id: int
    is_bookmarked: bool


class BookmarkItem(BaseModel):
    id: int
    title: str
    doc_type: str
    visibility: str
    owner_id: int
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_avatar: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    bookmarked_at: datetime
    like_count: int = 0
    is_liked: bool = False
    is_bookmarked: bool = True
    comment_count: int = 0


class BookmarkListResponse(BaseModel):
    items: List[BookmarkItem]
    total: int


class BookmarkStatusResponse(BaseModel):
    document_id: int
    is_bookmarked: bool
