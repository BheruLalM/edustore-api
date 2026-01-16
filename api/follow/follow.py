from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.follow.follow_service import FollowService

router = APIRouter(prefix="/users", tags=["Follow"])


@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = FollowService.follow_user(
        db=db,
        current_user=current_user,
        target_user_id=user_id,
    )

    return {
        "message": "Follow successful",
        "following_id": user_id,
        **result,
    }
