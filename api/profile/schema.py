from pydantic import BaseModel, EmailStr
from typing import Optional


class profile_update(BaseModel):
    name : Optional[str] = None
    college : Optional[str] = None
    semester : Optional[str] = None
    course : Optional[str] = None
    

class ProfileResponse(BaseModel):
    user_id: int
    email: EmailStr

    name: Optional[str] = None
    college: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None
    profile_url: Optional[str] = None
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0
    is_following: bool = False
    is_student: bool = False

    class Config:
        from_attributes = True
        

class AvatarUploadRequest(BaseModel):
    content_type: str


class AvatarCommitRequest(BaseModel):
    object_key: str

