# models/user.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Documents
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Follows
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",
        overlaps="follower"
    )

    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        cascade="all, delete-orphan",
        overlaps="following"
    )

    # Comments
    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Likes & Bookmarks
    likes = relationship("Like", cascade="all, delete")
    bookmarks = relationship("Bookmark", cascade="all, delete")
