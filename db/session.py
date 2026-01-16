from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import DatabaseSetting


engine = create_engine(
    DatabaseSetting.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine,autoflush=False)

