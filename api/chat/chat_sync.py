"""
Chat sync endpoint - syncs authenticated students to the chat microservice.
Only students with a profile can access the chat feature.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.get_current_user import get_current_user
from db.deps import get_db
from models.user import User
from services.chat.chat_service import is_student, get_student_data, sync_user_to_chat
import httpx


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/sync")
async def sync_to_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync the current authenticated user to the chat microservice.
    
    Only students (users with a student profile) can access chat.
    Returns a JWT token for chat authentication.
    
    Returns:
        - success: Boolean
        - chatToken: JWT token for chat authentication
        - userData: User data from chat service
        - message: Success message
        
    Raises:
        - 403: If user is not a student
        - 500: If chat service is unavailable
    """
    # Check if user is a student
    if not await is_student(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access the chat feature"
        )
    
    # Get student data
    student_data = await get_student_data(db, current_user.id)
    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    # Sync to chat microservice
    try:
        chat_response = await sync_user_to_chat(student_data)
        
        return {
            "success": True,
            "chatToken": chat_response.get("token"),
            "userData": chat_response.get("userData"),
            "isStudent": True,
            "message": "Successfully synced to chat service"
        }
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Chat service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync to chat service: {str(e)}"
        )
