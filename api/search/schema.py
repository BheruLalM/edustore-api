from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, example="machine learning")
    limit: int = Field(20, ge=1, le=50)
    offset: int = Field(0, ge=0)


class DocumentSearchItem(BaseModel):
    id: int
    title: str
    doc_type: str
    file_size: int | None
    visibility: str
    owner_id: int
    created_at: datetime
    owner_name: Optional[str] = None
    owner_avatar: Optional[str] = None
    comment_count: int = 0
    like_count: int = 0
    is_liked: bool = False
    is_bookmarked: bool = False


class DocumentSearchResponse(BaseModel):
    results: List[DocumentSearchItem]
    


class UserSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, example="rahul")
    limit: int = Field(20, ge=1, le=50)
    offset: int = Field(0, ge=0)


class UserSearchItem(BaseModel):
    id: int
    name: Optional[str]
    college: Optional[str]
    course: Optional[str]
    profile_url: Optional[str]
    followers_count: int = 0
    following_count: int = 0
    is_following: bool = False

    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    results: List[UserSearchItem]