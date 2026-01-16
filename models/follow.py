# models/follow.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)

    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    following_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )

    # Relationships with overlaps
    follower = relationship(
        "User",
        foreign_keys=[follower_id],
        overlaps="following"
    )

    following = relationship(
        "User",
        foreign_keys=[following_id],
        overlaps="follower"
    )
