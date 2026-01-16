from sqlalchemy.orm import Session
from sqlalchemy import or_, func, case, exists, literal
from models.user import User
from models.student import Student
from models.follow import Follow
from services.storage.factory import StorageFactory

class UserSearchService:

    @staticmethod
    def search_users(
        *,
        db: Session,
        query: str,
        current_user: User | None,
        limit: int = 20,
        offset: int = 0,
    ):
        
        if not query or len(query.strip()) < 2:
            return []

        limit = min(limit, 50)

        # ------------------------------------------------------------------
        # OPTIMIZED SUBQUERIES
        # ------------------------------------------------------------------
        
        # 1. Followers Count
        followers_sq = (
            db.query(func.count(Follow.id))
            .filter(Follow.following_id == User.id)
            .correlate(User)
            .scalar_subquery()
            .label("followers_count")
        )

        # 2. Following Count
        following_sq = (
            db.query(func.count(Follow.id))
            .filter(Follow.follower_id == User.id)
            .correlate(User)
            .scalar_subquery()
            .label("following_count")
        )

        # 3. Is Following (Current User -> Target User)
        if current_user:
            is_following_sq = (
                db.query(Follow.id)
                .filter(
                    Follow.follower_id == current_user.id,
                    Follow.following_id == User.id
                )
                .correlate(User)
                .exists()
            )
            is_following_col = case((is_following_sq, True), else_=False).label("is_following")
        else:
            is_following_col = literal(False).label("is_following")


        # ------------------------------------------------------------------
        # MAIN QUERY
        # ------------------------------------------------------------------
        
        base_query = (
            db.query(User, Student, followers_sq, following_sq, is_following_col)
            .join(Student, Student.user_id == User.id)
            .filter(
                User.is_active.is_(True),
                or_(
                    Student.name.ilike(f"%{query}%"),
                    Student.college.ilike(f"%{query}%"),
                    Student.course.ilike(f"%{query}%"),
                ),
            )
        )

        # Exclude self if logged in
        if current_user:
            base_query = base_query.filter(User.id != current_user.id)

        results = (
            base_query
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        storage = StorageFactory.get_storage()
        response_model = []

        for user, student, followers_count, following_count, is_following in results:
            
            # Generate profile URL
            profile_url = None
            if student.profile_url:
                try:
                    profile_url = storage.generate_download_url(
                        object_key=student.profile_url,
                        expires_in=31536000,
                    )
                except Exception:
                    pass

            response_model.append({
                "id": user.id,
                "name": student.name,
                "college": student.college,
                "course": student.course,
                "profile_url": profile_url,
                # Use subquery results
                "followers_count": followers_count or 0,
                "following_count": following_count or 0,
                "is_following": bool(is_following),
            })

        return response_model
