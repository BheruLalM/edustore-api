from sqlalchemy.orm import Session

from models.follow import Follow
from models.user import User
from core.exceptions import CannotFollowYourself, UserNotFound, NotFollowing
from services.cache.redis_service import cache


class UnFollowService:
    @staticmethod
    def unfollow_user(
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

        follow = (
            db.query(Follow)
            .filter(
                Follow.follower_id == current_user.id,
                Follow.following_id == target_user_id,
            )
            .first()
        )

        if not follow:
            return {
                "unfollowed": False,
                "already_unfollowed": True,
                "followers_count": db.query(Follow).filter(Follow.following_id == target_user_id).count(),
            }

        db.delete(follow)
        db.commit()

        # Invalidate cache
        cache.delete(f"user_profile_static:{target_user_id}")
        cache.delete(f"user_profile_static:{current_user.id}")

        return {
            "unfollowed": True,
            "already_unfollowed": False,
            "followers_count": db.query(Follow).filter(Follow.following_id == target_user_id).count(),
        }
