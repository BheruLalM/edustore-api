from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    content = Column(Text, nullable=True)  # Nullable for GDPR-friendly soft delete


    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="comments")
    document = relationship("Document", back_populates="comments")

    parent = relationship(
        "Comment",
        remote_side=[id],
        back_populates="replies",
    )

    replies = relationship(
        "Comment",
        back_populates="parent",
        order_by="Comment.created_at.asc()",
    )
