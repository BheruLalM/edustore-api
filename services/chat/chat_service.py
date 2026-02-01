"""
Chat microservice integration service.
Handles communication with the Node.js chat server and student verification.
"""
import httpx
from sqlalchemy.orm import Session
from models.student import Student
from typing import Optional, Dict, Any
from core.config import service_setting


CHAT_SERVICE_URL = service_setting.CHAT_SERVICE_URL


async def is_student(db: Session, user_id: int) -> bool:
    """
    Check if a user has a student profile.
    
    Args:
        db: Database session
        user_id: User ID to check
        
    Returns:
        True if user is a student, False otherwise
    """
    student = db.query(Student).filter(Student.user_id == user_id).first()
    return student is not None


async def get_student_data(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get student data for chat sync.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with student data or None if not a student
    """
    from models.user import User
    
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    from services.storage.factory import StorageFactory
    
    profile_url_signed = ""
    if student.profile_url:
        if student.profile_url.startswith("http"):
             profile_url_signed = student.profile_url
        else:
            try:
                storage = StorageFactory.get_storage()
                profile_url_signed = storage.generate_download_url(
                    object_key=student.profile_url,
                    expires_in=31536000,
                )
            except Exception:
                profile_url_signed = ""

    return {
        "postgresId": str(user_id),
        "email": user.email,
        "fullName": student.name or user.email.split("@")[0],
        "profilePic": profile_url_signed,
        "bio": f"{student.course or ''} - {student.college or ''}".strip(" -") or ""
    }


async def sync_user_to_chat(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync a student to the chat microservice.
    
    Args:
        student_data: Student data dictionary
        
    Returns:
        Response from chat service with token and user data
        
    Raises:
        httpx.HTTPError: If sync fails
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{CHAT_SERVICE_URL}/api/auth/sync",
            json=student_data
        )
        response.raise_for_status()
        return response.json()


async def get_chat_users(chat_token: str) -> Dict[str, Any]:
    """
    Get list of users from chat microservice.
    
    Args:
        chat_token: JWT token for chat authentication
        
    Returns:
        Response with users list
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{CHAT_SERVICE_URL}/api/messages/users",
            headers={"Authorization": f"Bearer {chat_token}"}
        )
        response.raise_for_status()
        return response.json()
