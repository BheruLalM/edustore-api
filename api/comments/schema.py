from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentUser(BaseModel):
    id: int
    username: Optional[str] = None


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    content: Optional[str] = None
    is_deleted: bool = False
    user: CommentUser
    created_at: datetime
    replies: List["CommentResponse"] = Field(default_factory=list)

    class Config:
        orm_mode = True


CommentResponse.update_forward_refs()
