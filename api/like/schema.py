from pydantic import BaseModel
from datetime import datetime
from typing import List


class LikeToggleResponse(BaseModel):
    document_id: int
    is_liked: bool
    like_count: int


class LikeUser(BaseModel):
    id: int
    name: str | None = None


class LikeItem(BaseModel):
    user: LikeUser
    liked_at: datetime


class LikeListResponse(BaseModel):
    items: List[LikeItem]
    total: int


class LikeCountResponse(BaseModel):
    document_id: int
    like_count: int
    is_liked: bool
