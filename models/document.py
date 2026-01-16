from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    BigInteger,
    Enum,
    Text,   # 👈 ADD THIS
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(255), nullable=False)

    # pdf | image | notes | post
    doc_type = Column(String(50), nullable=False)

    # 🔥 file ke liye, post ke liye NULL
    object_key = Column(
        String(500),
        nullable=True,
        unique=True,
        index=True,
    )

    original_filename = Column(String(255))
    content_type = Column(String(100))
    file_size = Column(BigInteger)

    # 🔥 UNIVERSAL TEXT (caption / post body)
    content = Column(Text, nullable=True)

    visibility = Column(
        Enum("private", "public", name="document_visibility"),
        nullable=False,
        server_default="private",
        index=True,
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    user = relationship("User", back_populates="documents")

    comments = relationship(
        "Comment",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    likes = relationship("Like", cascade="all, delete")
    bookmarks = relationship("Bookmark", cascade="all, delete")
