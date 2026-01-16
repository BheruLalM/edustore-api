from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.deps import get_db
from dependencies.get_current_user import get_current_user
from models.user import User
from services.follow.unfollow import UnFollowService

router = APIRouter(prefix="/users", tags=["Follow"])


@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UnFollowService.unfollow_user(
        db=db,
        current_user=current_user,
        target_user_id=user_id,
    )
