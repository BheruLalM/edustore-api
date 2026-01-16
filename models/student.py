from sqlalchemy import Column, String, Integer, Boolean,DateTime,func,ForeignKey
from db.base import Base

class Student(Base):
    __tablename__= "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String, nullable=True)
    course = Column(String,nullable=True)
    college = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    profile_url = Column(String,nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now())
    