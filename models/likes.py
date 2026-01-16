from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from db.base import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "document_id",
            name="uq_user_document_like",
        ),
    )
