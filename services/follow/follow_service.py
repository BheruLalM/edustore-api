from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.follow import Follow
from models.user import User
from core.exceptions import CannotFollowYourself, UserNotFound
from services.cache.redis_service import cache


class FollowService:
    @staticmethod
    def follow_user(
        *,
        db: Session,
        current_user: User,
        target_user_id: int,
    ) -> dict:

        if current_user.id == target_user_id:
            raise CannotFollowYourself()

        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise UserNotFound()

        # Atomic follow: try to insert, if conflict then it's already following
        try:
            follow = Follow(
                follower_id=current_user.id,
                following_id=target_user_id,
            )
            db.add(follow)
            db.commit()

            # Invalidate cache
            cache.delete(f"user_profile_static:{target_user_id}")
            cache.delete(f"user_profile_static:{current_user.id}")
            return {
                "followed": True,
                "already_following": False,
            }
        except IntegrityError:
            # Already following (idempotent)
            db.rollback()
            return {
                "followed": False,
                "already_following": True,
            }
