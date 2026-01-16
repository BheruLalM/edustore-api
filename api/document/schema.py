from pydantic import BaseModel
from typing import Optional,Literal

from enum import Enum

class DocumentVisibility(str, Enum):
    private = "private"
    public = "public"

class DocumentUploadRequest(BaseModel):
    content_type: str

    
class DocumentCommitRequest(BaseModel):
    title: str
    doc_type: str
    object_key: str
    original_filename: str | None
    content_type: str
    file_size: int | None
    visibility: str
    content: str | None 

    visibility: Literal["private", "public"] = "private"
    
from pydantic import BaseModel, Field
from typing import Optional


class CreateTextPostSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=1)
    visibility: str = Field(default="public", pattern="^(public|private)$")


class DocumentResponse(BaseModel):
    id: int
    user_id: int

    title: str
    doc_type: str

    object_key: str
    original_filename: Optional[str]
    content_type: Optional[str]
    file_size: Optional[int]
    content: Optional[str]

    visibility: DocumentVisibility
    is_deleted: bool

    class Config:
        from_attributes = True
        





