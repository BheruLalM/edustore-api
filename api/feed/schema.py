from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentFeedItem(BaseModel):
    id: int
    title: str
    doc_type: str
    file_size: Optional[int] 
    created_at: datetime
    owner_id: int
    owner_name: Optional[str] = None
    owner_avatar: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    comment_count: int = 0
    like_count: int = 0
    is_liked: bool = False
    is_bookmarked: bool = False

    class Config:
        from_attributes = True
